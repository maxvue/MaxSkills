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
  options.get.route  → GET /api/recurso/data  → Controller.data()  → { data: {...} }
  options.save       → POST /api/recurso/save → Controller.save()  → { success: true }
```

---

## Instruções

### 1. Padrão de Endpoint GET
O MaxPinia faz GET para `options.get.route` ao montar a store. O endpoint deve:
- Retornar um objeto JSON com `data` como chave raiz.
- Enviar os dados completos do estado — o MaxPinia popula `store.data` com o valor retornado.
- Usar autenticação e escopo de tenant adequados.

```typescript
// GET /api/brand-positioning/data → options.get.route: '/api/brand-positioning/data'
export default class BrandPositioningController {
  async data({ auth }: HttpContext) {
    const company = await SolarCompany.query()
      .where('id', auth.user!.solarCompanyId)
      .firstOrFail()

    return {
      data: {
        company_name: company.name,
        mission: company.mission,
        values: company.values,
        content_pillars: company.contentPillars ?? [],
      },
    }
  }
}
```

### 2. Padrão de Endpoint POST (Auto-Save)
O MaxPinia faz POST para `options.save` com o payload `{ data: store.data }` sempre que `data` muda (debounce 300ms). O endpoint deve:
- Receber o payload em `request.input('data')` ou como corpo da requisição.
- Validar o payload com VineJS.
- Retornar `{ success: true }` ou os dados atualizados.

```typescript
// POST /api/brand-positioning/save → options.save: '/api/brand-positioning/save'
const saveValidator = vine.compile(
  vine.object({
    data: vine.object({
      company_name: vine.string().nullable().optional(),
      mission: vine.string().nullable().optional(),
      values: vine.string().nullable().optional(),
      content_pillars: vine.array(vine.string()).optional(),
    }),
  })
)

export default class BrandPositioningController {
  async save({ request, auth }: HttpContext) {
    const { data } = await request.validateUsing(saveValidator)

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

  return {
    data: {
      id: project.id,
      name: project.name,
      status: project.status,
    },
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
  return {
    data: {
      id: user.id,
      name: user.fullName,
      email: user.email,
    },
  }
}
```

---

## Checklist ao Criar Endpoints para MaxPinia

- [ ] GET retorna `{ data: { ... } }` como objeto raiz
- [ ] POST recebe `{ data: { ... } }` no body (ou parâmetros individuais validados)
- [ ] A store referencia os caminhos string `/api/modulo/data` e `/api/modulo/save` (sem rota nomeada Ziggy)
- [ ] Ambas passam pelo middleware de autenticação `middleware.auth()`
- [ ] O escopo de tenant/empresa está aplicado nas queries
- [ ] POST valida com VineJS antes de persistir

---

## Restrições
- **Nunca retorne arrays diretamente** no GET do MaxPinia — sempre envolva em `{ data: [...] }` para manter consistência com o padrão da store.
- **Valide sempre** o payload do POST/save com VineJS antes de tocar no banco de dados.
- **Aplique escopo de tenant** em toda query — nunca retorne dados de outras empresas/usuários.
- **Não quebre o debounce** retornando erros 4xx em salvamentos parciais — prefira salvar o que é válido e ignorar campos inválidos silenciosamente, ou retornar 422 com mensagens claras para o frontend tratar.
