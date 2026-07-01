---
name: adonisjs-media-processing-ffmpeg-best-practices
description: Use when creating, modifying, reviewing, or debugging video and audio processing logic, utilizing FFmpeg or FFprobe, compressing media files for social media platforms (Instagram Reels, Stories, or Feed), extracting thumbnails, or converting audio formats (Opus, AAC, MP3, WAV) in AdonisJS v6. Triggers on fluent-ffmpeg integration, spawning child processes for media manipulation, metadata extraction, or stream-based media pipelines.
---

# Processamento de Mídia com FFmpeg no AdonisJS — Boas Práticas

## Objetivo
Estabelecer diretrizes seguras, performáticas e confiáveis para manipulação de arquivos de áudio e vídeo usando FFmpeg e FFprobe em aplicações AdonisJS, garantindo conformidade com os limites rígidos de APIs de redes sociais (como o Instagram).

## Instruções

### 1. Integração da Biblioteca e Resolução de Binários
* Integre o `fluent-ffmpeg` encapsulando-o em classes de serviço utilitárias assíncronas em `app/services/` ou `app/helpers/`.
* Evite codificar os caminhos dos binários diretamente no código (hardcoding). Leia `FFMPEG_PATH` e `FFPROBE_PATH` a partir da configuração de ambiente (`start/env.ts`), ou deixe que o sistema operacional os resolva dinamicamente se estiverem disponíveis globalmente.
* Declare imports dinâmicos ou definições de tipo de forma clara:
  ```typescript
  import ffmpeg from 'fluent-ffmpeg'
  ```

### 2. Extração de Metadados de Vídeo (FFprobe)
* Sempre investigue (probe) arquivos de mídia de forma assíncrona antes de iniciar tarefas pesadas de codificação.
* Verifique codecs, taxa de bits (bitrate), dimensões, duração, formato e taxa de quadros (framerate).
* Use um wrapper Promisified em torno de `ffmpeg.ffprobe` para consultar as propriedades do vídeo:
  ```typescript
  import { promisify } from 'node:util'
  const ffprobeAsync = promisify(ffmpeg.ffprobe)
  ```

### 3. Compressão e Transcodificação em Conformidade com o Instagram
* Ao otimizar vídeo para o Instagram (Feed, Stories, Reels), aplique critérios de codificação rigorosos:
  * **Codec de Vídeo:** H.264 (AVC) - use `-c:v libx264` or fluent-ffmpeg `.videoCodec('libx264')`.
  * **Codec de Áudio:** AAC - use `-c:a aac` or fluent-ffmpeg `.audioCodec('aac')`.
  * **Taxa de Quadros (FPS):** Máximo 30 FPS - use `.fps(30)`.
  * **Resolução:** Garanta a conformidade com as proporções recomendadas (9:16 para Reels/Stories, 1:1 ou 4:5 para Feed).
  * **Bitrate:** Limite o bitrate de vídeo a aproximadamente 5Mbps (5000k) e o de áudio a 128kbps.
  * **Formato de Pixel:** Use `-pix_fmt yuv420p` para alta compatibilidade de reprodução.

### 4. Geração Automatizada de Thumbnail
* Extraia thumbnails em carimbos de data/hora específicos (por exemplo, no primeiro segundo ou no meio do vídeo) para gerar imagens de capa do vídeo (poster images).
* Salve o arquivo gerado diretamente no diretório temporário antes de enviá-lo para o armazenamento de destino.
* Exemplo de chamada para extração de thumbnail com fluent-ffmpeg:
  ```typescript
  ffmpeg(videoPath)
    .screenshots({
      timestamps: [1],
      filename: 'thumbnail.jpg',
      folder: tmpDir,
    })
  ```

### 5. Gerenciamento Seguro de Arquivos Temporários e Recursos
* Execute todas as manipulações pesadas de arquivo dentro de um diretório temporário dedicado (por exemplo, uma subpasta dentro de `/tmp` ou usando o `tmpdir()` do módulo `node:os`).
* **Limpeza Absoluta:** Use blocos `try...finally` para garantir a exclusão de arquivos locais temporários (tanto o arquivo original carregado quanto o arquivo transcodificado final) após a conclusão ou falha do processo. Isso evita que o disco local fique cheio.
* Integre sempre com o provedor de Drive do AdonisJS para buscar o stream do arquivo bruto ou salvar o arquivo final processado.
  ```typescript
  import drive from '@adonisjs/drive/services/main'
  ```

### 6. Timeouts de Subprocessos e Tratamento de Exceções
* Nunca deixe o FFmpeg rodando indefinidamente. Defina limites de tempo estritos para a execução (ex: máximo de 60 a 120 segundos, dependendo da duração do vídeo).
* Capture a saída de erro padrão (`stderr`) e registre as mensagens de erro detalhadas da CLI do FFmpeg usando o serviço de Logger do AdonisJS.
* Intercepte `SIGKILL`, códigos de saída ou handlers de eventos (`error`) para limpar processos pendentes.

## Restrições
* **NÃO** execute a codificação pesada do FFmpeg de forma síncrona dentro de controllers HTTP. Sempre despache essas tarefas para jobs em segundo plano (ex: BullMQ).
* **NÃO** envie vídeos não comprimidos ou não verificados diretamente para as APIs do Meta/Instagram.
* **NÃO** deixe arquivos temporários órfãos no sistema de arquivos local. Todos os arquivos temporários DEVEM ser excluídos no bloco `finally` da execução.
* **NÃO** defina caminhos absolutos locais do sistema para binários ou pastas de entrada/saída de forma fixa (hardcoded).

## Examples

### Extração de Metadados com FFprobe (Promisified)
```typescript
import ffmpeg from 'fluent-ffmpeg'

export interface VideoMetadata {
  duration: number
  width: number
  height: number
  fps: number
  codec: string
}

export async function getVideoMetadata(filePath: string): Promise<VideoMetadata> {
  return new Promise((resolve, reject) => {
    ffmpeg.ffprobe(filePath, (err, metadata) => {
      if (err) return reject(err)
      
      const videoStream = metadata.streams.find((s) => s.codec_type === 'video')
      if (!videoStream) {
        return reject(new Error('Nenhum stream de vídeo encontrado'))
      }

      // Calcula FPS
      let fps = 30
      if (videoStream.avg_frame_rate) {
        const [num, den] = videoStream.avg_frame_rate.split('/').map(Number)
        if (den > 0) fps = Math.round(num / den)
      }

      resolve({
        duration: metadata.format.duration ? Number(metadata.format.duration) : 0,
        width: videoStream.width || 0,
        height: videoStream.height || 0,
        fps,
        codec: videoStream.codec_name || 'unknown',
      })
    })
  })
}
```

### Job de Transcodificação de Vídeo com Limpeza Garantida
```typescript
import { join } from 'node:path'
import { tmpdir } from 'node:os'
import fs from 'node:fs/promises'
import { createWriteStream } from 'node:fs'
import { pipeline } from 'node:stream/promises'
import ffmpeg from 'fluent-ffmpeg'
import drive from '@adonisjs/drive/services/main'
import logger from '@adonisjs/core/services/logger'

export async function processVideoForInstagram(
  driveKey: string, 
  outputKey: string
): Promise<void> {
  const localInputPath = join(tmpdir(), `input-${Date.now()}.mp4`)
  const localOutputPath = join(tmpdir(), `output-${Date.now()}.mp4`)

  try {
    // 1. Faz o download do arquivo do AdonisJS Drive para o /tmp local
    //    Use getStream()/getBytes() para binários — get() retorna string e
    //    corromperia arquivos de vídeo. Aqui usamos o stream com pipeline.
    const inputStream = await drive.use().getStream(driveKey)
    await pipeline(inputStream, createWriteStream(localInputPath))

    // 2. Transcodifica o vídeo usando fluent-ffmpeg
    await new Promise<void>((resolve, reject) => {
      ffmpeg(localInputPath)
        .videoCodec('libx264')
        .audioCodec('aac')
        .outputOptions([
          '-pix_fmt yuv420p',
          '-b:v 5000k',
          '-maxrate 5000k',
          '-bufsize 10000k',
          '-profile:v high',
          '-level 4.0'
        ])
        .fps(30)
        .size('1080x?') // Mantém a proporção, com largura de 1080px (padrão Instagram)
        .timeout(120) // Finaliza o processo caso passe de 2 minutos
        .on('start', (cmd) => {
          logger.info(`FFmpeg iniciado com o comando: ${cmd}`)
        })
        .on('error', (err) => {
          logger.error(`O processo FFmpeg falhou: ${err.message}`)
          reject(err)
        })
        .on('end', () => {
          logger.info('Processamento FFmpeg concluído com sucesso')
          resolve()
        })
        .save(localOutputPath)
    })

    // 3. Faz o upload do arquivo otimizado de volta para o AdonisJS Drive
    //    Assinatura correta: put(key, contents, options).
    const outputBuffer = await fs.readFile(localOutputPath)
    await drive.use().put(outputKey, outputBuffer, {
      contentType: 'video/mp4',
    })

  } finally {
    // 4. Limpeza garantida de todos os arquivos temporários locais
    await fs.unlink(localInputPath).catch(() => {})
    await fs.unlink(localOutputPath).catch(() => {})
  }
}
```
