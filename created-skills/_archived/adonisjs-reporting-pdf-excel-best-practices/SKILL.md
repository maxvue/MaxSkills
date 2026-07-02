---
name: adonisjs-reporting-pdf-excel-best-practices
description: Use when generating, exporting, or designing reports, PDF documents, and Excel or CSV spreadsheets in AdonisJS. Triggers on PDF generation (using Puppeteer, Playwright, or PDFKit), Excel exports (using exceljs or writing CSVs), generating reporting templates, and queueing reports via BullMQ.
---

# Padrões e Melhores Práticas de Relatórios, Geração de PDF e Excel no AdonisJS

## Objetivo
Estabelecer convenções e padrões rígidos para a geração de documentos PDF de alta fidelidade, planilhas Excel/CSV ricas e relatórios estruturados no framework AdonisJS v6, otimizando o consumo de memória através de streams, persistindo arquivos via Drive e executando exportações pesadas como tarefas em background via BullMQ.

## Instruções

### 1. Padrões Arquiteturais e Execução Assíncrona de Tarefas Pesadas
* **Nunca gere relatórios grandes ou PDFs de forma síncrona dentro de uma requisição HTTP.** Fazer isso bloqueia o event loop de thread única do Node.js, podendo causar timeouts de gateway ou travamento do servidor.
* **Sempre envie a geração de PDF/Excel para uma fila em background** usando BullMQ:
  1. Receba a requisição de exportação em um controller (ex: [ReportsController](file:///home/johnattas/GitHub/socialmedia-node/app/controllers/reports_controller.ts)).
  2. Crie e envie um Job (ex: `GenerateReportJob` em `app/jobs/`).
  3. Responda imediatamente com o status `202 Accepted` e um ID de rastreamento do job/relatório.
  4. Processe o relatório de forma assíncrona, grave a saída via stream no storage e notifique o usuário via AdonisJS Transmit (SSE) ou e-mail quando concluído.

### 2. Geração de PDF de Alta Fidelidade (Puppeteer e Edge.js)
* **Templates HTML com Edge.js:** Desenhe os layouts de relatórios utilizando templates Edge.js. O Edge.js fornece herança de layout, componentes e funções auxiliares para renderizar dados dinâmicos.
* **Gerenciamento Seguro do Ciclo de Vida do Puppeteer:** Navegadores headless consomem muita memória. Você deve garantir a inicialização e o encerramento corretos do navegador usando blocos `try/finally` para evitar vazamentos de processos no sistema operacional.
  
  ```typescript
  import puppeteer from 'puppeteer'
  import edge from '@adonisjs/core/services/edge'

  // Primeiro renderiza o HTML usando a config de views do projeto
  const html = await edge.render('emails/report_template', { data })

  // Inicializa o navegador com as flags recomendadas para ambientes containerizados
  const browser = await puppeteer.launch({
    headless: true,
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage', // Evita falhas no Docker devido ao tamanho da partição /dev/shm
      '--disable-gpu'
    ]
  })

  try {
    const page = await browser.newPage()
    await page.setContent(html, { waitUntil: 'networkidle0' }) // Aguarda o carregamento de imagens e estilos
    
    const pdfBuffer = await page.pdf({
      format: 'A4',
      printBackground: true,
      margin: { top: '20px', right: '20px', bottom: '20px', left: '20px' }
    })
    
    // Processa e salva o buffer do PDF
  } finally {
    await browser.close() // SEMPRE fecha o navegador
  }
  ```

### 3. Exportações Ricas para Excel/CSV (Streams do ExcelJS)
* **Workbook Padrão (Dados Pequenos < 5000 linhas):** Carregar todo o conjunto de dados na memória é aceitável.
* **Workbook Baseado em Streams (Dados Grandes):** Para milhares de registros, use o gravador por stream do ExcelJS (`ExcelJS.stream.xlsx.WorkbookWriter`) para gravar as linhas no disco/storage dinamicamente, mantendo o consumo de memória baixo.

  ```typescript
  import ExcelJS from 'exceljs'
  import fs from 'node:fs'

  const tempFilePath = './tmp/report.xlsx'
  const options = {
    filename: tempFilePath,
    useStyles: true,
    useSharedStrings: true
  }

  const workbook = new ExcelJS.stream.xlsx.WorkbookWriter(options)
  const worksheet = workbook.addWorksheet('Performances')

  // Define os cabeçalhos das colunas
  worksheet.columns = [
    { header: 'ID', key: 'id', width: 10 },
    { header: 'Título do Post', key: 'title', width: 30 },
    { header: 'Taxa de Engajamento', key: 'engagement', width: 15 }
  ]

  // Adiciona as linhas em lotes/pedaços
  for (const item of dataset) {
    worksheet.addRow({ id: item.id, title: item.title, engagement: item.engagement }).commit()
  }

  // Finaliza o arquivo Excel
  await workbook.commit()
  ```

### 4. Armazenamento de Arquivos e Persistência (AdonisJS Drive)
* Não armazene arquivos indefinidamente no sistema de arquivos local.
* Envie os arquivos para buckets públicos ou privados na nuvem (ex: S3, Google Cloud Storage) utilizando o provedor Drive do AdonisJS.
* Use armazenamento privado para dados confidenciais de clientes e gere URLs assinadas temporárias para download.
  
  ```typescript
  import drive from '@adonisjs/drive/services/main'

  // Salvando o PDF gerado
  await drive.use('s3').put('reports/report-2026.pdf', pdfBuffer, {
    contentType: 'application/pdf',
    visibility: 'private'
  })

  // Gerando um link de download seguro e temporário (expira em 15 minutos)
  const downloadUrl = await drive.use('s3').getSignedUrl('reports/report-2026.pdf', {
    expiresIn: '15m'
  })
  ```

### 5. Estrutura de Job Padrão (BullMQ)
* Integre o enfileiramento de relatórios seguindo a estrutura padrão de Jobs do projeto:
  * Crie a classe do job em `app/jobs/generate_report_job.ts`.
  * Declare `static readonly queueName`.
  * Implemente `static async dispatch(...)` para enfileirar tarefas.
  * Implemente `static async handle(job: Job<Data>)` para a execução.
  * Registre o worker no script global [worker.ts](file:///home/johnattas/GitHub/socialmedia-node/commands/worker.ts) e adicione o objeto da fila em [queue_service.ts](file:///home/johnattas/GitHub/socialmedia-node/app/services/queue_service.ts).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NÃO** bloqueie o event loop com operações síncronas de arquivos (`fs.writeFileSync`). Use versões assíncronas (`fs.promises`) ou streams.
* **NÃO** inicialize o Puppeteer sem um bloco `try/finally` que fecha o navegador. Vazamentos de processos zumbis do Chrome consumirão rapidamente toda a memória RAM da hospedagem.
* **NÃO** exponha URLs brutas dos arquivos do bucket diretamente ao público se os relatórios contiverem informações confidenciais do banco de dados, métricas ou credenciais. Use URLs assinadas.
