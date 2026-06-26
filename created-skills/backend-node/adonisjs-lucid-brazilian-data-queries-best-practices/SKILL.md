---
name: adonisjs-lucid-brazilian-data-queries-best-practices
description: Use when writing, optimizing, or reviewing AdonisJS database queries using Lucid ORM that involve Brazilian-specific data formats, patterns, or regulations. Triggers on queries, models, or hooks handling CPFs, CNPJs, CEPs, Brazilian phone numbers, currency formatting (BRL/Real), and Brasília timezone (UTC-3) conversions.
---

# Melhores Práticas para Consultas e Dados Brasileiros no AdonisJS Lucid ORM

## Objetivo
Estabelecer padrões e diretrizes estritas para modelagem, sanitização, consulta e formatação de dados específicos do contexto brasileiro (CPF, CNPJ, CEP, telefones, valores monetários em BRL e fuso horário de Brasília UTC-3) em aplicações AdonisJS v6 utilizando o Lucid ORM.

## Instruções

### 1. Normalização e Consulta de CPF e CNPJ
* **Armazenamento no Banco**: Sempre armazene CPFs e CNPJs como strings limpas (apenas números) para garantir a eficiência de índices e consistência em buscas.
* **Gancho de Sanitização do Modelo**: Use `@beforeSave()` ou `@beforeCreate()` para remover caracteres de formatação antes de persistir no banco de dados.
* **Query Scopes no Lucid**: Defina escopos de consulta (Query Scopes) que permitam buscar dados passando tanto a string limpa quanto formatada.
* **Getters de Serialização**: Formate os valores de volta para a representação padrão brasileira ao serializar os dados.

```typescript
import { BaseModel, beforeSave, column } from '@adonisjs/lucid/orm'
import { scope } from '@adonisjs/lucid/orm'

export default class Customer extends BaseModel {
  static table = 'customers'

  @column()
  declare cpf: string // Armazenado como "12345678901"

  @column()
  declare cnpj: string // Armazenado como "12345678000100"

  // Formatação automática na serialização
  @column({
    consume: (value: string) => value ? value.replace(/^(\d{3})(\d{3})(\d{3})(\d{2})$/, '$1.$2.$3-$4') : value
  })
  declare cpfFormatted: string

  @column({
    consume: (value: string) => value ? value.replace(/^(\d{2})(\d{3})(\d{3})(\d{4})(\d{2})$/, '$1.$2.$3/$4-$5') : value
  })
  declare cnpjFormatted: string

  @beforeSave()
  static sanitizeDocuments(customer: Customer) {
    if (customer.cpf) customer.cpf = customer.cpf.replace(/\D/g, '')
    if (customer.cnpj) customer.cnpj = customer.cnpj.replace(/\D/g, '')
  }

  // Scopes para pesquisar por valores limpos ou formatados
  public static filterCpf = scope((query, cpf: string) => {
    const clean = cpf.replace(/\D/g, '')
    query.where('cpf', clean)
  })

  public static filterCnpj = scope((query, cnpj: string) => {
    const clean = cnpj.replace(/\D/g, '')
    query.where('cnpj', clean)
  })
}
```

### 2. Normalização de CEP e Telefone
* **CEP**: Armazene CEPs como strings de exatamente 8 dígitos. Use `@beforeSave()` para limpar a string e um callback de consumo ou getter para formatar como `XXXXX-XXX` na serialização.
* **Telefone**: Armazene números de celular brasileiros com o DDD (código de área) como uma string limpa de 11 dígitos (ex: `11999998888`), ou 10 dígitos para telefones fixos. Para integrações com APIs como WhatsApp, adicione o prefixo do país `55` se estiver ausente.

```typescript
export default class Address extends BaseModel {
  @column()
  declare cep: string

  @column()
  declare phone: string

  @beforeSave()
  static sanitizeData(address: Address) {
    if (address.cep) address.cep = address.cep.replace(/\D/g, '')
    if (address.phone) {
      // Mantém apenas dígitos, adicionando 55 se o código do país estiver ausente e for um número completo
      let cleaned = address.phone.replace(/\D/g, '')
      if (cleaned.length === 11 || cleaned.length === 10) {
        cleaned = `55${cleaned}`
      }
      address.phone = cleaned
    }
  }
}
```

### 3. Tratamento de Valores Monetários (BRL / Real)
* **Padrão em Centavos**: Sempre armazene valores monetários como números inteiros representando centavos (`100` = `R$ 1,00`) no banco de dados para evitar erros de precisão do ponto flutuante IEEE 754.
* **Conversão Automática**: Converta de decimal para centavos na escrita do banco, e de volta para decimal na leitura utilizando as opções `prepare` e `consume` da coluna.
* **Formatação**: Disponibilize um campo calculado (`@computed`) com a representação em BRL formatada.

```typescript
import { BaseModel, column, computed } from '@adonisjs/lucid/orm'

export default class Transaction extends BaseModel {
  @column({
    prepare: (value: number) => value ? Math.round(value * 100) : value,
    consume: (value: number) => value ? value / 100 : value
  })
  declare amount: number // Representado como float em tempo de execução, armazenado como centavos no banco

  @computed()
  get amountBrl() {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(this.amount)
  }
}
```

### 4. Fuso Horário de Brasília (UTC-3) e Consultas com Datas
* **Armazenamento em UTC**: Mantenha o fuso horário do banco de dados em UTC. Timestamps devem ser gravados em UTC.
* **Manipulação com Luxon**: Use a biblioteca `DateTime` do Luxon para interpretar entradas de data especificando explicitamente o fuso `America/Sao_Paulo`.
* **Consultas por Intervalo de Dias**: Ao consultar registros filtrando por uma data local do usuário (ex: "pedidos criados em 2026-06-23" no Brasil), calcule o início e o fim desse dia no fuso horário de Brasília primeiro, e converta esses limites para UTC antes de executar a consulta.

```typescript
import { DateTime } from 'luxon'
import Order from '#models/order'

// Busca pedidos criados em uma data local específica de Brasília
export async function getOrdersByLocalDate(dateStr: string) {
  // Interpreta a string de data no fuso do Brasil
  const localDate = DateTime.fromISO(dateStr, { zone: 'America/Sao_Paulo' })
  
  // Obtém o início e o fim do dia local e converte para UTC
  const startUtc = localDate.startOf('day').toUTC()
  const endUtc = localDate.endOf('day').toUTC()

  return await Order.query()
    .whereBetween('createdAt', [
      startUtc.toSQL(),
      endUtc.toSQL()
    ])
}
```

## Restrições
* **Nunca armazene documentos formatados**: Não salve pontos, traços ou barras nas colunas de banco de dados para CPF, CNPJ ou CEP.
* **Não utilize tipos de ponto flutuante para dinheiro**: Evite tipos de banco de dados como `float` ou `double` para valores monetários; utilize sempre `integer` representando os valores em centavos.
* **Nunca compare datas locais usando strings brutas**: Evite buscar registros utilizando `where('created_at', dateStr)` diretamente se a data representar um dia local, pois o desvio do fuso horário trará resultados errados. Sempre converta as fronteiras explicitamente para UTC.
* **Sem offsets de fuso horário fixados (hardcoded)**: Nunca aplique offsets manuais de tempo (ex: subtrair ou somar horas via SQL bruto como `- INTERVAL '3 hours'`), pois isso causará falhas no período do horário de verão. Sempre use a biblioteca Luxon com o fuso `America/Sao_Paulo` para as conversões.
