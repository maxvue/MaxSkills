---
name: adonisjs-image-optimization-sharp-best-practices
description: Use when implementing, reviewing, or debugging server-side image processing, optimization, compression, or format conversion (e.g., WebP, AVIF, JPEG) using Sharp in AdonisJS v6. Triggers on files modifying ImageService, processing uploads, generating thumbnails, or handling media compression background jobs.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Estabelecer um padrão robusto e eficiente em memória para o processamento de imagens no lado do servidor no AdonisJS v6 usando a biblioteca `sharp`. Isso inclui otimizar, comprimir, gerar thumbnails e converter formatos de imagem (AVIF, WebP, JPEG), integrando com o `@adonisjs/drive` e delegando tarefas pesadas a workers em segundo plano.

## Instruções

### 1. Service Dedicado de Imagem (`ImageService`)
Crie um service para encapsular a lógica de manipulação de imagens. Isso evita misturar bibliotecas de processamento de imagem diretamente com controllers ou models.

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
   * Converte um buffer de imagem para AVIF, para necessidades modernas de alta compressão.
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

### 2. Tratamento de Uploads e Integração com Storage
Integre o processamento de imagens diretamente com o AdonisJS Drive. Evite salvar os arquivos não otimizados em disco. Processe o stream ou buffer do arquivo enviado em memória e escreva a saída otimizada.

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

    // Lê o arquivo diretamente para um buffer
    const fileBuffer = await fs.readFile(image.tmpPath!)
    
    // Otimiza para WebP em memória
    const optimizedBuffer = await this.imageService.toWebp(fileBuffer, {
      width: 1200,
      quality: 80,
    })

    const fileName = `${crypto.randomUUID()}.webp`
    const storagePath = `uploads/images/${fileName}`

    // Escreve o buffer otimizado no Drive (storage configurado: S3, local, etc.)
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

### 3. Processamento em Segundo Plano para Jobs Pesados (BullMQ)
Para processamento em massa, uploads de galeria ou múltiplas resoluções de saída (como gerar vários tamanhos responsivos e thumbnails), delegue a operação a um worker BullMQ para manter rápidos os tempos de resposta HTTP.

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

    // 1. Busca a imagem crua no storage
    const exists = await drive.use().exists(sourcePath)
    if (!exists) return

    // `get()` retorna string (UTF-8) e corrompe binário — use `getBytes()` para ler bytes crus.
    const rawBuffer = Buffer.from(await drive.use().getBytes(sourcePath))

    // 2. Gera thumbnails e múltiplas resoluções usando o Sharp
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

    // 3. Limpa o arquivo cru de origem, se necessário
    await drive.use().delete(sourcePath)
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** bloqueie o event loop do node processando imagens enormes de forma síncrona na thread principal da requisição HTTP. Delegue operações de redimensionamento de alto volume ou pesadas para background jobs.
- **NÃO** escreva imagens cruas não otimizadas diretamente no storage local público permanente. Sempre comprima e otimize os uploads.
- **NÃO** faça upscale de imagens (ex: redimensionar uma imagem de 300px para 1200px), pois isso infla o tamanho do arquivo enquanto degrada a qualidade. Sempre use `withoutEnlargement: true`.
- **NÃO** deixe caminhos de arquivo locais hardcoded (`fs.writeFileSync`). Use o `@adonisjs/drive` para garantir compatibilidade com arquiteturas distribuídas (S3, MinIO).
- **NÃO** esqueça de remover (unlink) de forma assíncrona os arquivos temporários deixados pelo `bodyparser` (`image.tmpPath`) para evitar ficar sem espaço em disco no servidor.
