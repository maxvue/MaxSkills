---
name: adonisjs-audio-transcription-analysis-best-practices
description: Use when implementing, reviewing, or debugging audio transcription and voice analysis features in AdonisJS v6, using services like OpenAI Whisper, Google Gemini API (speech-to-text), or local tools. Triggers on files handling audio upload processing for speech-to-text, integrating with Whisper/Gemini APIs for audio parsing, extracting voice metadata, or generating transcription transcripts for database storage.
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

## 2. Padrões de Integração de API (Whisper e Gemini)
Integre-se com APIs de transcrição de forma segura e eficiente:
- **API OpenAI Whisper**: Use o pacote oficial `openai`. Envie o arquivo usando `fs.createReadStream(file.tmpPath)`.
- **API Google Gemini**: Use o SDK oficial `@google/genai` ou os endpoints REST. Para arquivos maiores que 20MB, utilize o helper File API do Gemini em vez de enviar dados inline brutos.
- **Variáveis de ambiente**: Carregue as credenciais usando a configuração de ambiente do AdonisJS: `env.get('OPENAI_API_KEY')` ou `env.get('GEMINI_API_KEY')`. Nunca insira chaves diretamente no código (hardcoded).
- **Timeout e Tentativas (Retries)**: Implemente mecanismos de retry usando bibliotecas auxiliares ou loops de atraso simples para lidar com instabilidades de rede e rate limiting (HTTP 429).

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
- **NÃO** execute tarefas de transcrição de forma síncrona para áudios com mais de 15 segundos; sempre use um job/worker em segundo plano (por exemplo, BullMQ).
- **NÃO** armazene arquivos de áudio grandes diretamente no banco de dados (por exemplo, usando `bytea` ou `blob`). Armazene os arquivos em um sistema de armazenamento local ou em nuvem (AdonisJS Drive) e referencie o caminho deles.
- **NÃO** ignore a validação do tipo MIME e do tamanho do arquivo enviado no lado do servidor.
- **NÃO** exponha detalhes de erro de APIs de terceiros contendo chaves secretas ou parâmetros de configuração em manipuladores de exceção públicos. Limpe as mensagens de erro antes de enviá-las ao cliente.

# Exemplos

### Exemplo: Serviço de Transcrição (OpenAI e Gemini)
```typescript
import fs from 'node:fs'
import { inject } from '@adonisjs/core'
import env from '#start/env'
import OpenAI from 'openai'
import { GoogleGenAI } from '@google/genai'

@inject()
export default class AudioTranscriptionService {
  private openai?: OpenAI
  private ai?: GoogleGenAI

  constructor() {
    const openAiKey = env.get('OPENAI_API_KEY')
    if (openAiKey) {
      this.openai = new OpenAI({ apiKey: openAiKey })
    }

    const geminiKey = env.get('GEMINI_API_KEY')
    if (geminiKey) {
      this.ai = new GoogleGenAI({ apiKey: geminiKey })
    }
  }

  /**
   * Transcreve áudio usando OpenAI Whisper
   */
  async transcribeWithWhisper(filePath: string): Promise<string> {
    if (!this.openai) {
      throw new Error('A chave da OpenAI não está configurada')
    }

    const response = await this.openai.audio.transcriptions.create({
      file: fs.createReadStream(filePath),
      model: 'whisper-1',
    })

    return response.text
  }

  /**
   * Processa o áudio e gera uma análise estruturada usando o Gemini
   */
  async analyzeAudioWithGemini(filePath: string, prompt: string): Promise<string | null> {
    if (!this.ai) {
      throw new Error('A API do Gemini não está configurada')
    }

    const fileBuffer = await fs.promises.readFile(filePath)
    const mimeType = this.detectMimeType(filePath)

    const response = await this.ai.models.generateContent({
      model: 'gemini-2.5-flash',
      contents: [
        {
          inlineData: {
            data: fileBuffer.toString('base64'),
            mimeType
          }
        },
        prompt
      ]
    })

    return response.text
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
import { uploadAudioValidator } from '#validators/audio'
import VoiceNote from '#models/voice_note'
// import QueueService ou BullMQ helper

@inject()
export default class VoiceNotesController {
  async store({ request, response }: HttpContext) {
    const { audio } = await request.validateUsing(uploadAudioValidator)

    // Salva o áudio localmente ou no Drive
    await audio.moveToDisk('voice-notes')
    const fileName = audio.fileName!

    // Salva o registro inicial no banco de dados com status pendente
    const voiceNote = await VoiceNote.create({
      filePath: fileName,
      transcript: '',
      metadata: {
        duration: 0,
        language: 'unknown',
        confidence: 0,
        segments: []
      }
    })

    // Despacha o job em segundo plano para transcrição para evitar bloquear a resposta
    // await QueueService.dispatch('transcribe-audio', { voiceNoteId: voiceNote.id })

    return response.accepted({
      message: 'Áudio recebido e enfileirado para processamento',
      id: voiceNote.id
    })
  }
}
```
