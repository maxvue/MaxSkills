---
name: adonisjs-audio-transcription-analysis-best-practices
description: Use when implementing, reviewing, or debugging audio transcription and voice analysis features in AdonisJS v6, routing AI calls (Google Gemini speech-to-text) through the Vercel AI SDK. Triggers on files handling audio upload processing for speech-to-text, integrating Gemini via the AI SDK for audio parsing, extracting voice metadata, or generating transcription transcripts for database storage.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Fornecer padrões estruturados, altamente confiáveis e seguros para receber, validar, transcrever e realizar análises cognitivas em arquivos de áudio e notas de voz no AdonisJS v6.

## Instruções

## 1. Validação de Requisições e Manipulação de Upload de Arquivos
Ao receber uploads de áudio via requisições HTTP:
- Sempre utilize os recursos do Bodyparser do AdonisJS v6 para limitar o tamanho do arquivo e as extensões permitidas.
- Os formatos permitidos para serviços de transcrição de IA normalmente incluem: `mp3`, `wav`, `ogg`, `m4a`, `webm` e `opus`.
- Valide o upload usando as regras do validador VineJS em um validador dedicado ou em uma ação do controller.

Exemplo de regra do VineJS para upload de áudio:
```typescript
import vine from '@vinejs/vine'

export const uploadAudioValidator = vine.compile(
  vine.object({
    audio: vine.file({
      size: '25mb',
      extnames: ['mp3', 'wav', 'ogg', 'm4a', 'webm', 'opus']
    })
  })
)
```

## 2. Padrões de Integração de API (Vercel AI SDK)
Toda integração de IA (transcrição e análise) DEVE passar pelo **Vercel AI SDK** (`ai`), nunca pelos SDKs diretos `@google/genai`. O provider `@ai-sdk/openai` (Whisper) NÃO faz parte do stack-alvo — apenas `@ai-sdk/google` e `@ai-sdk/anthropic` estão disponíveis.
- **Transcrição (Gemini)**: Use `generateText()` do `ai` com o provider Google (`@ai-sdk/google`), usando um modelo Gemini com suporte a áudio (ex.: `gemini-2.5-flash`) e passando o áudio como content part do tipo `file` (`Buffer`/`Uint8Array` lido do disco).
- **Análise/Resumo (Gemini)**: Use `generateText()`/`generateObject()` do `ai` com o provider Google (`@ai-sdk/google`). Para arquivos maiores que 20MB, prefira referenciar o arquivo via File API do provider em vez de enviar dados inline brutos.
- **Variáveis de ambiente**: Carregue as credenciais usando a configuração de ambiente do AdonisJS: `env.get('GOOGLE_GENERATIVE_AI_API_KEY')`. Nunca insira chaves diretamente no código (hardcoded).
- **Timeout e Tentativas (Retries)**: O Vercel AI SDK aceita `maxRetries` nas chamadas; configure-o para lidar com instabilidades de rede e rate limiting (HTTP 429).

## 3. Execução Assíncrona e Integração com Filas
A transcrição é um processo pesado e pode bloquear o ciclo principal de requisição-resposta HTTP.
- Para notas de voz curtas (por exemplo, menos de 10 segundos), a transcrição inline/síncrona é aceitável se o cliente esperar uma resposta em tempo real.
- Para gravações de áudio mais longas ou análises em várias etapas (transcrição + resumo + análise de sentimentos), delegue a tarefa para um job em segundo plano usando o **BullMQ** ou o sistema de filas do AdonisJS.
- Faça o upload dos arquivos para uma pasta de armazenamento temporária ou persistente (via AdonisJS Drive) antes de despachar o job da fila, e passe o caminho do arquivo no payload do job.

## 4. Persistência de Dados no PostgreSQL usando JSONB
Armazene o resultado da transcrição juntamente com metadados ricos em colunas JSONB do PostgreSQL usando o Lucid ORM.
- **Esquema de Transcrições**: Sempre salve marcadores estruturais como timestamps, identificação de locutores (speaker diarization, se disponível), níveis de confiança e a segmentação do texto bruto.
- **Configuração do Model Lucid**:
  ```typescript
  import { BaseModel, column } from '@adonisjs/lucid/orm'

  export interface TranscriptionMetadata {
    duration: number
    language: string
    confidence: number
    segments: Array<{ start: number; end: number; text: string }>
  }

  export default class VoiceNote extends BaseModel {
    @column({ isPrimary: true })
    declare id: number

    @column()
    declare filePath: string

    @column()
    declare transcript: string

    @column({
      prepare: (value: TranscriptionMetadata) => JSON.stringify(value),
      consume: (value: string | object) => typeof value === 'string' ? JSON.parse(value) : value
    })
    declare metadata: TranscriptionMetadata
  }
  ```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** execute tarefas de transcrição de forma síncrona para áudios com mais de 15 segundos; sempre use um job/worker em segundo plano (por exemplo, BullMQ).
- **NÃO** armazene arquivos de áudio grandes diretamente no banco de dados (por exemplo, usando `bytea` ou `blob`). Armazene os arquivos em um sistema de armazenamento local ou em nuvem (AdonisJS Drive) e referencie o caminho deles.
- **NÃO** ignore a validação do tipo MIME e do tamanho do arquivo enviado no lado do servidor.
- **NÃO** exponha detalhes de erro de APIs de terceiros contendo chaves secretas ou parâmetros de configuração em manipuladores de exceção públicos. Limpe as mensagens de erro antes de enviá-las ao cliente.

# Exemplos

### Exemplo: Serviço de Transcrição (Vercel AI SDK)
```typescript
import fs from 'node:fs'
import { inject } from '@adonisjs/core'
import { generateText } from 'ai'
import { google } from '@ai-sdk/google'

@inject()
export default class AudioTranscriptionService {
  /**
   * Transcreve áudio usando Gemini via Vercel AI SDK
   * (lê GOOGLE_GENERATIVE_AI_API_KEY do ambiente automaticamente)
   */
  async transcribeWithGemini(filePath: string): Promise<string> {
    const audio = await fs.promises.readFile(filePath)
    const mimeType = this.detectMimeType(filePath)

    const { text } = await generateText({
      model: google('gemini-2.5-flash'),
      maxRetries: 3,
      messages: [
        {
          role: 'user',
          content: [
            { type: 'text', text: 'Transcreva o áudio a seguir na íntegra, apenas o texto falado.' },
            { type: 'file', data: audio, mediaType: mimeType },
          ],
        },
      ],
    })

    return text
  }

  /**
   * Processa o áudio e gera uma análise estruturada usando o Gemini
   * via Vercel AI SDK (lê GOOGLE_GENERATIVE_AI_API_KEY do ambiente)
   */
  async analyzeAudioWithGemini(filePath: string, prompt: string): Promise<string> {
    const fileBuffer = await fs.promises.readFile(filePath)
    const mimeType = this.detectMimeType(filePath)

    const { text } = await generateText({
      model: google('gemini-2.5-flash'),
      maxRetries: 3,
      messages: [
        {
          role: 'user',
          content: [
            { type: 'text', text: prompt },
            { type: 'file', data: fileBuffer, mediaType: mimeType },
          ],
        },
      ],
    })

    return text
  }

  private detectMimeType(filePath: string): string {
    if (filePath.endsWith('.mp3')) return 'audio/mp3'
    if (filePath.endsWith('.wav')) return 'audio/wav'
    if (filePath.endsWith('.ogg')) return 'audio/ogg'
    if (filePath.endsWith('.opus')) return 'audio/opus'
    return 'audio/mpeg'
  }
}
```

### Exemplo: Controller Manipulando Upload de Áudio e Despachando para Fila
```typescript
import { HttpContext } from '@adonisjs/core/http'
import { inject } from '@adonisjs/core'
import { cuid } from '@adonisjs/core/helpers'
import { uploadAudioValidator } from '#validators/audio'
import VoiceNote from '#models/voice_note'
import Queue from '#services/queue_service'

@inject()
export default class VoiceNotesController {
  async store({ request, response }: HttpContext) {
    const { audio } = await request.validateUsing(uploadAudioValidator)

    // Calcule a chave de destino (o 1º argumento de moveToDisk É a key completa no storage).
    const key = `voice-notes/${cuid()}.${audio.extname}`
    await audio.moveToDisk(key)

    // Salva o registro inicial no banco de dados com status pendente
    const voiceNote = await VoiceNote.create({
      filePath: key,
      transcript: '',
      metadata: {
        duration: 0,
        language: 'unknown',
        confidence: 0,
        segments: []
      }
    })

    // Despacha o job em segundo plano para transcrição para evitar bloquear a resposta
    await Queue.add('transcribe-audio', { voiceNoteId: voiceNote.id })

    return response.accepted({
      message: 'Áudio recebido e enfileirado para processamento',
      id: voiceNote.id
    })
  }
}
```
