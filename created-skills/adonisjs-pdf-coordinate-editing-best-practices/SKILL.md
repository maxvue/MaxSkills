---
name: adonisjs-pdf-coordinate-editing-best-practices
description: Use when loading existing PDF templates, placing texts or lines using coordinate systems (millimeters to points conversion), configuring fonts, colors, and line parameters, or testing PDF manipulation using pdf-lib in AdonisJS. Triggers on PdfEditService, coordinate conversion, loading PDF bytes, drawing text column, or drawing lines on PDF pages.
---

# Boas Práticas de Edição de PDF por Coordenadas no AdonisJS

## Objetivo
Estabelecer padrões claros e consistentes para importação, edição e geração de documentos PDF via sobreposição de coordenadas (traduzindo milímetros com origem no topo-esquerdo para pontos com origem na base-esquerda) usando a biblioteca `pdf-lib` em serviços de backend do AdonisJS v6.

## Instruções

### 1. Estrutura do Serviço de PDF
Toda manipulação de PDF baseada em coordenadas deve ser encapsulada em uma classe Service dedicada chamada `PdfEditService` (tipicamente localizada em `app/services/pdf/pdf_edit_service.ts`), utilizando a biblioteca `pdf-lib`.
- **Métodos de Fábrica (Factory):** Não instancie `new PdfEditService()`. Utilize métodos estáticos assíncronos como `.create(width, height)` para novos documentos em branco ou `.load(bytes)` para carregar templates existentes.
- **Embutimento de Fontes:** Carregue e embuta fontes padrão (como `StandardFonts.Helvetica` e `StandardFonts.HelveticaBold`) de forma assíncrona dentro da fábrica durante a inicialização do serviço.
- **Interface Fluente:** Retorne `this` (a própria instância do serviço) em todos os métodos de desenho para permitir o encadeamento limpo de chamadas.

### 2. Conversão de Coordenadas de Milímetros para Pontos
- **Conversão de Unidade:** Pontos padrão de PDF são definidos como 72 pontos por polegada. Converta milímetros para pontos utilizando o fator: `MM_TO_PT = 72 / 25.4`.
- **Mapeamento de Origem:**
  - Os templates legados em PHP (TCPDF/FPDI) utilizam a origem ($0,0$) no canto **superior esquerdo** com o eixo $Y$ crescendo para baixo ($y\downarrow$).
  - A biblioteca `pdf-lib` utiliza a origem ($0,0$) no canto **inferior esquerdo** com o eixo $Y$ crescendo para cima ($y\uparrow$).
  - Ao posicionar elementos, mapeie a coordenada $y$ conforme a seguinte fórmula:
    $$\text{yPt} = \text{pageHeight} - (yMm \times \text{MM\_TO\_PT}) - \text{offset}$$
    Para linhas de texto, o offset deve ser igual ao tamanho da fonte, pois o `pdf-lib` alinha a linha de base do texto. Para retângulos, o offset deve ser a própria altura do retângulo em pontos.

### 3. Utilitários Principais de Desenho
O serviço deve fornecer suporte para as seguintes operações básicas:
- **`text(xMm, yMm, value, options)`**: Posiciona uma string de texto em $(x, y)$ em mm. Use a opção `align: 'C' | 'R' | 'L'` para ajustar a coordenada $X$ dinamicamente com base na largura do texto obtida por `font.widthOfTextAtSize()`.
- **`textColumn(xMm, yMm, values, spaceMm, options)`**: Empilha um array de strings verticalmente, incrementando $Y$ por `spaceMm` para cada linha.
- **`line(x1Mm, y1Mm, x2Mm, y2Mm, options)`**: Desenha uma linha entre dois pontos.
- **`drawRect(xMm, yMm, wMm, hMm, options)`**: Desenha um retângulo, ajustando a conversão de coordenada inferior esquerda.

### 4. Testes Unitários e Funcionais com Japa
Todos os serviços geradores de PDF devem ser testados de forma automatizada no Japa.
- **Isolamento:** Os testes de PDF devem rodar no nível de serviço, sem boot de HTTP, banco de dados ou requisições de rede.
- **Validação:** Assegure que os bytes gerados correspondam a um PDF válido (verifique se o cabeçalho começa com `%PDF-`) e que o tamanho do buffer gerado seja aceitável.
- **Controle de Páginas:** Valide que o carregamento do template mantém o número de páginas inalterado e que a adição de novos elementos não corrompe a estrutura do documento.

## Exemplos

### Implementação Base do PdfEditService
```typescript
import { PDFDocument, StandardFonts, rgb, type PDFPage, type PDFFont } from 'pdf-lib'

const MM_TO_PT = 72 / 25.4

export interface TextOptions {
  size?: number
  align?: 'L' | 'C' | 'R'
  color?: [number, number, number]
  font?: PDFFont
  bold?: boolean
}

export default class PdfEditService {
  private doc!: PDFDocument
  private helvetica!: PDFFont
  private helveticaBold!: PDFFont
  private currentPage!: PDFPage

  private constructor() {}

  static async create(width = 595.28, height = 841.89): Promise<PdfEditService> {
    const instance = new PdfEditService()
    instance.doc = await PDFDocument.create()
    await instance.embedFonts()
    instance.currentPage = instance.doc.addPage([width, height])
    return instance
  }

  static async load(bytes: Uint8Array | ArrayBuffer): Promise<PdfEditService> {
    const instance = new PdfEditService()
    instance.doc = await PDFDocument.load(bytes)
    await instance.embedFonts()
    instance.currentPage = instance.doc.getPage(0)
    return instance
  }

  private async embedFonts(): Promise<void> {
    this.helvetica = await this.doc.embedFont(StandardFonts.Helvetica)
    this.helveticaBold = await this.doc.embedFont(StandardFonts.HelveticaBold)
  }

  text(xMm: number, yMm: number, value: string, options: TextOptions = {}): this {
    const size = options.size ?? 8
    const font = options.font ?? (options.bold ? this.helveticaBold : this.helvetica)
    const [r, g, b] = options.color ?? [0, 0, 0]
    const str = value ?? ''

    const xPt = xMm * MM_TO_PT
    const yPt = this.currentPage.getHeight() - yMm * MM_TO_PT - size

    let drawX = xPt
    if (options.align === 'C' || options.align === 'R') {
      const w = font.widthOfTextAtSize(str, size)
      drawX = options.align === 'C' ? xPt - w / 2 : xPt - w
    }

    this.currentPage.drawText(str, { x: drawX, y: yPt, size, font, color: rgb(r, g, b) })
    return this
  }

  async output(): Promise<Uint8Array> {
    return this.doc.save()
  }
}
```

### Exemplo de Teste Japa para o Serviço
```typescript
import { test } from '@japa/runner'
import PdfEditService from '#services/pdf/pdf_edit_service'

test.group('Pdf Edit Service', () => {
  function isPdf(bytes: Uint8Array): boolean {
    return Buffer.from(bytes.subarray(0, 5)).toString('latin1') === '%PDF-'
  }

  test('create + overlay text produces a valid PDF', async ({ assert }) => {
    const pdf = await PdfEditService.create()
    pdf.text(20, 20, 'Test Heading', { size: 12, bold: true })
    
    const bytes = await pdf.output()
    assert.isTrue(isPdf(bytes))
    assert.isAbove(bytes.length, 500)
  })
})
```

## Restrições
- **Não insira valores de coordenadas diretamente em pontos (`pt`) na lógica de negócio/sobreposição.** Mantenha todos os parâmetros em milímetros (`mm`) e faça a conversão dinamicamente no serviço.
- **Não utilize métodos síncronos de geração/carregamento** que possam bloquear a thread de execução do Node.js. O embutimento de fontes e carregamento de bytes devem ser assíncronos.
- **Não implemente cálculos de desenho de diagramas elétricos complexos** dentro do `PdfEditService`. Crie serviços de diagramas separados que chamem os métodos primitivos do `PdfEditService`.
- **Não utilize fontes externas personalizadas (TTF/OTF)** sem real necessidade do negócio. Utilize as fontes padrão (`StandardFonts`) da biblioteca para otimizar tamanho e performance.
