---
name: adonisjs-ai-text-to-speech-elevenlabs-best-practices
description: Use when implementing, reviewing, or debugging text-to-speech (TTS) features, voice generation, or integrating ElevenLabs API in AdonisJS v6. Triggers on ElevenLabsService, synthesizeVoice, voiceover jobs, and TTS credentials configuration.
---

# Boas Práticas para AI Text-to-Speech (ElevenLabs) no AdonisJS

## Objetivo
Fornecer padrões unificados, padrões de arquitetura e restrições para integrar a API de Text-to-Speech (TTS) da ElevenLabs em aplicações AdonisJS v6. O objetivo é garantir a eficiência de custos por meio do cache de conteúdo, manipulação robusta de armazenamento via `@adonisjs/drive`, execução não bloqueante usando tarefas (jobs) do BullMQ e isolamento estrito a nível de tenant para modelos de voz personalizados.

## Instruções

### 1. Serviço Centralizado ElevenLabs (`app/services/elevenlabs_service.ts`)
* Sempre envolva o cliente da API ElevenLabs dentro de uma classe de serviço dedicada.
* Carregue as credenciais da API com segurança a partir de variáveis de ambiente (configuradas via `start/env.ts` e `config/services.ts`).
* Use o SDK oficial `@elevenlabs/client` ou manipule consultas da API REST com o cliente `fetch` nativo usando `AbortSignal` para timeouts.
* **Exemplo de Esqueleto do Serviço:**
  ```typescript
  import env from '#start/env'
  import drive from '@adonisjs/drive/services/main'
  import crypto from 'node:crypto'
  import logger from '@adonisjs/core/services/logger'

  export default class ElevenLabsService {
    private readonly apiKey: string
    private readonly baseUrl = 'https://api.elevenlabs.io/v1'

    constructor() {
      this.apiKey = env.get('ELEVENLABS_API_KEY')
    }

    /**
     * Sintetiza texto em fala e retorna a chave do caminho de armazenamento.
     */
    async synthesize(text: string, voiceId: string, tenantId: string): Promise<string> {
      const sanitizedText = text.trim()
      const textHash = crypto.createHash('sha256').update(`${voiceId}:${sanitizedText}`).digest('hex')
      const storageKey = `tts/${tenantId}/${textHash}.mp3`

      // 1. Verificação de Cache de Text-to-Speech (Otimização de Custos)
      const exists = await drive.use().exists(storageKey)
      if (exists) {
        logger.info({ storageKey }, 'ElevenLabsService: Retornando arquivo de áudio em cache')
        return storageKey
      }

      // 2. Realizar chamada de API externa
      logger.info({ voiceId, tenantId }, 'ElevenLabsService: Enviando requisição para API ElevenLabs')
      const response = await fetch(`${this.baseUrl}/text-to-speech/${voiceId}`, {
        method: 'POST',
        headers: {
          'xi-api-key': this.apiKey,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: sanitizedText,
          model_id: 'eleven_multilingual_v2',
          voice_settings: {
            stability: 0.5,
            similarity_boost: 0.75,
          },
        }),
        signal: AbortSignal.timeout(30000), // Timeout de 30 segundos
      })

      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Erro na API ElevenLabs: ${response.status} - ${errorText}`)
      }

      const audioBuffer = Buffer.from(await response.arrayBuffer())

      // 3. Salvar arquivo de áudio usando @adonisjs/drive
      await drive.use().put(storageKey, audioBuffer, {
        contentType: 'audio/mpeg',
      })

      // 4. Registrar uso e custos (ex: 1 caractere = 1 cota de caractere / estimativa de custo)
      await this.logQuotaUsage(sanitizedText.length, tenantId)

      return storageKey
    }

    private async logQuotaUsage(characterCount: number, tenantId: string) {
      // Lógica para registrar caracteres usados em uma tabela do banco de dados (ex: modelo AgentAiCost)
      // estimativa de custo: ex: $0.00015 por caractere para a faixa de preço padrão
    }
  }
  ```

### 2. Processamento em Background com BullMQ (`app/jobs/voiceover_job.ts`)
* A síntese de fala (Text-to-Speech) é uma requisição externa intensiva em E/S (I/O) e deve ser executada fora do ciclo de requisição-resposta HTTP.
* Enfileire as requisições de síntese usando um Job dedicado do BullMQ.
* **Exemplo de Implementação de Job:**
  ```typescript
  import type { Job } from 'bullmq'
  import ElevenLabsService from '#services/elevenlabs_service'
  import { voiceoverQueue } from '#services/queue_service'
  import CalendarEvent from '#models/calendar/event'

  export interface VoiceoverJobData {
    eventId: string
    text: string
    voiceId: string
    tenantId: string
  }

  export default class VoiceoverJob {
    static readonly queueName = 'voiceover'

    static async dispatch(data: VoiceoverJobData) {
      await voiceoverQueue.add('generate-voice', data, {
        attempts: 3,
        backoff: {
          type: 'exponential',
          delay: 5000,
        },
        removeOnComplete: { count: 50 },
        removeOnFail: { count: 100 },
      })
    }

    static async handle(job: Job<VoiceoverJobData>) {
      const { eventId, text, voiceId, tenantId } = job.data
      const elevenlabs = new ElevenLabsService()

      try {
        const audioPath = await elevenlabs.synthesize(text, voiceId, tenantId)
        
        // Associar o áudio resultante ao CalendarEvent ou recurso de vídeo
        const event = await CalendarEvent.findOrFail(eventId)
        await event.merge({
          audioPath,
          status: 'ready_for_render',
        }).save()
      } catch (error) {
        // O tratamento de erros deve atualizar o status do recurso
        const event = await CalendarEvent.find(eventId)
        if (event) {
          await event.merge({
            publishError: `Falha na síntese de voz: ${error.message}`,
            status: 'failed',
          }).save()
        }
        throw error
      }
    }
  }
  ```

### 3. Integração de Análise de Custos (`app/models/agent_ai_cost.ts`)
* Ao registrar o uso de TTS, certifique-se de que os detalhes sejam gravados no banco de dados para rastrear custos por agência/tenant.
* Use o modelo `agent_ai_cost` ou similar, salvando:
  * `characterCount` (Tamanho do texto).
  * `provider` (Sempre definido como 'elevenlabs').
  * `model` (ex: 'eleven_multilingual_v2').
  * `cost` (Estimativa baseada no modelo de preço por caractere da ElevenLabs).
  * `tenantId` (ID da organização ou empresa que utiliza o recurso).

## Restrições
* **Nunca** execute chamadas de text-to-speech de forma síncrona dentro de uma ação de Controller HTTP. Sempre despache as tarefas de síntese para o BullMQ.
* **Nunca** chame a API da ElevenLabs sem antes verificar se o hash do texto já existe no armazenamento do `@adonisjs/drive`. Essa verificação de cache é obrigatória para evitar cobranças duplicadas.
* **Nunca** defina IDs de voz de forma estática (hardcoded). Os IDs de voz devem ser recuperados dinamicamente dos modelos de configuração de tenant/empresa (ex: `SocialMediaCredential` or `SolarCompany`).
* **Nunca** permita que entradas não validadas (ex: roteiros extremamente longos) sejam enviadas diretamente para a ElevenLabs. Garanta que os validadores do VineJS apliquem limites estritos de caracteres (ex: no máximo 5000 caracteres por roteiro) antes de disparar o job.
* **Nunca** armazene chaves de API da ElevenLabs dentro do controle de versão. Sempre leia-as através de `env.get('ELEVENLABS_API_KEY')` e configure-as em `start/env.ts`.
