---
name: adonisjs-image-optimization-sharp-best-practices
description: Use when implementing, reviewing, or debugging server-side image processing, optimization, compression, or format conversion (e.g., WebP, AVIF, JPEG) using Sharp in AdonisJS v6. Triggers on files modifying ImageService, processing uploads, generating thumbnails, or handling media compression background jobs.
---

## Goal
Establish a robust, memory-efficient standard for server-side image processing in AdonisJS v6 using the `sharp` library. This includes optimizing, compressing, generating thumbnails, and converting image formats (AVIF, WebP, JPEG) while integrating with `@adonisjs/drive` and offloading heavy tasks to background workers.

## Instructions

### 1. Dedicated Image Service (`ImageService`)
Create a service to encapsulate image manipulation logic. This avoids mixing image processing libraries directly with controllers or models.

```typescript
// app/services/image_service.ts
import sharp from 'sharp'

export default class ImageService {
  /**
   * Resizes and converts an image buffer to WebP format.
   */
  public async toWebp(
    fileBuffer: Buffer,
    options: { width?: number; height?: number; quality?: number } = {}
  ): Promise<Buffer> {
    const quality = options.quality ?? 80
    
    let pipeline = sharp(fileBuffer)

    if (options.width || options.height) {
      pipeline = pipeline.resize({
        width: options.width,
        height: options.height,
        fit: 'inside',
        withoutEnlargement: true,
      })
    }

    return pipeline
      .webp({ quality, lossless: false, effort: 4 })
      .toBuffer()
  }

  /**
   * Converts an image buffer to AVIF for modern high-compression needs.
   */
  public async toAvif(
    fileBuffer: Buffer,
    options: { width?: number; height?: number; quality?: number } = {}
  ): Promise<Buffer> {
    const quality = options.quality ?? 65
    
    let pipeline = sharp(fileBuffer)

    if (options.width || options.height) {
      pipeline = pipeline.resize({
        width: options.width,
        height: options.height,
        fit: 'inside',
        withoutEnlargement: true,
      })
    }

    return pipeline
      .avif({ quality, effort: 4 })
      .toBuffer()
  }
}
```

### 2. Handling Uploads and Storage Integration
Integrate image processing directly with AdonisJS Drive. Avoid saving the unoptimized files to disk. Process the uploaded file stream or buffer in-memory and write the optimized output.

```typescript
// app/controllers/uploads_controller.ts
import { HttpContext } from '@adonisjs/core/http'
import drive from '@adonisjs/drive/services/main'
import { inject } from '@adonisjs/core'
import ImageService from '#services/image_service'
import crypto from 'node:crypto'
import fs from 'node:fs/promises'

@inject()
export default class UploadsController {
  constructor(protected imageService: ImageService) {}

  public async upload({ request, response }: HttpContext) {
    const image = request.file('image', {
      size: '10mb',
      extnames: ['jpg', 'jpeg', 'png', 'webp', 'avif'],
    })

    if (!image || !image.isValid) {
      return response.badRequest({ errors: image?.errors || 'Invalid image file' })
    }

    // Read file directly into a buffer
    const fileBuffer = await fs.readFile(image.tmpPath!)
    
    // Optimize to WebP in memory
    const optimizedBuffer = await this.imageService.toWebp(fileBuffer, {
      width: 1200,
      quality: 80,
    })

    const fileName = `${crypto.randomUUID()}.webp`
    const storagePath = `uploads/images/${fileName}`

    // Write optimized buffer to Drive (configured storage: S3, local, etc.)
    await drive.use().put(storagePath, optimizedBuffer, {
      contentType: 'image/webp',
    })

    const url = await drive.use().getUrl(storagePath)

    // Delete temp file asynchronously
    if (image.tmpPath) {
      fs.unlink(image.tmpPath).catch(() => {})
    }

    return response.ok({ url, path: storagePath })
  }
}
```

### 3. Background Processing for Heavy Jobs (BullMQ)
For bulk processing, gallery uploads, or multiple output resolutions (like generating multiple responsive sizes and thumbnails), offload the operation to a BullMQ worker to keep HTTP response times fast.

```typescript
// app/jobs/optimize_image_job.ts
import { Job } from 'bullmq'
import drive from '@adonisjs/drive/services/main'
import ImageService from '#services/image_service'
import { inject } from '@adonisjs/core'

interface JobData {
  sourcePath: string
  targetFolder: string
}

@inject()
export default class OptimizeImageJob {
  constructor(protected imageService: ImageService) {}

  public async handle(job: Job<JobData>) {
    const { sourcePath, targetFolder } = job.data

    // 1. Fetch raw image from storage
    const exists = await drive.use().exists(sourcePath)
    if (!exists) return

    // `get()` retorna string (UTF-8) e corrompe binário — use `getBytes()` para ler bytes crus.
    const rawBuffer = Buffer.from(await drive.use().getBytes(sourcePath))

    // 2. Generate Thumbnails and Multi-resolutions using Sharp
    const sizes = [
      { name: 'thumbnail', width: 200 },
      { name: 'medium', width: 600 },
      { name: 'large', width: 1200 },
    ]

    for (const size of sizes) {
      const optimized = await this.imageService.toWebp(rawBuffer, {
        width: size.width,
        quality: 80,
      })

      const targetPath = `${targetFolder}/${size.name}.webp`
      await drive.use().put(targetPath, optimized, {
        contentType: 'image/webp',
      })
    }

    // 3. Cleanup source raw file if needed
    await drive.use().delete(sourcePath)
  }
}
```

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do NOT** block the node event loop processing huge images synchronously in the main HTTP request thread. Offload high-volume or heavy resizing operations to background jobs.
- **Do NOT** write raw unoptimized images directly to the permanent public local storage. Always compress and optimize uploads.
- **Do NOT** upscale images (e.g., resizing a 300px image to 1200px) as it inflates file size while degrading quality. Always use `withoutEnlargement: true`.
- **Do NOT** hardcode local file paths (`fs.writeFileSync`). Use `@adonisjs/drive` to ensure compatibility with distributed architectures (S3, MinIO).
- **Do NOT** forget to asynchronously unlink the temporary files left behind by `bodyparser` (`image.tmpPath`) to prevent running out of disk space on the server.
