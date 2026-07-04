---
name: adonisjs-gemini-file-api-media-integration-best-practices
description: Use when implementing, reviewing, or debugging media uploads and processing using the Google AI File API with Gemini in AdonisJS. Triggers on files managing multimodal AI requests, processing large video, audio, or PDF files for Gemini analysis, uploading temp files to the Google File API, monitoring upload state, and cleanup operations.
---

## Goal
Provide secure, robust, and resource-efficient guidelines for uploading and processing large multimedia files (videos, audios, and heavy PDFs) to the Google AI File API and passing them to Gemini models within an AdonisJS v6 application. The target backend uses the **Vercel AI SDK** (`ai@7.0.2`) with the Google provider **`@ai-sdk/google@4.0.0`** — the standalone `@google/genai` / `@google/generative-ai` packages are **not** installed and must not be used.

## Instructions

### 1. Client Initialization (Vercel AI SDK + Google provider)
Always read the API key from the AdonisJS Env service. Create the provider with `createGoogleGenerativeAI` and obtain a model via the `google(...)` factory; run generations with `generateText` / `generateObject` from `ai`.
```typescript
import { createGoogleGenerativeAI } from '@ai-sdk/google'
import { generateText } from 'ai'
import env from '#start/env'

const google = createGoogleGenerativeAI({ apiKey: env.get('GEMINI_API_KEY') })
const model = google('gemini-2.5-flash')
```
> The `@ai-sdk/google` provider does **not** wrap the Google File API upload/polling/delete endpoints in a way you can rely on across versions. Handle the file lifecycle with raw REST calls (below) and then reference the resulting file URI in your `generateText`/`generateObject` prompt via a `fileData` part — the file-input shape the provider accepts.

### 2. Bridge with AdonisJS Drive
The Google File API upload needs the file bytes. AdonisJS may store uploaded files on a local disk (`fs`) or cloud storage (`s3` / `gcs`), so read the file through the Drive **stream** API, which is disk-agnostic. Do **not** call `drive.use().makePath(...)` — the flydrive `Disk` class has no `makePath` method and it will throw `TypeError: ...makePath is not a function`.
```typescript
import drive from '@adonisjs/drive/services/main'
import app from '@adonisjs/core/services/app'
import { cuid } from '@adonisjs/core/helpers'
import fs from 'node:fs'
import path from 'node:path'
import { pipeline } from 'node:stream/promises'

/**
 * Streams a drive file (any disk: fs, s3, gcs) to a local temporary path.
 * Returns the local path — always temporary, so the caller always cleans up.
 */
export async function getLocalPath(fileKey: string): Promise<{ localPath: string; isTemp: boolean }> {
  const tempPath = path.join(app.tmpPath(), `gemini-file-${cuid()}`)
  const fileStream = await drive.use().getStream(fileKey)
  await pipeline(fileStream, fs.createWriteStream(tempPath))

  return { localPath: tempPath, isTemp: true }
}
```
> If you must avoid the temp copy for the local `fs` disk, resolve the path from the driver's configured `location` root manually (`path.join(config.location, fileKey)`) — but there is no public `Disk` API for that, so streaming to a temp path is the portable default.

### 3. Uploading to the Google File API (raw REST)
Upload the resolved bytes to the File API. Provide an accurate `mimeType` and a semantic `displayName`. The File API returns a `file` object containing `name` (e.g. `files/abc123`), `uri`, `mimeType`, and `state`.
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

### 4. Active Status Polling (Media Processing)
Large media (videos, large audios) is processed asynchronously. Poll the File API until the file's `state` changes from `PROCESSING` to `ACTIVE` before referencing it in a generation:
```typescript
let current = file
while (current.state === 'PROCESSING') {
  await new Promise((resolve) => setTimeout(resolve, 10000)) // 10s wait
  const res = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/${current.name}?key=${apiKey}`
  )
  current = await res.json()
}
if (current.state !== 'ACTIVE') {
  throw new Error(`File processing failed with state: ${current.state}`)
}
```

### 5. Invoking Gemini with File References
Reference the active file in the prompt via a `fileData` part (using its `uri` and `mimeType`), alongside your text instruction:
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
> The AI SDK maps a file part with a URL/URI `data` to the Google `fileData: { fileUri, mimeType }` request shape. Use `generateObject` instead when you need a typed/structured result.

### 6. Resource Cleanup and Lifecycle Hooks
Google File API files persist for up to 48 hours unless deleted. Always trigger cleanup in a `finally` block to remove both the Google file and any local temporary file:
```typescript
try {
  // Upload, poll, and generate...
} finally {
  // 1. Delete the Google File API reference (raw REST DELETE)
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

  // 2. Delete the local temp file
  if (isTemp && localPath) {
    fs.promises.unlink(localPath).catch((error) => {
      logger.warn({ err: error }, 'Failed to delete local temporary file')
    })
  }
}
```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Never** use `@google/genai` or `@google/generative-ai` — they are not installed. Use `@ai-sdk/google` (`createGoogleGenerativeAI` / `google(...)`) with `generateText`/`generateObject` from `ai`.
- **Never** call `drive.use().makePath(...)` — it does not exist on the flydrive `Disk`. Stream files with `drive.use().getStream(key)`.
- **Never** perform Base64 conversions for large video/audio payloads in memory. Doing so leads to RAM exhaustion. Always route them through the File API.
- **Never** proceed to generate content using a file without verifying that its state has transitioned to `ACTIVE`.
- **Never** leak local temporary files or Google File API references. Always clean up resources inside `finally` blocks.
- **Do not** expose raw API keys or hardcode configuration. Access all parameters through the AdonisJS `env` service.
