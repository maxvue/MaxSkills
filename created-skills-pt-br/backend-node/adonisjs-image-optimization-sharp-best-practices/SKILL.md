---
name: adonisjs-image-optimization-sharp-best-practices
description: Use when implementing, reviewing, or debugging server-side image processing, optimization, compression, or format conversion (e.g., WebP, AVIF, JPEG) using Sharp in AdonisJS v6. Triggers on files modifying ImageService, processing uploads, generating thumbnails, or handling media compression background jobs.
---

## Objetivo
Estabelecer um padrão robusto e eficiente no uso de memória para processamento de imagens no backend com AdonisJS v6 usando a biblioteca `sharp`. Isso inclui otimização, compactação, geração de miniaturas (thumbnails) e conversão de formatos de imagem (AVIF, WebP, JPEG), integrando com `@adonisjs/drive` e delegando tarefas pesadas para workers em segundo plano (background jobs).

## Instruções

### 1. Serviço de Imagem Dedicado (`ImageService`)
Crie um serviço para encapsular a lógica de manipulação de imagens. Isso evita misturar bibliotecas de processamento de imagem diretamente nos controllers ou models.

```typescript
// app/services/image_service.ts
import sharp from 'sharp'

export default class ImageService {
  /**
   * Redimensiona e converte um buffer de imagem para o formato WebP.
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
   * Converte um buffer de imagem para AVIF para compressão moderna de alta qualidade.
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

### 2. Tratamento de Uploads e Integração de Armazenamento
Integre o processamento de imagem diretamente com o AdonisJS Drive. Evite salvar os arquivos não otimizados no disco. Processe o stream ou buffer do arquivo enviado em memória e salve a saída otimizada.

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
      return response.badRequest({ errors: image?.errors || 'Arquivo de imagem inválido' })
    }

    // Lê o arquivo temporário diretamente em um buffer
    const fileBuffer = await fs.readFile(image.tmpPath!)
    
    // Otimiza para WebP em memória
    const optimizedBuffer = await this.imageService.toWebp(fileBuffer, {
      width: 1200,
      quality: 80,
    })

    const fileName = `${crypto.randomUUID()}.webp`
    const storagePath = `uploads/images/${fileName}`

    // Grava o buffer otimizado no Drive (S3, local, etc.)
    await drive.use().put(storagePath, optimizedBuffer, {
      contentType: 'image/webp',
    })

    const url = await drive.use().getUrl(storagePath)

    // Remove o arquivo temporário de forma assíncrona
    if (image.tmpPath) {
      fs.unlink(image.tmpPath).catch(() => {})
    }

    return response.ok({ url, path: storagePath })
  }
}
```

### 3. Processamento em Segundo Plano para Tarefas Pesadas (BullMQ)
Para processamento em lote, uploads de galerias ou geração de múltiplas resoluções (como gerar vários tamanhos responsivos e thumbnails), delegue a operação para um worker do BullMQ para manter o tempo de resposta HTTP rápido.

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

    // 1. Recupera a imagem original do storage
    const exists = await drive.use().exists(sourcePath)
    if (!exists) return

    const rawBuffer = await drive.use().get(sourcePath)

    // 2. Gera miniaturas e resoluções responsivas usando o Sharp
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

    // 3. Limpa o arquivo original não otimizado se necessário
    await drive.use().delete(sourcePath)
  }
}
```

## Restrições
- **NÃO** bloqueie o event loop do Node.js processando imagens gigantes de forma síncrona na thread principal de requisições HTTP. Delegue operações de redimensionamento pesadas ou em lote para jobs em segundo plano (workers).
- **NÃO** salve imagens originais não otimizadas diretamente no armazenamento local permanente público. Sempre compacte e otimize os uploads.
- **NÃO** aumente o tamanho de imagens (upscaling) de forma artificial (ex: redimensionar uma imagem de 300px para 1200px), pois isso infla o tamanho do arquivo sem melhorar a qualidade. Use sempre `withoutEnlargement: true`.
- **NÃO** utilize caminhos locais fixos e síncronos no disco (`fs.writeFileSync`). Use `@adonisjs/drive` para garantir a compatibilidade com arquiteturas distribuídas (S3, MinIO).
- **NÃO** se esqueça de remover de forma assíncrona os arquivos temporários deixados pelo `bodyparser` (`image.tmpPath`) para evitar o esgotamento do espaço em disco no servidor.
