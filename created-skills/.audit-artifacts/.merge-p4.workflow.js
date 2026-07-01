export const meta = {
  name: 'merge-engeapp-skills-p4',
  description: 'Consolida 5 clusters de skills redundantes (BullMQ, PDF/Puppeteer, simuladores social, ecossistema Max, docs); arquiva as absorvidas em _archived/',
  phases: [
    { title: 'Mesclar', detail: '5 agentes consolidam cada cluster e arquivam fontes' },
    { title: 'Resumo', detail: 'consolida o resultado dos merges' },
  ],
}

const ROOT = '/home/johnattas/GitHub/Skills/created-skills'
const SCOPE_PATH = '/tmp/claude-1000/-home-johnattas-GitHub-Skills/ccbe1006-08d5-4df9-9c60-b4a329886e06/scratchpad/SCOPE.md'
const ARCHIVE = ROOT + '/_archived'

const clusters = [
  {
    id: 'bullmq',
    target: ROOT + '/backend-node/adonisjs-bullmq-best-practices/SKILL.md',
    master: 'adonisjs-bullmq-queue-management-best-practices (config/Worker base — usar como esqueleto)',
    sources: [
      'backend-node/adonisjs-bullmq-queue-management-best-practices',
      'backend-node/adonisjs-bullmq-job-idempotency-deduplication-best-practices',
      'backend-node/adonisjs-bullmq-job-resilience-retries-best-practices',
      'backend-node/adonisjs-bullmq-multi-tenant-job-isolation-best-practices',
    ],
    plan: 'Skill-hub única `adonisjs-bullmq-best-practices`: base de config/Worker da queue-management, depois seções "Idempotência/Deduplicação", "Resiliência/Retries" e "Multi-tenancy/Isolamento" absorvendo as outras três. Description deve cobrir todos os triggers das 4.',
  },
  {
    id: 'pdf-render',
    target: ROOT + '/backend-node/adonisjs-puppeteer-rendering-best-practices/SKILL.md',
    master: 'adonisjs-reporting-pdf-excel + adonisjs-puppeteer-image-generation',
    sources: [
      'backend-node/adonisjs-reporting-pdf-excel-best-practices',
      'backend-node/adonisjs-puppeteer-image-generation-best-practices',
    ],
    plan: 'Fundir reporting-pdf-excel + puppeteer-image-generation numa `adonisjs-puppeteer-rendering-best-practices` (compartilham Puppeteer+Edge+BullMQ+Drive). Seções: render HTML→PDF, HTML→imagem, planilhas Excel. NÃO tocar `adonisjs-pdf-coordinate-editing` (pdf-lib, fica separada) — apenas cross-linkar.',
  },
  {
    id: 'social-preview',
    target: ROOT + '/front-end-vue/vue-social-post-preview-simulator-best-practices/SKILL.md',
    master: 'nova skill genérica',
    sources: [
      'front-end-vue/vue-facebook-post-preview-simulator-best-practices',
      'front-end-vue/vue-google-business-profile-post-preview-simulator-best-practices',
      'front-end-vue/vue-instagram-feed-grid-simulator-best-practices',
      'front-end-vue/vue-instagram-reels-preview-simulator-best-practices',
      'front-end-vue/vue-instagram-stories-preview-simulator-best-practices',
      'front-end-vue/vue-threads-post-preview-simulator-best-practices',
      'front-end-vue/vue-tiktok-video-preview-simulator-best-practices',
      'front-end-vue/vue-youtube-shorts-preview-simulator-best-practices',
    ],
    plan: 'Consolidar os 8 simuladores numa única `vue-social-post-preview-simulator-best-practices` organizada por VARIANTES de formato: (a) feed/timeline card (Facebook, Threads, Instagram feed-grid, Google Business), (b) vertical 9:16 stories/reels/shorts (Instagram stories+reels, TikTok, YouTube Shorts). Preserve as particularidades visuais de cada rede como subseções/tabela de specs (dimensões, limites de caracteres, elementos de UI). Description ampla cobrindo todas as redes. É front: estilização UnoCSS attributify + MaxComponentsUi, sem Tailwind.',
  },
  {
    id: 'max-front',
    target: ROOT + '/front-end-vue/vue-max-stack-frontend-best-practices/SKILL.md',
    master: 'vue-max-stack-frontend (master, absorve ecosystem)',
    sources: [
      'front-end-vue/vue-max-stack-frontend-best-practices',
      'front-end-vue/vue-max-ecosystem-best-practices',
    ],
    plan: 'vue-max-stack-frontend é o master: absorver o conteúdo único de vue-max-ecosystem que não esteja duplicado. Manter o arquivo do stack-frontend como destino (não criar nome novo). Arquivar só o ecosystem. Atualizar refs cruzadas que apontavam para ecosystem.',
  },
  {
    id: 'docs',
    target: ROOT + '/general/technical-documentation-best-practices/SKILL.md',
    master: 'technical-documentation (master, absorve typescript-documentation)',
    sources: [
      'general/technical-documentation-best-practices',
      'general/typescript-documentation-best-practices',
    ],
    plan: 'technical-documentation é o master (mais ampla: README/ADR/changelog/CONTRIBUTING/doc-API). Absorver o que typescript-documentation tem de único e aderente ao stack (JSDoc/TSDoc/TypeDoc, ADRs) — descartando exemplos de NestJS/React/Angular fora de escopo. Arquivar typescript-documentation e seus references/. Manter destino = technical-documentation.',
  },
]

phase('Mesclar')
const results = await parallel(clusters.map((c) => () =>
  agent(
    `Você consolida um CLUSTER de skills redundantes da migração EngeApp→Adonis. Faça um merge cuidadoso, sem perder conteúdo útil.\n\n` +
    `1. Leia o contrato de escopo: ${SCOPE_PATH}\n` +
    `2. Leia TODAS as skills-fonte deste cluster (SKILL.md de cada, e qualquer references/ que tenham):\n` +
    c.sources.map(s => `   - ${ROOT}/${s}/SKILL.md`).join('\n') + `\n\n` +
    `Master/estratégia: ${c.master}\n` +
    `Plano de merge: ${c.plan}\n\n` +
    `3. ESCREVA a skill consolidada em: ${c.target}\n` +
    `   - Frontmatter com name derivado do diretório-alvo e uma description AMPLA que dispare para todos os tópicos das fontes (some os triggers).\n` +
    `   - Una o conteúdo eliminando duplicação, preservando exemplos de código únicos e corretos de cada fonte. Mantenha PT e o estilo das skills.\n` +
    `   - Garanta aderência ao escopo (Adonis v6, MaxPinia para GET/save no front, Transmit, PostgreSQL, sem Inertia/Ziggy/Tailwind).\n` +
    `   - Se o diretório-alvo já é uma das fontes (master), edite-o in-place absorvendo as demais.\n\n` +
    `4. ARQUIVE cada skill-fonte ABSORVIDA (todas exceto a que é o próprio diretório-alvo) movendo o diretório inteiro para ${ARCHIVE}/ via \`mv\`. NÃO arquive o diretório-alvo. NÃO delete nada — só mova.\n` +
    `   Ex.: \`mv ${ROOT}/front-end-vue/vue-facebook-post-preview-simulator-best-practices ${ARCHIVE}/\`\n\n` +
    `5. Se houver skills que o plano manda NÃO tocar (ex.: pdf-coordinate-editing), apenas adicione um cross-link e não as mova.\n\n` +
    `Retorne: skill consolidada criada (path), skills arquivadas (lista), e um resumo do que foi unido/descartado.`,
    { label: `merge:${c.id}`, phase: 'Mesclar' }
  )
))

const done = (results || []).filter(Boolean)

phase('Resumo')
const summary = await agent(
  `Consolide o resultado de 5 merges de cluster de skills (EngeApp→Adonis). Dados:\n` +
  JSON.stringify(done) +
  `\n\nResuma em Markdown PT: por cluster — skill consolidada resultante, quantas/quais skills foram arquivadas, e qualquer perda de conteúdo ou ponto que exija revisão humana.`,
  { label: 'resumo', phase: 'Resumo' }
)

return { clusters: clusters.length, summary, details: done }
