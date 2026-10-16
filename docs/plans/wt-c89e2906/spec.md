# Especificação técnica — Dimensionamento fluido e MaxGrid nas skills

- Data: 16/10/2026.
- Projeto: MaxSkills.
- Worktree exclusiva: `/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-c89e2906`.
- Branch observada: `wt-c89e2906`.
- HEAD investigado: `19c90e03af72a5f904a1811227bfb603c868a96a`.
- Estado: especificação para revisão; nenhuma atualização de skill foi executada nesta sessão Plan.

## 1. Contexto & Objetivo

Atualizar todas as skills locais afetadas pelo contrato atual de `presetMaxUno`, incluindo o funcionamento de MaxGrid e seus auxiliares internos. A família `sN`/`s-N` deixou de representar porcentagem. Exemplos antigos como `s50` e `s100` continuam sintaticamente válidos, mas agora impõem mínimos de 1.000 e 2.000 pixels. Usá-los como metade ou largura inteira ensina layouts incorretos.

O resultado esperado é uma referência técnica única, instruções curtas nos pontos de entrada das skills e exemplos coerentes com dimensionamento fluido. O público são agentes e mantenedores que produzem interfaces Vue consumidoras das bibliotecas Max.

O trecho fornecido pelo usuário coincide com `projects/MaxComponentsUi/src/presetMaxUno.ts:84–119`. Esse caminho é um symlink para outro repositório e foi consultado somente em leitura. O `package.json` dessa referência declara `@maxvue/max-components-ui` versão `1.1.12` e UnoCSS `^66.10.5`; isso não comprova a versão publicada nem a instalada em cada consumidor.

## 2. Escopo

### Incluído

- Atualizar as skills autorais de layout, styling, referência de API, formulários e diagnóstico afetadas; cobrir exemplos e arquivos de referência, não apenas `SKILL.md`.
- Explicar gramática, fórmulas, máximos, dispositivos, posições, limites de aplicação e migração de exemplos.
- Documentar `MaxGrid`, `GridSlotRows`/`renderGridSlotRows`, `InputBase` e o encaminhamento observado em `MaxInputText`, distinguindo internos de API pública.
- Preservar o uso de MaxComponentsUi nas interfaces, MaxPinia para os fluxos novos de dados e MaxUse para helpers. Esta mudança documental não migra stores legadas nem introduz novas requisições.
- Criar uma referência detalhada e testes documentais pequenos, sem novas dependências; preservar nomes, descrições e manifestos das skills.
- Investigar por busca direcionada todo o catálogo para garantir que não existam outras instruções Max afetadas. Não aplicar alterações genéricas a skills que não tratam desse contrato.

### Fora do escopo

- Implementar ou corrigir `presetMaxUno`, MaxGrid, seus testes upstream ou aplicações consumidoras.
- Completar suporte do MaxGrid para quebras desktop/tablet/mobile-start.
- Mudar comportamento de inputs, modelos, validações, autenticação, cache, salvamentos, uploads ou segurança de credenciais.
- Corrigir outros contratos antigos do catálogo, atualizar versões/dependências, migrar PrimeVue, modificar temas ou modo escuro.
- Editar symlinks/projeções, repositórios referenciados em `projects/`, conteúdo de terceiros, relatórios históricos ou instruções globais.
- Instalação, build de biblioteca, publicação, commit, merge, push, troca de branch ou remoção de worktree.

## 3. Arquitetura & Mudanças Técnicas

### 3.1 Contrato da família `s`

Gramática efetiva, confirmada no fonte:

```text
^s-?(\d+)(?:-(full|max|\d+))?(?:-(start|end)(?:-(desktop|mobile|tablet))?|-(desktop|mobile|tablet)(?:-(start|end))?)?$
```

- `N` é inteiro não negativo aceito pelo regex; não há faixa obrigatória 1–100. Prefira valores positivos adequados à largura mínima desejada. Negativos, decimais e unidades não pertencem a essa gramática.
- Sempre: `flex: 1 1 0%` e `min-width: N × 20px`.
- Máximo omitido: `max-width: N × 24px`.
- Máximo `M` numérico: `max-width: M × 20px`.
- Máximo `full` ou `max`: `max-width: 100%`; não altera o mínimo e não força `width: 100%`.
- O token não emite `width: N%` nem `flex-basis: N%`. Não representa fração fixa, porcentagem ou número de colunas.
- `start` emite `break-before: always`; `end` emite `break-after: always`. Sozinhos, esses estilos de fragmentação não organizam linhas de um flexbox comum.
- Uma posição e um dispositivo podem vir em qualquer das duas ordens, depois do máximo opcional: `s7-10-end-mobile` e `s7-10-mobile-end`.
- Dispositivos restringem **todas** as declarações emitidas pelo token: mobile `max-width: 767.98px`; tablet `max-width: 1000.98px`; desktop `min-width: 1001px`.
- Tablet inclui mobile: não é uma faixa exclusiva. O intervalo fracionário acima de 1000.98 e abaixo de 1001 não é coberto por tablet/desktop; documentar sem alterar breakpoints.
- Fora da media query, o token não estabelece um tamanho alternativo. Não prometer precedência entre vários tokens aplicáveis sem verificar a cascata gerada.

| Token | Mínimo | Máximo | Efeito adicional |
|---|---:|---:|---|
| `s1` / `s-1` | 20px | 24px | nenhum |
| `s7` / `s-7` | 140px | 168px | nenhum |
| `s3-10-start` | 60px | 200px | declaração CSS antes; MaxGrid inicia segmento |
| `s7-full` / `s7-max` | 140px | 100% | pode crescer, não força largura inteira |
| `s7-end-mobile` / `s7-mobile-end` | 140px | 168px | CSS e encerramento MaxGrid somente em mobile |
| `s50` | 1000px | 1200px | não significa 50% |
| `s100` | 2000px | 2400px | não significa 100% |

Casos a explicar: mínimo maior que o contêiner pode provocar overflow, inclusive com `full`; máximo numérico menor que o mínimo não é rejeitado pelo regex e não deve ser recomendado. A largura final depende de conteúdo, espaço disponível, gap e outras regras CSS. Não oferecer conversão automática de porcentagem antiga para `N`.

### 3.2 Contrato de MaxGrid e internos

```text
Token literal no template ─→ UnoCSS/presetMaxUno ─→ flex + min/max + media + break-*
Filhos do slot MaxGrid ─→ GridSlotRows ─→ marcadores ativos ─→ div.max-grid-row
MaxInputText + attrs ─→ InputBase/rootAttrs ─→ caixa externa dimensionada
```

- `MaxGrid.vue`: raiz `.max-grid`, `display:flex`, wrap, gap `13px 8px`, padding superior `14px`; props públicas `label?` e `labelCenter?`, slot default.
- `no-message`/`no-messages` são atributos tratados pelo CSS do grid, não novas props. Preservar documentação de label, gaps e mensagens.
- Sem marcador ativo, não cria wrappers de linha. Com marcadores, organiza os filhos lógicos em `.max-grid-row`, segmentos de largura inteira que herdam gap/alinhamento e ainda permitem wrap natural.
- `GridSlotRows` é funcional interno, com `inheritAttrs=false`; recebe `isMobile`, obtido no MaxGrid pelo `useMediaQuery` reexportado de MaxUse. Não orientar imports desse auxiliar pela aplicação.
- `renderGridSlotRows` achata Fragments de template/v-for, compõe keys, preserva VNodes e não percorre o conteúdo interno de componentes filhos. Marcadores devem estar no filho lógico recebido pelo slot; não basta colocá-los dentro de um wrapper ou de outro componente.
- Reconhece classes normalizadas e nomes de atributos ativos com valores `''`, `true` ou `'true'`. `false`, `null` e `undefined` não ativam o marcador do organizador; isso não é garantia sobre todo seletor CSS gerado pelo Attributify.
- `start`/`end` sem dispositivo são reconhecidos; `end-mobile`/`mobile-end` são reconhecidos somente em mobile. **Não há coordenação de linhas para start-mobile, start/end-tablet ou start/end-desktop**, embora o preset gere CSS para eles. Informar a diferença, não implementá-la.
- `end` seguido de `start` não deve ser descrito como linha vazia extra. Grids aninhados administram seus próprios slots.
- `MaxGridCols` é outro componente: CSS Grid de 24 colunas, raiz `.max-grid-cols`; não substitui MaxGrid em formulários e não fornece esse organizador de linhas.
- Em `MaxInputText.vue`, attrs seguem para InputBase; em `InputBase.vue`, classes/style e attrs de layout seguem para a raiz externa, enquanto atributos do controle seguem para o input. Registrar o percurso observado sem generalizar uma auditoria de todos os MaxInput*.

### 3.3 Organização documental

Criar `all_skills/created-skills/frontEnd/vue-unocss-styling-best-practices/references/max-grid-sizing.md` como referência detalhada de dimensionamento. A skill UnoCSS aponta para ela; a referência de API descreve o contrato de MaxGrid e seus internos, com link para as fórmulas. Demais skills recebem apenas exemplos corrigidos e links relativos, evitando duplicar tabelas extensas.

Os arquivos existentes e as responsabilidades estão enumerados no plano. A informação sobre unidades de `w-min/w-max/h-min/h-max` na skill de design deve ser corrigida pontualmente na mesma orientação de dimensionamento: o fonte atual usa `getCssSize`, que acrescenta `px` apenas a números e preserva unidades existentes. Não generalizar essa regra para `sN`.

Manter frontmatter, nomes, autores e caminhos das skills. Sem mudança nas descrições, `index.json`, `awesome_skills.json` e `other_skills.json` permanecem intactos. Não executar sincronizador que reescreve os três manifestos.

## 4. Plano de Execução Faseado

1. Revalidar fontes, worktree, alterações locais, caminhos reais e permissões por leitura.
2. Escrever a referência canônica, atualizar entrada UnoCSS e contratos da referência de API.
3. Corrigir todos os exemplos de dimensionamento afetados e pontos de diagnóstico, preservando lógica de domínio.
4. Implementar testes documentais de cobertura, exemplos e links; concluir todo o lote antes de executar validações.
5. Validar o conjunto pertinente, revisar contratos e limitações, corrigir falhas em lote e repetir apenas checks invalidados.
6. Entregar evidências e registro de execução futuro, sem integrar Git nem operar bibliotecas externas.

## 5. Critérios de Aceite & Validação

- Nenhuma orientação vigente trata `s50/s100` como porcentagens; exemplos novos usam mínimos realistas e distinguem largura inteira de máximo de 100%.
- Fórmulas, exemplos numéricos, gramática e breakpoints coincidem com o fonte; tablet inclui mobile.
- MaxGrid, seus internos e InputBase estão descritos sem export/prop inventados; limitações responsivas estão explícitas.
- Todos os pontos afetados encontrados na busca estão corrigidos ou classificados justificadamente como não dependentes do contrato; terceiros e fluxos de dados permanecem intactos.
- Testes documentais futuros cobrem tabelas, vínculos entre skills, links locais, tokens de exemplos e ausência dos snippets antigos nos locais conhecidos. Não devem chamar repositórios externos, instalar pacotes ou substituir revisão semântica.
- Comandos Git de leitura já identificados: `git status --short`, `git diff --check`, `git diff --stat`, `git diff` e buscas `git grep` delimitadas. O plano separa verificações futuras das leituras realizadas.
- `docs/scripts/verify_all_final.py` existe, mas contém contagens globais fixas e não é prova específica da nova semântica. Não fazer da varredura upstream global uma dependência desta entrega.
- O comando do teste novo será confirmado após sua criação em Execute; não existe ainda. Nenhuma suíte, lint, tipo, build, navegador ou script de validação foi executado nesta sessão Plan.
- Aceite de documentação não comprova publicação da biblioteca nem layout visual de aplicações consumidoras. Esses pontos estão fora do escopo e não devem ser relatados como validados.
