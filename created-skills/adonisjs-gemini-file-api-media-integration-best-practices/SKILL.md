---
name: adonisjs-gemini-file-api-media-integration-best-practices
description: Use when implementing, reviewing, or debugging media uploads and processing using the Google AI File API with the Gemini SDK in AdonisJS. Triggers on files managing multimodal AI requests, processing large video, audio, or PDF files for Gemini analysis, uploading temp files to the Google File API, monitoring upload state, and cleanup operations.
---

## Goal
Provide secure, robust, and resource-efficient guidelines for uploading and processing large multimedia files (videos, audios, and heavy PDFs) to the Google AI File API and passing them to Gemini models within an AdonisJS v6 application.

## Instructions

### 1. SDK Selection and Client Initialization
Always read the API keys from the AdonisJS Env service. Use either the modern `@google/genai` (recommended) or `@google/generative-ai` SDK.
- **Using `@google/genai` (New Standard)**:
  ```typescript
  import { GoogleGenAI } from '@google/genai'
  import env from '#start/env'

  const ai = new GoogleGenAI({ apiKey: env.get('GEMINI_API_KEY') })
  ```
- **Using `@google/generative-ai` (Legacy/Common)**:
  ```typescript
  import { GoogleGenerativeAI } from '@google/generative-ai'
  import { GoogleAIFileManager } from '@google/generative-ai/server'
  import env from '#start/env'

  const genAI = new GoogleGenerativeAI(env.get('GEMINI_API_KEY'))
  const fileManager = new GoogleAIFileManager(env.get('GEMINI_API_KEY'))
  ```

### 2. Bridge with AdonisJS Drive
The Google File API SDKs require a path to a local file. Since AdonisJS can store uploaded files in either local disks (`fs`) or cloud storage (`s3` / `gcs`), you must write a dynamic helper to resolve files to a local path before uploading them:
```typescript
import drive from '@adonisjs/drive/services/main'
import app from '@adonisjs/core/services/app'
import { cuid } from '@adonisjs/core/helpers'
import env from '#start/env'
import fs from 'node:fs'
import path from 'node:path'
import { pipeline } from 'node:stream/promises'

/**
 * Resolves a drive file key to a local filesystem path.
 * If the file is on cloud storage, downloads it to the temporary folder.
 * Returns the local path and a boolean indicating if it's a temporary file.
 */
export async function getLocalPath(fileKey: string): Promise<{ localPath: string; isTemp: boolean }> {
  const currentDisk = env.get('DRIVE_DISK')
  
  if (currentDisk === 'fs') {
    return {
      localPath: drive.use().makePath(fileKey),
      isTemp: false
    }
  }

  // Cloud disk: download to tmp directory
  const tempPath = path.join(app.tmpPath(), `gemini-file-${cuid()}`)
  const fileStream = await drive.use().getStream(fileKey)
  await pipeline(fileStream, fs.createWriteStream(tempPath))

  return {
    localPath: tempPath,
    isTemp: true
  }
}
```

### 3. Uploading to Google File API
Perform the upload using the resolved local path. Provide accurate `mimeType` and a semantic `displayName`.
- **Using `@google/genai`**:
  ```typescript
  const uploadResult = await ai.files.upload({
    file: localPath,
    mimeType,
    config: { displayName }
  })
  // uploadResult contains name, uri, mimeType, etc.
  ```
- **Using `@google/generative-ai`**:
  ```typescript
  const uploadResult = await fileManager.uploadFile(localPath, {
    mimeType,
    displayName
  })
  ```

### 4. Active Status Polling (Media Processing)
Large media files (like videos or large audios) undergo asynchronous processing in Google's servers. You must implement a polling loop to wait until the file's state changes from `PROCESSING` to `ACTIVE` before sending it to a generative model:
- **Using `@google/genai`**:
  ```typescript
  let fileState = await ai.files.get({ name: uploadResult.name })
  while (fileState.state === 'PROCESSING') {
    await new Promise((resolve) => setTimeout(resolve, 10000)) // 10s wait
    fileState = await ai.files.get({ name: uploadResult.name })
  }
  if (fileState.state !== 'ACTIVE') {
    throw new Error(`File processing failed with state: ${fileState.state}`)
  }
  ```
- **Using `@google/generative-ai`**:
  ```typescript
  let fileState = await fileManager.getFile(uploadResult.name)
  while (fileState.state === 'PROCESSING') {
    await new Promise((resolve) => setTimeout(resolve, 10000))
    fileState = await fileManager.getFile(uploadResult.name)
  }
  if (fileState.state !== 'ACTIVE') {
    throw new Error(`File processing failed with state: ${fileState.state}`)
  }
  ```

### 5. Invoking Gemini with File References
Once active, pass the file object (or reference) in the contents array.
- **Using `@google/genai`**:
  ```typescript
  const response = await ai.models.generateContent({
    model: 'gemini-2.5-flash',
    contents: [
      uploadResult, // Direct object reference
      'Analyze this media file'
    ]
  })
  ```
- **Using `@google/generative-ai` or Vercel AI SDK**:
  Pass the file data using the `fileData` format:
  ```typescript
  const response = await model.generateContent([
    {
      fileData: {
        fileUri: uploadResult.uri,
        mimeType: uploadResult.mimeType
      }
    },
    'Analyze this media file'
  ])
  ```

### 6. Resource Cleanup and Lifecycle Hooks
Google File API files persist for up to 48 hours unless deleted. Always trigger a cleanup step in a `finally` block to remove both the Google File and any local temporary files:
```typescript
try {
  // Upload and process...
} finally {
  // 1. Delete Google File API reference
  try {
    if (uploadResult?.name) {
      // @google/genai
      await ai.files.delete({ name: uploadResult.name })
      // Or @google/generative-ai
      // await fileManager.deleteFile(uploadResult.name)
    }
  } catch (error) {
    logger.warn({ err: error }, 'Failed to delete file from Google File API')
  }

  // 2. Delete local temp file (if downloaded from cloud storage)
  if (isTemp && localPath) {
    fs.promises.unlink(localPath).catch((error) => {
      logger.warn({ err: error }, 'Failed to delete local temporary file')
    })
  }
}
```

## Constraints
- **Never** perform Base64 conversions for large video/audio payloads in memory. Doing so leads to RAM exhaustion. Always route them through the File API.
- **Never** proceed to generate content using a file without verifying that its state has transitioned to `ACTIVE`.
- **Never** leak local temporary files or Google File API references. Always clean up resources inside `finally` blocks.
- **Do not** write custom file upload protocols. Use the Google SDK's `files.upload` or `uploadFile` methods.
- **Do not** expose raw API keys or hardcode configuration. Access all parameters through the AdonisJS `env` service.
