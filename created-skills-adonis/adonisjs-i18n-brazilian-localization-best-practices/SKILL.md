---
name: adonisjs-i18n-brazilian-localization-best-practices
description: Use when implementing, configuring, translating, or debugging internationalization (i18n) and localization features in AdonisJS v6, configuring translation files for Brazilian Portuguese (pt-BR), localizing VineJS validator error messages, or formatting dates/currencies according to Brazilian standards (pt-BR). Triggers on configurations of @adonisjs/i18n, translations in resources/lang/pt, custom validation messages for VineJS, and formatting utilities for pt-BR.
author: Johnattas Conrady Gomes Santana
---
# Melhores Práticas de i18n e Localização Brasileira (pt-BR) no AdonisJS v6

## Objetivo
Fornecer uma abordagem clara, unificada e padronizada para configurar a internacionalização (i18n) e localizar aplicações backend AdonisJS v6 para o português brasileiro (pt-BR). Isso inclui a configuração adequada do pacote, a estrutura dos arquivos de tradução, a tradução automatizada de validações do VineJS e helpers padronizados para formatação de moeda (BRL) e datas.

## Instruções

### 1. Instalação e Configuração do Pacote
Para instalar o pacote oficial de i18n no AdonisJS v6, execute:
```bash
node ace add @adonisjs/i18n
```
Este comando instala o `@adonisjs/i18n`, registra o provider no arquivo `adonisrc.ts` e cria o arquivo de configuração `config/i18n.ts`.

Certifique-se de que o arquivo `config/i18n.ts` esteja configurado com `pt-BR` como o locale padrão e utilize carregadores de sistema de arquivos local:
```typescript
import { defineConfig, formatters, loaders } from '@adonisjs/i18n'

const i18nConfig = defineConfig({
  defaultLocale: 'pt-BR',
  formatter: formatters.icu(),
  supportedLocales: ['pt-BR', 'en'],
  loaders: [
    loaders.fs({
      location: './resources/lang'
    })
  ]
})

export default i18nConfig
```

### 2. Estrutura dos Arquivos de Tradução
Mantenha as traduções estruturadas de forma limpa dentro de `resources/lang/pt-BR/` (ou `resources/lang/pt/` dependendo dos seus requisitos, mas `pt-BR` é preferido para especificidade brasileira). Use arquivos YAML ou JSON:

Exemplo de estrutura:
* `resources/lang/pt-BR/messages.json`
```json
{
  "shared": {
    "welcome": "Bem-vindo ao Engeapp, {name}!",
    "error_occurred": "Ocorreu um erro inesperado. Tente novamente mais tarde."
  }
}
```

* `resources/lang/pt-BR/validator.json` — as chaves das mensagens do VineJS são **planas** (nomes das regras), sem aninhamento sob `shared`:
```json
{
  "required": "O campo {field} é obrigatório.",
  "email": "O campo {field} deve ser um endereço de e-mail válido.",
  "minLength": "O campo {field} deve ter pelo menos {min} caracteres."
}
```

### 3. Localização de Validadores VineJS
Não escreva mensagens de erro de validação diretamente nos validadores (hardcoded). Em vez disso, integre a validação do VineJS com a instância de `i18n` dinâmica vinculada à requisição.

#### Tradução baseada na Requisição (Request-bound)
Dentro dos controllers, obtenha a instância de `i18n` do HttpContext e passe-a como um `messagesProvider` ao executar as validações:
```typescript
import { loginValidator } from '#validators/auth'
import { HttpContext } from '@adonisjs/core/http'

export default class AuthController {
  async login({ request, response, i18n }: HttpContext) {
    // Valida a requisição usando o messagesProvider específico do i18n da requisição
    const payload = await request.validateUsing(loginValidator, {
      messagesProvider: i18n.createVineMessagesProvider()
    })
    
    // Prossiga com a lógica de login
  }
}
```

#### Configuração de Mensagens Globais do VineJS
Para configurar as traduções em `resources/lang/pt-BR/validator.json` para serem usadas automaticamente pelo `@adonisjs/i18n` no VineJS, defina as chaves usando os nomes das regras do VineJS.

Exemplo de configuração para `validator.json`:
```json
{
  "database.unique": "O {field} informado já está cadastrado no sistema.",
  "string": "O campo {field} precisa ser um texto válido.",
  "email": "Informe um e-mail válido no campo {field}.",
  "required": "O campo {field} é obrigatório.",
  "minLength": "O campo {field} deve conter no mínimo {min} caracteres."
}
```

### 4. Detecção Dinâmica de Locale via Middleware
Para detectar automaticamente o locale do cliente (a partir de cookies, sessão ou do cabeçalho `Accept-Language`), rode `node ace add @adonisjs/i18n`. O passo de configuração **cria um arquivo de middleware local** em `app/middleware/detect_user_locale_middleware.ts` (mesmo padrão do `initialize_bouncer_middleware.ts` já presente no projeto) e o registra em `start/kernel.ts`. **Não** existe um subpath importável `@adonisjs/i18n/initialize_middleware` — importar esse caminho falha na resolução. Registre o arquivo local gerado:
```typescript
// start/kernel.ts
router.use([
  () => import('#middleware/detect_user_locale_middleware')
])
```
Este middleware analisa os cabeçalhos de requisição e define o locale ativo na instância de `HttpContext.i18n` para a requisição atual. Confira em `start/kernel.ts` se o `add` já o incluiu na pilha; caso contrário, adicione a linha acima manualmente.

### 5. Formatação de Datas e Moeda (BRL / pt-BR)
Use as funções de formatação da instância de `i18n` para produzir consistentemente datas e moedas no formato brasileiro (BRL / pt-BR) no backend. O front é uma SPA Vue pura (sem Edge), então o backend formata os valores e os entrega já formatados via API (consumidos no front através de stores `@maxvue/max-pinia`), ou o front formata no cliente com `Intl.NumberFormat`/`Intl.DateTimeFormat` em `pt-BR`.

#### Backend (TypeScript)
```typescript
import { HttpContext } from '@adonisjs/core/http'

export default class ReportController {
  async index({ i18n }: HttpContext) {
    const value = 1500.50
    const today = new Date()
    
    const formattedCurrency = i18n.formatCurrency(value, { currency: 'BRL' }) 
    // Retorna: R$ 1.500,50
    
    const formattedDate = i18n.formatDate(today, { dateStyle: 'short' })
    // Retorna: 25/06/2026
  }
}
```

#### Front (Vue SPA, formatação no cliente)
```ts
const moeda = new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' })
const data = new Intl.DateTimeFormat('pt-BR', { dateStyle: 'medium' })

moeda.format(transaction.amount) // R$ 1.500,50
data.format(new Date(transaction.createdAt))
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NÃO use APIs de localização legadas do AdonisJS v5** (como o provider legado `Antl`). Use as APIs padrão do `@adonisjs/i18n` v2 (para Adonis v6).
* **NÃO escreva diretamente strings de tradução em pt-BR (hardcoded)** dentro de validadores VineJS ou controllers. Todas as mensagens de tradução devem estar localizadas em `resources/lang/pt-BR/`.
* **NÃO ignore a Injeção de Locale no nível da Requisição**. Não importe um singleton global de `i18n` diretamente ao validar dados da requisição, pois isso quebrará o suporte a múltiplos inquilinos (multitenancy) ou múltiplos idiomas. Use sempre a instância de `i18n` do `HttpContext` para garantir que o idioma de preferência do usuário seja respeitado.
* **Sempre especifique a moeda BRL explicitamente** ao chamar `i18n.formatCurrency()`. O comportamento padrão pode reverter para USD se não for informado explicitamente.
