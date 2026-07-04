---
name: adonisjs-gemini-file-api-media-integration-best-practices
description: Use when implementing, reviewing, or debugging media uploads and processing using the Google AI File API with Gemini in AdonisJS. Triggers on files managing multimodal AI requests, processing large video, audio, or PDF files for Gemini analysis, uploading temp files to the Google File API, monitoring upload state, and cleanup operations.
---

## Objetivo
Fornecer diretrizes seguras, robustas e eficientes em recursos para fazer upload e processar grandes arquivos multimídia (vídeos, áudios e PDFs pesados) para a Google AI File API e passá-los para os modelos Gemini dentro de uma aplicação AdonisJS v6. O backend-alvo usa o **Vercel AI SDK** (`ai@7.0.2`) com o provider Google **`@ai-sdk/google@4.0.0`** — os pacotes standalone `@google/genai` / `@google/generative-ai` **não** estão instalados e não devem ser usados.

## Instruções

### 1. Inicialização do Cliente (Vercel AI SDK + provider Google)
Sempre leia a chave de API a partir do serviço Env do AdonisJS. Crie o provider com `createGoogleGenerativeAI` e obtenha um modelo através da factory `google(...)`; execute as gerações com `generateText` / `generateObject` de `ai`.
```typescript
import { createGoogleGenerativeAI } from '@ai-sdk/google'
import { generateText } from 'ai'
import env from '#start/env'

const google = createGoogleGenerativeAI({ apiKey: env.get('GEMINI_API_KEY') })
const model = google('gemini-2.5-flash')
```
> O provider `@ai-sdk/google` **não** encapsula os endpoints de upload/polling/delete da Google File API de uma forma na qual você possa confiar entre versões. Gerencie o ciclo de vida do arquivo com chamadas REST cruas (abaixo) e então referencie o file URI resultante no seu prompt de `generateText`/`generateObject` através de uma parte `fileData` — o formato de entrada de arquivo que o provider aceita.

### 2. Ponte com o AdonisJS Drive
O upload para a Google File API precisa dos bytes do arquivo. O AdonisJS pode armazenar arquivos enviados em um disco local (`fs`) ou em armazenamento em nuvem (`s3` / `gcs`), então leia o arquivo através da API de **stream** do Drive, que é agnóstica de disco. **Não** chame `drive.use().makePath(...)` — a classe `Disk` do flydrive não possui o método `makePath` e ele lançará `TypeError: ...makePath is not a function`.
```typescript
import drive from '@adonisjs/drive/services/main'
import app from '@adonisjs/core/services/app'
import { cuid } from '@adonisjs/core/helpers'
import fs from 'node:fs'
import path from 'node:path'
import { pipeline } from 'node:stream/promises'

/**
 * Faz stream de um arquivo do drive (qualquer disco: fs, s3, gcs) para um caminho temporário local.
 * Retorna o caminho local — sempre temporário, então o chamador sempre faz a limpeza.
 */
export async function getLocalPath(fileKey: string): Promise<{ localPath: string; isTemp: boolean }> {
  const tempPath = path.join(app.tmpPath(), `gemini-file-${cuid()}`)
  const fileStream = await drive.use().getStream(fileKey)
  await pipeline(fileStream, fs.createWriteStream(tempPath))

  return { localPath: tempPath, isTemp: true }
}
```
> Se você precisa evitar a cópia temporária para o disco local `fs`, resolva o caminho a partir da raiz `location` configurada do driver manualmente (`path.join(config.location, fileKey)`) — mas não há API pública de `Disk` para isso, então fazer stream para um caminho temporário é o padrão portável.

### 3. Upload para a Google File API (REST cru)
Faça o upload dos bytes resolvidos para a File API. Forneça um `mimeType` preciso e um `displayName` semântico. A File API retorna um objeto `file` contendo `name` (ex: `files/abc123`), `uri`, `mimeType` e `state`.
```typescript
const apiKey = env.get('GEMINI_API_KEY')
const bytes = await fs.promises.readFile(localPath)

const uploadRes = await fetch(
  `https://generativelanguage.googleapis.com/upload/v1beta/files?key=${apiKey}`,
  {
    method: 'POST',
    headers: {
      'X-Goog-Upload-Protocol': 'raw',
      'X-Goog-Upload-File-Name': displayName,
      'Content-Type': mimeType,
    },
    body: bytes,
  }
)
if (!uploadRes.ok) throw new Error(`File API upload failed: ${uploadRes.status}`)
const { file } = await uploadRes.json() // file: { name, uri, mimeType, state, ... }
```

### 4. Polling de Status Ativo (Processamento de Mídia)
Mídias grandes (vídeos, áudios grandes) são processadas de forma assíncrona. Faça polling na File API até que o `state` do arquivo mude de `PROCESSING` para `ACTIVE` antes de referenciá-lo em uma geração:
```typescript
let current = file
while (current.state === 'PROCESSING') {
  await new Promise((resolve) => setTimeout(resolve, 10000)) // espera de 10s
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/${current.name}?key=${apiKey}`
  )
  current = await res.json()
}
if (current.state !== 'ACTIVE') {
  throw new Error(`File processing failed with state: ${current.state}`)
}
```

### 5. Invocando o Gemini com Referências de Arquivo
Referencie o arquivo ativo no prompt através de uma parte `fileData` (usando seu `uri` e `mimeType`), junto com sua instrução de texto:
```typescript
import { generateText } from 'ai'

const response = await generateText({
  model: google('gemini-2.5-flash'),
  messages: [
    {
      role: 'user',
      content: [
        { type: 'text', text: 'Analyze this media file' },
        { type: 'file', data: current.uri, mediaType: current.mimeType },
      ],
    },
  ],
})
```
> O AI SDK mapeia uma parte de arquivo com um `data` do tipo URL/URI para o formato de requisição `fileData: { fileUri, mimeType }` do Google. Use `generateObject` em vez disso quando precisar de um resultado tipado/estruturado.

### 6. Limpeza de Recursos e Hooks de Ciclo de Vida
Os arquivos da Google File API persistem por até 48 horas, a menos que sejam deletados. Sempre dispare a limpeza em um bloco `finally` para remover tanto o arquivo do Google quanto qualquer arquivo temporário local:
```typescript
try {
  // Upload, poll e generate...
} finally {
  // 1. Deleta a referência da Google File API (REST DELETE cru)
  try {
    if (file?.name) {
      await fetch(
        `https://generativelanguage.googleapis.com/v1beta/${file.name}?key=${apiKey}`,
        { method: 'DELETE' }
      )
    }
  } catch (error) {
    logger.warn({ err: error }, 'Failed to delete file from Google File API')
  }

  // 2. Deleta o arquivo temporário local
  if (isTemp && localPath) {
    fs.promises.unlink(localPath).catch((error) => {
      logger.warn({ err: error }, 'Failed to delete local temporary file')
    })
  }
}
```

## Restrições
- **Idioma:** Sempre comunique-se com o usuário humano em português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill esteja escrito.
- **Nunca** use `@google/genai` ou `@google/generative-ai` — eles não estão instalados. Use `@ai-sdk/google` (`createGoogleGenerativeAI` / `google(...)`) com `generateText`/`generateObject` de `ai`.
- **Nunca** chame `drive.use().makePath(...)` — ele não existe no `Disk` do flydrive. Faça stream de arquivos com `drive.use().getStream(key)`.
- **Nunca** faça conversões Base64 para payloads grandes de vídeo/áudio em memória. Fazer isso leva ao esgotamento da RAM. Sempre roteie-os através da File API.
- **Nunca** prossiga para gerar conteúdo usando um arquivo sem verificar que seu estado transicionou para `ACTIVE`.
- **Nunca** deixe vazar arquivos temporários locais ou referências da Google File API. Sempre limpe os recursos dentro de blocos `finally`.
- **Não** exponha chaves de API cruas nem faça hardcode de configuração. Acesse todos os parâmetros através do serviço `env` do AdonisJS.
