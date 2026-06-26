export const meta = {
  name: 'fix-engeapp-skills-leva1',
  description: 'Corrige in-place as 66 skills high+medium (violações de escopo, erros de API, conformidade MaxPinia) da migração EngeApp→Adonis',
  phases: [
    { title: 'Corrigir', detail: '66 agentes editam um SKILL.md cada conforme seus findings' },
    { title: 'Resumo', detail: 'consolida o que mudou' },
  ],
}

const SCOPE_PATH = '/tmp/claude-1000/-home-johnattas-GitHub-Skills/ccbe1006-08d5-4df9-9c60-b4a329886e06/scratchpad/SCOPE.md'

const items = JSON.parse(`__ITEMS__`)

const FIX_SCHEMA = {
  type: 'object',
  properties: {
    skill: { type: 'string' },
    edited: { type: 'boolean', description: 'true se o arquivo foi modificado' },
    changes: { type: 'array', items: { type: 'string' }, description: 'lista curta das correções aplicadas' },
    skipped: { type: 'array', items: { type: 'string' }, description: 'findings que NÃO foram corrigidos e por quê' },
  },
  required: ['skill', 'edited', 'changes']
}

phase('Corrigir')
const results = await parallel(items.map((it, i) => () =>
  agent(
    `Você corrige UMA skill da migração EngeApp (Laravel → AdonisJS/Node).\n\n` +
    `1. Leia o contrato de escopo: ${SCOPE_PATH}\n` +
    `2. Leia os findings desta skill: ${it.findings}\n` +
    `3. Leia o arquivo da skill: ${it.skill}\n\n` +
    `Decisões transversais JÁ TOMADAS (aplique sem perguntar):\n` +
    `- SGBD-alvo = PostgreSQL. JSONB/GIN/pgvector/timestamptz estão CORRETOS. Sintaxe MySQL (ex.: FIELD()) ou assunções MariaDB são ERRO — corrija para Postgres.\n` +
    `- Realtime = AdonisJS Transmit (SSE). Remova Pusher/Soketi/Reverb/Laravel Echo.\n` +
    `- AI = Vercel AI SDK. Roteie SDKs diretos (openai, @google/genai) via Vercel AI SDK quando for o caso.\n` +
    `- Auth = sessão + cookie (guard web). Remova Bearer/JWT/Sanctum/\`/sanctum/csrf-cookie\` como padrão; OAT só para MCP/M2M.\n` +
    `- TODO GET/save de dados de página passa por store @maxvue/max-pinia. Converta axios.get/post manual e save-por-submit para o fluxo MaxPinia (apiGetRoute/apiPostRoute resolvem caminhos string /api/...; sem rotas nomeadas estilo Ziggy).\n` +
    `- Sem Inertia/Ziggy. Sem Tailwind — use UnoCSS attributify (presetMaxUno) e componentes Max.\n` +
    `- Domínio do projeto é fotovoltaico/solar (EngeApp). Realinhe exemplos vazados de "SocialMediaApp/Instagram/MarketingAgency" quando forem o exemplo principal da skill — mas NÃO descaracterize skills cujo tema legítimo é uma integração social específica (ex.: skill de TikTok API continua sobre TikTok).\n\n` +
    `4. EDITE o arquivo ${it.skill} in-place (use Edit/Write) corrigindo TODOS os findings aplicáveis: scope_violations, technical_errors, maxpinia_gaps e description_issues.\n\n` +
    `Regras de edição:\n` +
    `- Preserve o estilo, idioma (PT) e estrutura da skill. Faça edições cirúrgicas, não reescreva o que está correto.\n` +
    `- Para violações de escopo profundas (ex.: skill inteira sobre Pusher/Reverb), reescreva as seções afetadas para o equivalente do stack-alvo (Transmit).\n` +
    `- Se um finding for um falso-positivo (a skill já está correta sob o escopo), registre em "skipped" com o motivo e NÃO altere.\n` +
    `- Verifique que exemplos de código usem APIs reais do Adonis v6/Lucid v6/pacotes @maxvue (não Eloquent/Laravel).\n\n` +
    `Retorne o objeto estruturado com o que mudou.`,
    { label: `${it.severity}:${it.skill.split('/created-skills/')[1].split('/')[1]}`, phase: 'Corrigir', schema: FIX_SCHEMA }
  )
))

const done = (results || []).filter(Boolean)
const edited = done.filter(r => r.edited)
log(`${edited.length}/${items.length} skills editadas`)

phase('Resumo')
const summary = await agent(
  `Consolide o resultado da correção de ${items.length} skills (migração EngeApp→Adonis). Dados:\n` +
  JSON.stringify(done) +
  `\n\nProduza um resumo em Markdown PT: (1) quantas editadas vs puladas; (2) principais classes de correção aplicadas; (3) findings pulados/falsos-positivos notáveis; (4) skills que merecem revisão manual humana.`,
  { label: 'resumo', phase: 'Resumo' }
)

return { total: items.length, edited: edited.length, summary, details: done }
