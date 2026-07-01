---
name: adonisjs-puppeteer-image-generation-best-practices
description: Use when setting up, configuring, or debugging Puppeteer in AdonisJS to generate social media post images from HTML/CSS templates, rendering Edge views, managing browser instances in background BullMQ jobs, capturing screenshots with Instagram aspect ratios (1:1, 4:5, 9:16), or optimizing headless browser performance and concurrency. Triggers on launchBrowser, captureTemplateScreenshot, renderPostImage, and Puppeteer pool configuration.
---

# Boas Práticas de Geração de Imagem com Puppeteer no AdonisJS

## Objetivo
Estabelecer padrões robustos, eficientes em termos de memória e de alto desempenho para a geração de imagens de redes sociais a partir de templates HTML/CSS usando Puppeteer, Edge.js e AdonisJS v6.

## Instruções

### 1. Gerenciamento do Ciclo de Vida do Navegador (Padrão Singleton)
O Puppeteer inicia um processo pesado do Chrome headless. Nunca inicie uma nova instância do navegador a cada requisição. Utilize uma classe de serviço que gerencie uma instância única (singleton) do navegador, inicializando-a sob demanda e encerrando-a no encerramento da aplicação.

* Crie um serviço em `app/services/puppeteer_service.ts`:
  ```typescript
  import puppeteer, { Browser } from 'puppeteer'
  import app from '@adonisjs/core/services/app'

  export class PuppeteerService {
    private browser: Browser | null = null

    /**
     * Obtém ou inicializa a instância singleton do navegador
     */
    async getBrowser(): Promise<Browser> {
      if (this.browser && this.browser.connected) {
        return this.browser
      }

      this.browser = await puppeteer.launch({
        headless: true,
        args: [
          '--no-sandbox',
          '--disable-setuid-sandbox',
          '--disable-dev-shm-usage',
          '--disable-gpu',
        ],
      })

      // Registra o gancho de encerramento para limpar os processos quando a aplicação parar
      app.terminating(async () => {
        await this.close()
      })

      return this.browser
    }

    /**
     * Limpa e fecha a instância do navegador
     */
    async close() {
      if (this.browser) {
        await this.browser.close()
        this.browser = null
      }
    }
  }

  const puppeteerService = new PuppeteerService()
  export default puppeteerService
  ```

### 2. Proporções de Aspecto e Viewport do Instagram
Configure a viewport da página com densidade de saída elevada (`deviceScaleFactor: 2`) para obter imagens nítidas (retina). Padronize as dimensões com base nas mídias de destino do Instagram.

* **1:1 Quadrado (Square):** 1080 x 1080 px
* **4:5 Retrato (Portrait):** 1080 x 1350 px
* **9:16 Reels/Stories:** 1080 x 1920 px

* Helper de implementação:
  ```typescript
  export type InstagramRatio = 'square' | 'portrait' | 'reels'

  export function getDimensions(ratio: InstagramRatio) {
    switch (ratio) {
      case 'portrait':
        return { width: 1080, height: 1350 }
      case 'reels':
        return { width: 1080, height: 1920 }
      case 'square':
      default:
        return { width: 1080, height: 1080 }
    }
  }
  ```

### 3. Renderização Dinâmica de Templates com Edge e UnoCSS
Compile templates dinâmicos utilizando o serviço de renderização Edge do AdonisJS e insira as classes compiladas do UnoCSS inline para evitar o carregamento de folhas de estilo externas.

```typescript
import edge from '@adonisjs/core/services/edge'

// Renderiza a view utilizando o sistema de templates Edge.js
const html = await edge.render('templates/post_template', {
  title: 'Otimize suas aplicações AdonisJS!',
  author: 'Equipe Engeapp',
})
```

Dentro do serviço gerador:
```typescript
import puppeteerService from '#services/puppeteer_service'
import { getDimensions, InstagramRatio } from '#helpers/instagram_helper'

export async function generatePostImage(html: string, ratio: InstagramRatio): Promise<Buffer> {
  const browser = await puppeteerService.getBrowser()
  const page = await browser.newPage()

  try {
    const { width, height } = getDimensions(ratio)
    
    // Define um deviceScaleFactor alto para resolução retina de saída
    await page.setViewport({
      width,
      height,
      deviceScaleFactor: 2, 
    })

    // Define o conteúdo HTML dinâmico e aguarda o carregamento dos assets
    await page.setContent(html, { waitUntil: 'networkidle0' })

    // Captura a tela como PNG ou JPEG de alta qualidade
    const buffer = await page.screenshot({
      type: 'png',
      omitBackground: true,
    })

    return buffer as Buffer
  } finally {
    // Crucial: Sempre feche as páginas/abas no bloco finally para evitar vazamentos de memória (memory leaks)
    await page.close()
  }
}
```

### 4. Upload Direto usando o AdonisJS Drive
Em vez de gravar arquivos temporários no disco local, envie diretamente o Buffer da imagem gerada para o armazenamento usando o AdonisJS Drive.

```typescript
import drive from '@adonisjs/drive/services/main'
import { generatePostImage } from '#services/image_generator'

const imageBuffer = await generatePostImage(htmlContent, 'square')
const storagePath = `posts/images/${Date.now()}-feed-post.png`

// Insere o buffer diretamente no storage
await drive.use().put(storagePath, imageBuffer, {
  contentType: 'image/png',
  visibility: 'public',
})
```

### 5. Execução em Segundo Plano com BullMQ
A geração de imagens via navegador headless consome muita CPU e memória. Mova essa tarefa para fora da thread de requisição HTTP utilizando um job em segundo plano do BullMQ.

* Definição do Job: `app/jobs/generate_post_image_job.ts`
  ```typescript
  import { Job } from 'bullmq'
  import { generatePostImage } from '#services/image_generator'
  import drive from '@adonisjs/drive/services/main'

  export interface PostGenerationData {
    htmlContent: string
    ratio: 'square' | 'portrait' | 'reels'
    destinationPath: string
  }

  export default class GeneratePostImageJob {
    static key = 'GeneratePostImageJob'

    async handle(job: Job<PostGenerationData>) {
      const { htmlContent, ratio, destinationPath } = job.data

      // Executa no worker em segundo plano
      const buffer = await generatePostImage(htmlContent, ratio)

      await drive.use().put(destinationPath, buffer, {
        contentType: 'image/png',
      })
    }
  }
  ```

## Restrições
* NÃO execute `puppeteer.launch` diretamente dentro de controllers de requisição ou em loops. Use sempre o serviço singleton encapsulado.
* NÃO deixe páginas abertas. Sempre envolva a captura da imagem em um bloco `try...finally`, garantindo que `page.close()` seja chamado independentemente de sucesso ou falha.
* NÃO use assets de rede lentos (como fontes externas ou imagens pesadas) sem fazer pré-carregamento ou embuti-los como base64; caso contrário, o Puppeteer bloqueará ou causará timeout aguardando `networkidle0`.
* NÃO escreva arquivos no sistema de arquivos local usando `fs.writeFile`. Use sempre o helper do AdonisJS Drive `drive.use().put()` para suportar drivers de armazenamento flexíveis (S3, local, etc.).
* NÃO inicie instâncias do navegador com aceleração de GPU ativada em ambientes headless ou Docker (o argumento `--disable-gpu` deve sempre ser incluído ao lançar o browser).
