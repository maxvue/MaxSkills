---
name: adonisjs-puppeteer-rendering-best-practices
description: Use when rendering HTML to PDF or to images, generating reports, exporting spreadsheets, or driving a headless browser in AdonisJS. Triggers on PDF generation (Puppeteer/Playwright/PDFKit), social media post image generation from HTML/CSS templates, Instagram aspect ratios (1:1, 4:5, 9:16), Excel/CSV exports (exceljs), Edge.js reporting templates, headless browser pool/singleton configuration, AdonisJS Drive uploads of generated files, and queueing heavy rendering via BullMQ. Triggers on launchBrowser, captureTemplateScreenshot, renderPostImage, GenerateReportJob, and Puppeteer concurrency/pool tuning.
---

# Padrões e Melhores Práticas de Renderização com Puppeteer no AdonisJS (PDF, Imagem e Planilhas)

## Objetivo
Estabelecer convenções rígidas, eficientes em memória e de alto desempenho para renderizar HTML em PDF de alta fidelidade, gerar imagens de redes sociais a partir de templates HTML/CSS, e exportar planilhas Excel/CSV ricas no AdonisJS v6. Em todos os casos: renderize via Edge.js, otimize memória com streams e padrão singleton de navegador, persista arquivos via Drive e execute cargas pesadas em background via BullMQ.

> Para edição de PDFs já existentes por coordenadas (preencher campos, carimbar texto/assinaturas em posições fixas) com `pdf-lib`, consulte a skill `adonisjs-pdf-coordinate-editing-best-practices`. Esta skill cobre apenas **renderização** de HTML→PDF/imagem e exportação de planilhas.

## Instruções

### 1. Padrões Arquiteturais e Execução Assíncrona de Tarefas Pesadas
* **Nunca gere PDFs, imagens ou relatórios grandes de forma síncrona dentro de uma requisição HTTP.** Isso bloqueia o event loop de thread única do Node.js e a geração via navegador headless consome muita CPU e memória, podendo causar timeouts de gateway ou travamento do servidor.
* **Sempre envie a geração para uma fila em background** usando BullMQ:
  1. Receba a requisição de exportação em um controller (ex: `app/controllers/reports_controller.ts`).
  2. Crie e envie um Job (ex: `GenerateReportJob`, `GeneratePostImageJob` em `app/jobs/`).
  3. Responda imediatamente com o status `202 Accepted` e um ID de rastreamento do job/relatório.
  4. Processe de forma assíncrona, grave a saída via stream/buffer no storage e notifique o usuário via AdonisJS Transmit (SSE) ou e-mail quando concluído.
* No front, o status/lista de relatórios e qualquer GET de dados de página deve passar por uma store `@maxvue/max-pinia` (rotas string `/api/...` resolvidas por `apiGetRoute` do `@maxvue/max-use`), não por `fetch`/axios manual.

### 2. Gerenciamento do Ciclo de Vida do Navegador (Padrão Singleton)
O Puppeteer inicia um processo pesado do Chrome headless. Nunca inicie uma nova instância do navegador a cada requisição ou em loops. Utilize uma classe de serviço que gerencie uma instância única (singleton), inicializando-a sob demanda e encerrando-a no shutdown da aplicação. Em fluxos pontuais fora do singleton, use sempre `try/finally` para garantir o `browser.close()` e evitar processos zumbis do Chrome.

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
          '--disable-dev-shm-usage', // Evita falhas no Docker devido ao tamanho da partição /dev/shm
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

### 3. Renderização de Templates HTML com Edge.js
Desenhe todos os layouts (relatórios, documentos, posts) com templates Edge.js. O Edge fornece herança de layout, componentes e helpers para dados dinâmicos. Para imagens de post, insira as classes compiladas do UnoCSS inline para evitar carregamento de folhas de estilo externas.

```typescript
import edge from '@adonisjs/core/services/edge'

// Relatório
const reportHtml = await edge.render('emails/report_template', { data })

// Imagem de post social
const postHtml = await edge.render('templates/post_template', {
  title: 'Otimize suas aplicações AdonisJS!',
  author: 'Equipe Engeapp',
})
```

### 4. Renderização HTML → PDF de Alta Fidelidade
Reutilize o navegador singleton e gere o buffer do PDF a partir do HTML renderizado pelo Edge.

```typescript
import puppeteerService from '#services/puppeteer_service'

export async function generateReportPdf(html: string): Promise<Buffer> {
  const browser = await puppeteerService.getBrowser()
  const page = await browser.newPage()

  try {
    await page.setContent(html, { waitUntil: 'networkidle0' }) // Aguarda imagens e estilos

    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: { top: '20px', right: '20px', bottom: '20px', left: '20px' },
    })

    return pdfBuffer as Buffer
  } finally {
    await page.close() // SEMPRE feche a página
  }
}
```

### 5. Renderização HTML → Imagem (Proporções do Instagram)
Configure a viewport com densidade elevada (`deviceScaleFactor: 2`) para saída nítida (retina). Padronize dimensões pelas mídias de destino:

* **1:1 Quadrado (Square):** 1080 x 1080 px
* **4:5 Retrato (Portrait):** 1080 x 1350 px
* **9:16 Reels/Stories:** 1080 x 1920 px

* Helper de dimensões (`app/helpers/instagram_helper.ts`):
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

* Serviço gerador (`app/services/image_generator.ts`):
  ```typescript
  import puppeteerService from '#services/puppeteer_service'
  import { getDimensions, InstagramRatio } from '#helpers/instagram_helper'

  export async function generatePostImage(html: string, ratio: InstagramRatio): Promise<Buffer> {
    const browser = await puppeteerService.getBrowser()
    const page = await browser.newPage()

    try {
      const { width, height } = getDimensions(ratio)

      // deviceScaleFactor alto para resolução retina de saída
      await page.setViewport({ width, height, deviceScaleFactor: 2 })

      // Define o conteúdo HTML dinâmico e aguarda o carregamento dos assets
      await page.setContent(html, { waitUntil: 'networkidle0' })

      const buffer = await page.screenshot({ type: 'png', omitBackground: true })

      return buffer as Buffer
    } finally {
      // Crucial: sempre feche a página no finally para evitar memory leaks
      await page.close()
    }
  }
  ```

### 6. Exportações Ricas para Excel/CSV (Streams do ExcelJS)
* **Workbook Padrão (Dados Pequenos < 5000 linhas):** Carregar todo o conjunto na memória é aceitável.
* **Workbook Baseado em Streams (Dados Grandes):** Para milhares de registros, use o gravador por stream (`ExcelJS.stream.xlsx.WorkbookWriter`) para gravar as linhas dinamicamente, mantendo o consumo de memória baixo.

  ```typescript
  import ExcelJS from 'exceljs'

  const tempFilePath = './tmp/report.xlsx'
  const options = {
    filename: tempFilePath,
    useStyles: true,
    useSharedStrings: true,
  }

  const workbook = new ExcelJS.stream.xlsx.WorkbookWriter(options)
  const worksheet = workbook.addWorksheet('Performances')

  // Define os cabeçalhos das colunas
  worksheet.columns = [
    { header: 'ID', key: 'id', width: 10 },
    { header: 'Título do Post', key: 'title', width: 30 },
    { header: 'Taxa de Engajamento', key: 'engagement', width: 15 },
  ]

  // Adiciona as linhas em lotes/pedaços
  for (const item of dataset) {
    worksheet.addRow({ id: item.id, title: item.title, engagement: item.engagement }).commit()
  }

  // Finaliza o arquivo Excel
  await workbook.commit()
  ```

### 7. Armazenamento e Persistência (AdonisJS Drive)
* Não grave arquivos no sistema de arquivos local com `fs.writeFile`. Envie o Buffer gerado diretamente ao storage via Drive para suportar drivers flexíveis (S3, GCS, local).
* Use armazenamento privado para dados confidenciais de clientes e gere URLs assinadas temporárias para download. Conteúdo público (ex: imagens de post) pode usar `visibility: 'public'`.

  ```typescript
  import drive from '@adonisjs/drive/services/main'

  // PDF privado
  await drive.use('s3').put('reports/report-2026.pdf', pdfBuffer, {
    contentType: 'application/pdf',
    visibility: 'private',
  })
  const downloadUrl = await drive.use('s3').getSignedUrl('reports/report-2026.pdf', {
    expiresIn: '15m',
  })

  // Imagem pública de post
  const storagePath = `posts/images/${Date.now()}-feed-post.png`
  await drive.use().put(storagePath, imageBuffer, {
    contentType: 'image/png',
    visibility: 'public',
  })
  ```

### 8. Estrutura de Job Padrão (BullMQ)
* Integre o enfileiramento seguindo a estrutura padrão de Jobs do projeto:
  * Crie a classe do job em `app/jobs/` (ex: `generate_report_job.ts`, `generate_post_image_job.ts`).
  * Declare `static readonly queueName` (ou `static key`).
  * Implemente `static async dispatch(...)` para enfileirar tarefas.
  * Implemente o `handle(job)` para a execução.
  * Registre o worker no script global `commands/worker.ts` e adicione o objeto da fila em `app/services/queue_service.ts`.

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
* **NÃO** bloqueie o event loop com operações síncronas de arquivos (`fs.writeFileSync`). Use versões assíncronas (`fs.promises`) ou streams.
* **NÃO** execute `puppeteer.launch` diretamente dentro de controllers de requisição ou em loops. Use o serviço singleton encapsulado; em fluxos pontuais, garanta o `browser.close()` em `try/finally`. Vazamentos de processos zumbis do Chrome consomem rapidamente toda a RAM.
* **NÃO** deixe páginas/abas abertas. Sempre envolva a captura/geração em `try...finally`, garantindo `page.close()` independentemente de sucesso ou falha.
* **NÃO** use assets de rede lentos (fontes externas, imagens pesadas) sem pré-carregamento ou embutimento como base64; o Puppeteer bloqueará ou dará timeout aguardando `networkidle0`.
* **NÃO** inicie o navegador com aceleração de GPU em ambientes headless/Docker (`--disable-gpu` sempre presente).
* **NÃO** escreva no FS local com `fs.writeFile`/`fs.writeFileSync`. Use sempre `drive.use().put()`.
* **NÃO** exponha URLs brutas do bucket ao público quando os arquivos contiverem dados confidenciais; use URLs assinadas temporárias.
