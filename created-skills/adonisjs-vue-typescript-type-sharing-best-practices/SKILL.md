---
name: adonisjs-vue-typescript-type-sharing-best-practices
description: Use when configuring TypeScript, sharing models or validation types between AdonisJS v6 backend and Vue 3 frontend, or defining APIs and generated.d.ts in Node.js. Triggers on types integration, sharing interfaces, and VineJS schemas inferring.
---

# Melhores Práticas de Compartilhamento de Tipos TypeScript entre AdonisJS e Vue 3

## Objetivo
Estabelecer uma integração robusta e segura de tipos (type-safe) de ponta a ponta entre o backend AdonisJS v6 (modelos Lucid ORM, validadores VineJS) e o frontend Vue 3 dentro de um repositório unificado ou workspace integrado. Isso reduz a definição de interfaces duplicadas manuais, evita inconsistências em tempo de compilação e previne falhas de build do Vite causadas pela importação de bibliotecas exclusivas do Node no código do frontend.

## Instruções

### 1. Importando Tipos de Modelos Lucid ORM com Segurança
Para evitar erros de compilação no Vite devido a pacotes de backend do Node.js (ex: `@adonisjs/lucid/orm` ou `@adonisjs/core/helpers`) sendo avaliados no cliente, sempre importe modelos usando o modificador `type`:

* **NÃO** importe classes diretamente para tipar variáveis no lado do cliente:
  ```typescript
  // INCORRETO: Isso carrega a classe de execução e suas dependências de Node
  import User from '#models/user'
  const currentUser: User = reactive({...})
  ```

* **SIM**, use imports apenas de tipo (`import type`):
  ```typescript
  // CORRETO: Importa apenas a interface de tipo estática em tempo de compilação
  import type User from '#models/user'
  const currentUser = ref<User | null>(null)
  ```

* Se você precisar apenas das propriedades brutas (atributos) do registro de banco de dados, em vez dos métodos completos do modelo, você pode extrair as propriedades usando utilitários do Lucid:
  ```typescript
  import type { ModelAttributes } from '@adonisjs/lucid/types/model'
  import type User from '#models/user'
  
  export type UserAttributes = ModelAttributes<User>
  ```

### 2. Inferindo e Compartilhando Tipos de Validação do VineJS
Os esquemas de validação definidos no backend com VineJS servem como a única fonte de verdade para a estrutura dos payloads. Exponha esses esquemas como tipos para que o frontend possa validar os campos dos formulários e os payloads do Axios.

* **Backend: Definição e Inferência de Tipo**
  Defina e compile o validador em seu arquivo de validadores, e exporte seu tipo inferido usando `Infer`:
  ```typescript
  import vine from '@vinejs/vine'
  import { Infer } from '@vinejs/vine/types'

  // Define o esquema
  export const saveValidator = vine.compile(
    vine.object({
      company_name: vine.string().maxLength(255),
      is_active: vine.boolean().optional(),
    })
  )

  // Exporta o tipo inferido
  export type SavePayload = Infer<typeof saveValidator>
  ```

* **Expondo o tipo para o frontend**
  O alias `#controllers/*` (e demais subpaths `#...`) vem do `package.json` do backend Adonis e **não resolve** no Vite da SPA front, que é um projeto/build separado. Não importe tipos diretamente de `#controllers/...` no front. Em vez disso, exporte o tipo inferido a partir de um módulo de tipos compartilhado que ambos os lados consigam resolver — por exemplo um arquivo em `resources/Types/` (incluído no `tsconfig.frontend.json`) ou um pacote/path alias de tipos compartilhados configurado explicitamente no Vite:
  ```typescript
  // resources/Types/api_payloads.ts (compartilhado)
  import type { Infer } from '@vinejs/vine/types'
  import type { saveValidator } from '../../app/validators/company.js'

  export type SavePayload = Infer<typeof saveValidator>
  ```

* **Frontend: Importando e vinculando a formulários**
  Importe o tipo a partir do módulo compartilhado (não de `#controllers/*`) para tipar estados reativos em componentes Vue:
  ```typescript
  import type { SavePayload } from '~/resources/Types/api_payloads'

  const formData = ref<SavePayload>({
    company_name: '',
    is_active: true,
  })
  ```

### 3. Organizando Tipos Globais em `generated.d.ts`
Quando a geração automática de tipos não estiver ativa, utilize o arquivo `resources/Types/generated.d.ts` como repositório para modelos globais de frontend e interfaces compartilhadas de domínio.

* Estenda o escopo global usando `declare global` para evitar isolamento de módulo local.
* Declare propriedades opcionais de forma clara (`?` ou `| null`) para espelhar colunas anuláveis do banco de dados.
* Termine o arquivo com `export {}` para garantir que o compilador o trate como uma declaração de módulo.
  ```typescript
  declare global {
      interface CalendarEvent {
          id: string
          title: string | null
          start_at: string | null
          end_at: string | null
      }
  }
  export {}
  ```
* Certifique-se de que o `tsconfig.frontend.json` inclua o padrão `"./resources/Types/**/*.d.ts"` na sua seção de `include`.

### 4. Tipando o Fluxo de Dados de Página (MaxPinia)
No padrão do projeto, **todo GET/save de dados de página passa por uma store `@maxvue/max-pinia`** — não por wrappers axios manuais. O ganho de tipagem aqui é tipar o `state` da store com o tipo do model/atributos e o payload de save com o tipo inferido do VineJS, de modo que o auto-save (debounced) e o GET inicial sejam type-safe de ponta a ponta. As rotas são caminhos string `/api/...` resolvidos por `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use` (não há `route()`/Ziggy).

```typescript
import type { SavePayload } from '~/resources/Types/api_payloads'
import type { ModelAttributes } from '@adonisjs/lucid/types/model'
import type SolarCompany from '#models/solar_company'

// O state da store é tipado pelos atributos do model; o save reaproveita o SavePayload do VineJS.
type CompanyState = ModelAttributes<SolarCompany>

// A store @maxvue/max-pinia faz o GET inicial e o auto-save por '/api/company'.
// O componente apenas muta o state tipado e o MaxPinia persiste automaticamente.
const company = useCompanyStore() // state: CompanyState; save aceita SavePayload
```

> **Endpoints REST avulsos.** Apenas para um endpoint fora do fluxo de store (raro), tipe a resposta com o envelope correto: GET retorna `{ data: ... }` e save retorna `{ success: true }` — não o model cru. Mesmo nesses casos, prefira o fluxo de store para dados de página (ver `adonisjs-maxpinia-endpoint-patterns-best-practices`).

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **NUNCA** importe modelos Lucid sem o modificador `type` (ex: `import type User`) dentro de componentes Vue ou composables do frontend. Fazer isso resultará em erros de `Unable to resolve dependency` ou falhas de empacotamento no Vite.
* **NUNCA** instancie classes de backend diretamente dentro de scripts do frontend.
* **NUNCA** duplique a estrutura de campos manualmente entre o modelo do banco de dados e a interface do frontend; reutilize os tipos dos modelos AdonisJS ou a inferência do VineJS sempre que possível.
* Todos os comentários em arquivos de código do projeto TS e Vue devem ser escritos em Português do Brasil (pt-BR).
