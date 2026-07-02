---
name: adonisjs-maxpinia-endpoint-patterns-best-practices
description: Use when creating or reviewing AdonisJS backend endpoints that serve data to Vue 3 frontend stores powered by @maxvue/max-pinia. Every frontend store with isCached=true makes automatic GET and POST requests — the backend endpoints must match the expected patterns. Triggers on creating data endpoints, save endpoints, designing controller response structures, handling auto-save payloads, or debugging why MaxPinia GET/save is not working correctly.
---

# Padrões de Endpoints AdonisJS para MaxPinia

## Objetivo
O plugin `@maxvue/max-pinia` no frontend realiza automaticamente:
1. **GET automático** ao montar a store — busca dados frescos do servidor.
2. **POST automático com debounce (300ms)** — salva quando `data` da store muda.

Os endpoints AdonisJS precisam seguir padrões específicos para funcionar corretamente com esses comportamentos automáticos. Esta skill documenta esses padrões.

---

## Fluxo MaxPinia ↔ AdonisJS

```
Frontend Store (isCached=true)
  options.get.route  → GET /api/recurso/data  → Controller.data()  → { ...campos }   (vira store.data verbatim)
  options.save       → POST /api/recurso/save → Controller.save()  → { success: true }
                       body do POST = { ...store.data } (campos na raiz, sem wrapper "data")
```

---

## Instruções

### 1. Padrão de Endpoint GET
O MaxPinia faz GET para `options.get.route` ao montar a store. **Atenção:** o plugin faz `store.data = response.data`, ou seja, `store.data` recebe o **corpo JSON inteiro da resposta, verbatim**. Portanto, se você envolver os campos em `{ data: {...} }`, os campos ficam em `store.data.data` (e não em `store.data.company_name`). Para que o componente leia `store.data.company_name` diretamente, retorne os **campos na raiz** da resposta. O endpoint deve:
- Retornar os campos do estado diretamente na raiz do objeto JSON (sem wrapper `data`), pois `store.data` = corpo inteiro.
- Manter a mesma forma no GET e no POST (campos na raiz em ambos).
- Usar autenticação e escopo de tenant adequados.

```typescript
// GET /api/brand-positioning/data → options.get.route: '/api/brand-positioning/data'
export default class BrandPositioningController {
  async data({ auth }: HttpContext) {
    const company = await SolarCompany.query()
      .where('id', auth.user!.solarCompanyId)
      .firstOrFail()

    // Campos na raiz → store.data = { company_name, mission, ... }
    return {
      company_name: company.name,
      mission: company.mission,
      values: company.values,
      content_pillars: company.contentPillars ?? [],
    }
  }
}
```

### 2. Padrão de Endpoint POST (Auto-Save)
O MaxPinia faz POST para `options.save` sempre que `data` muda (debounce 300ms). **Atenção ao formato do corpo:** por padrão o plugin envia `{ ...store.data }` — os campos da store espalhados na **raiz** do corpo da requisição (sem wrapper `data`). Em `saveInServer`, o corpo é `const data_send = getPostData() ?? { ...store.data }`, postado verbatim como body do axios. Só existe um wrapper diferente se a store definir explicitamente `options.save.data`/`getSaveData`. O endpoint deve:
- Ler/validar os campos **na raiz** do corpo (ex: `request.input('company_name')`), não sob uma chave `data`.
- Validar o payload com VineJS.
- Retornar `{ success: true }` ou os dados atualizados.

```typescript
// POST /api/brand-positioning/save → options.save: '/api/brand-positioning/save'
// Corpo recebido = { company_name, mission, values, content_pillars } (campos na raiz)
const saveValidator = vine.compile(
  vine.object({
    company_name: vine.string().nullable().optional(),
    mission: vine.string().nullable().optional(),
    values: vine.string().nullable().optional(),
    content_pillars: vine.array(vine.string()).optional(),
  })
)

export default class BrandPositioningController {
  async save({ request, auth }: HttpContext) {
    const data = await request.validateUsing(saveValidator)

    const company = await SolarCompany.query()
      .where('id', auth.user!.solarCompanyId)
      .firstOrFail()

    await company.merge({
      name: data.company_name ?? company.name,
      mission: data.mission ?? company.mission,
      values: data.values ?? company.values,
      contentPillars: data.content_pillars ?? company.contentPillars,
    }).save()

    return { success: true }
  }
}
```

### 3. Rota com Parâmetros Dinâmicos
Quando a store usa `options.get.data` para parâmetros dinâmicos:

```typescript
// Frontend store
const options = computed(() => ({
  get: {
    route: '/api/projects/data',
    data: { project_id: projectId.value },
  },
}))

// Backend: GET /api/projects/data?project_id=123
async data({ request, auth }: HttpContext) {
  const { project_id } = await request.validateUsing(
    vine.compile(vine.object({ project_id: vine.number() }))
  )

  const project = await Project.query()
    .where('id', project_id)
    .where('solar_company_id', auth.user!.solarCompanyId)
    .firstOrFail()

  // Campos na raiz → store.data = { id, name, status }
  return {
    id: project.id,
    name: project.name,
    status: project.status,
  }
}
```

### 4. Convenção de Rotas
A store referencia o endpoint pelo **caminho string** (`/api/modulo/data` e `/api/modulo/save`). **Não existe Ziggy** — os helpers `apiGetRoute`/`apiPostRoute` do `@maxvue/max-use` apenas resolvem caminhos `/api/...`, não rotas nomeadas do Laravel. Padronize os caminhos com o sufixo `/data` (GET) e `/save` (POST):

```typescript
// start/routes/web/brand-positioning.routes.ts
router.group(() => {
  router.get('/data', [BrandPositioningController, 'data'])
  router.post('/save', [BrandPositioningController, 'save'])
}).prefix('/api/brand-positioning').use(middleware.auth())
// → store: get.route '/api/brand-positioning/data', save '/api/brand-positioning/save'
```
O `.as('nome')` continua opcional/útil apenas para geração de URL server-side com `router.makeUrl()` (emails, redirects); não é exigido pelo frontend.

### 5. Stores sem Auto-Save (GET-only)
Para stores somente de leitura, omita `options.save`:

```typescript
// Frontend store
const options = computed(() => ({
  get: { route: '/api/user/profile' },
  key: 'user-profile',
  // sem 'save' → sem auto-save
}))

// Backend: retorna apenas o objeto de dados
async profile({ auth }: HttpContext) {
  const user = auth.user!
  // Campos na raiz → store.data = { id, name, email }
  return {
    id: user.id,
    name: user.fullName,
    email: user.email,
  }
}
```

---

## Checklist ao Criar Endpoints para MaxPinia

- [ ] GET retorna os campos na raiz (`{ ...campos }`), pois `store.data = response.data` (corpo inteiro)
- [ ] POST recebe os campos na raiz do body (`{ ...store.data }`), sem wrapper `data` (salvo se a store definir `options.save.data`/`getSaveData`)
- [ ] A store referencia os caminhos string `/api/modulo/data` e `/api/modulo/save` (sem rota nomeada Ziggy)
- [ ] Ambas passam pelo middleware de autenticação `middleware.auth()`
- [ ] O escopo de tenant/empresa está aplicado nas queries
- [ ] POST valida com VineJS antes de persistir

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Lembre-se que `store.data = response.data`** (corpo inteiro) — para listas, retorne o array/objeto na forma exata que o componente vai consumir em `store.data`; não adicione wrappers `{ data: ... }` inesperados que empurrem os campos para `store.data.data`.
- **Valide sempre** o payload do POST/save com VineJS antes de tocar no banco de dados.
- **Aplique escopo de tenant** em toda query — nunca retorne dados de outras empresas/usuários.
- **Não quebre o debounce** retornando erros 4xx em salvamentos parciais — prefira salvar o que é válido e ignorar campos inválidos silenciosamente, ou retornar 422 com mensagens claras para o frontend tratar.
