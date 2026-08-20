---
name: adonisjs-ai-image-generation-best-practices
description: Use when designing, implementing, configuring, or debugging AI-based image generation features (using Google Imagen via @ai-sdk/google) within AdonisJS v6 backend. Triggers on setting up Vercel AI SDK image generation, handling image upload/storage to local Drive/S3, defining image prompt templates for graphic editor agents, and integrating image generation jobs in BullMQ.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Estabelecer padrões robustos, resilientes e com controle de custos para integrar a geração de imagens baseada em IA (Google Imagen via `@ai-sdk/google`) no backend AdonisJS v6, incluindo o processamento assíncrono de filas de tarefas via BullMQ, armazenamento persistente de arquivos usando o `@adonisjs/drive` e o registro de custos/uso de tokens de IA.

## Instruções

## 1. Configuração do SDK de Geração de Imagens por IA
Ao integrar a geração de imagens, use o Vercel AI SDK (`ai` e `@ai-sdk/google`, o único provider de imagem instalado no projeto). Evite usar chamadas REST diretas ou SDKs antigos e desatualizados.

### Exemplo: Serviço Auxiliar (`app/services/image_generation_service.ts`)
```typescript
import { generateImage } from 'ai'
import { google } from '@ai-sdk/google'
import env from '#start/env'

export class ImageGenerationService {
  /**
   * Gera uma imagem usando o modelo Google Imagen 4 via Vercel AI SDK
   */
  async generate(prompt: string, aspectRatio: '1:1' | '3:4' | '4:3' | '16:9' = '4:3'): Promise<Buffer> {
    const model = google.image('imagen-4.0-generate-001')

    // O Vercel AI SDK aceita `size` OU `aspectRatio` (mutuamente exclusivos).
    // A resposta expõe `image.uint8Array` e `image.base64` (confirme contra a versão instalada do pacote `ai`).
    const { image } = await generateImage({
      model,
      prompt,
      aspectRatio,
    })

    // Retorna a imagem como um buffer
    return Buffer.from(image.uint8Array)
  }
}
```

Certifique-se de que as configurações do modelo e do provedor de IA sejam carregadas a partir do arquivo `env`.

---

## 2. Engenharia de Prompts Visuais e Padrões do Projeto
A geração de imagens por IA produz melhores resultados quando os prompts originais são envelopados com predefinições do projeto fotovoltaico e melhorias estruturais.

- **Prefixo / Sufixo de Contexto:** Adicione padrões de qualidade (ex: iluminação, estilo, composição) e estilos negativos diretamente na requisição feita ao backend.
- **Envelopamento de Prompt do Editor Gráfico:**
```typescript
export function buildVisualPrompt(userPrompt: string, projectStyle: string): string {
  return `
    <StylePreset>
      Style: ${projectStyle}
      Quality: Professional photography, sharp focus, 8k resolution, high dynamic range
    </StylePreset>
    <UserPrompt>
      ${userPrompt}
    </UserPrompt>
    <Constraints>
      No text overlays, no distorted hands, no watermark, no low resolution
    </Constraints>
  `.trim()
}
```

---

## 3. Armazenamento Persistente com `@adonisjs/drive`
As APIs de IA de terceiros retornam URLs temporárias de imagens que expiram rapidamente (geralmente em 1 hora). Você **deve** baixar e persistir a imagem gerada imediatamente no armazenamento do seu sistema.

### Fluxo de Download e Armazenamento:
1. Gere a imagem e obtenha o Buffer (ou faça o download se a API retornar uma URL).
2. Salve o arquivo usando o serviço centralizado `@adonisjs/drive`.
3. Use `cuid()` ou `ulid()` para gerar nomes de arquivo únicos e seguros.

```typescript
import drive from '@adonisjs/drive/services/main'
import { cuid } from '@adonisjs/core/helpers'
import { ImageGenerationService } from '#services/image_generation_service'

export default class ImageProcessor {
  protected generator = new ImageGenerationService()

  async processAndStore(prompt: string, projectId: string): Promise<string> {
    // 1. Gera o Buffer da imagem
    const imageBuffer = await this.generator.generate(prompt)

    // 2. Define o caminho da chave única
    const key = `projects/${projectId}/generated-images/${cuid()}.jpg`

    // 3. Grava diretamente no Drive (S3 / disco local)
    await drive.use().put(key, imageBuffer, {
      contentType: 'image/jpeg',
    })

    return key
  }
}
```

---

## 4. Integração Resiliente de Jobs no BullMQ
A geração de imagens é lenta (geralmente levando de 5 a 15 segundos) e está sujeita a limites de taxa dos provedores (rate limits). **Nunca** execute isso de forma síncrona dentro de um controller HTTP. Roteie sempre através de uma fila de tarefas do BullMQ.

### Definição do Job (`app/jobs/image_generation_job.ts`)
```typescript
import type { Job } from 'bullmq'
import { imageGenerationQueue } from '#services/queue_service'
import ImageProcessor from '#services/image_processor'
import { saveAiCost } from '#helpers/ai_cost_helper'

export interface ImageGenerationJobData {
  projectId: string
  prompt: string
}

export default class ImageGenerationJob {
  static readonly queueName = 'image-generation'

  static async dispatch(payload: ImageGenerationJobData) {
    await imageGenerationQueue.add('generate-image', payload, {
      attempts: 5,
      backoff: {
        type: 'exponential',
        delay: 10000, // 10s de atraso inicial
      },
      removeOnComplete: { count: 100 },
      removeOnFail: { count: 500 },
    })
  }

  static async handle(job: Job<ImageGenerationJobData>) {
    const { projectId, prompt } = job.data
    const processor = new ImageProcessor()

    try {
      const fileKey = await processor.processAndStore(prompt, projectId)

      // Persiste o resultado no banco de dados e atualiza o registro do Projeto
      // Exemplo:
      // const project = await Project.findOrFail(projectId)
      // await project.merge({ imageUrl: fileKey, status: 'ready' }).save()

      // Registra o Custo da API
      await saveAiCost('Project', projectId, {
        tokens: 0, // A geração geralmente tem preço fixo ou específico por modelo
        model: 'imagen-4.0-generate-001',
        costInCents: 3, // Preço de referência em centavos por imagem
      })
    } catch (error) {
      // Em caso de erros de cota, a lógica de retry é gerenciada pelo BullMQ
      throw error
    }
  }
}
```

---

## 5. Fallbacks e Monitoramento
- **Imagem de Fallback:** Defina um placeholder visual padrão caso todas as tentativas falhem.
- **Log Estruturado de Erros:** Use o Logger do AdonisJS para registrar falhas detalhadas na geração (ex: bloqueios de segurança, prompts inválidos, cota excedida).

```typescript
import logger from '@adonisjs/core/services/logger'

// dentro do bloco catch:
logger.error({ err: error, prompt }, 'Falha ao gerar imagem via IA')
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Nunca** armazene URLs externas temporárias retornadas por APIs de IA diretamente no banco de dados. Sempre baixe e salve os arquivos via `@adonisjs/drive` e persista o caminho local/S3 resolvido.
- **Nunca** execute a geração de imagens por IA de forma síncrona em requisições de controllers. Roteie sempre para uma fila do BullMQ.
- **Nunca** ignore políticas de erro. Configure sempre retries exponenciais e controle de limites de taxa de chamadas no BullMQ.
- **Não** grave arquivos utilizando diretamente o módulo `fs` ou `fs/promises` do Node. Use sempre o `@adonisjs/drive` para garantir portabilidade de armazenamento.
