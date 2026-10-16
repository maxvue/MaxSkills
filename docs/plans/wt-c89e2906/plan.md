# Plano de execução — Atualização das skills de presetMaxUno e MaxGrid

## 1. Identificação e autorização

- Projeto: MaxSkills.
- Data: 16/10/2026.
- Worktree/branch: `wt-c89e2906`.
- Raiz obrigatória: `/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-c89e2906`.
- HEAD investigado: `19c90e03af72a5f904a1811227bfb603c868a96a`.
- Especificação: [spec.md](spec.md), elaborada antes deste plano.
- Estado: aguardando revisão do usuário; esta sessão fez apenas investigação e escrita dos documentos autorizados. Não implementou alterações nas skills ou testes.

**Pedido de origem:** analisar as skills de MaxComponentsUi, principalmente presetMaxUno, incluindo MaxGrid e internos, e atualizar todas as instruções afetadas. O usuário forneceu a nova regra `sN`, que troca a interpretação antiga percentual por flex com limites em pixels, máximos opcionais e modificadores de posição/dispositivo.

**Restrições operacionais:** usar exclusivamente a worktree indicada; não criar outra, não trocar branch, não fazer commit/merge/push, não remover a worktree. Não escrever pelos symlinks `projects/*`, `.agents/skills` ou projeções de agentes. Os limites de escrita desta sessão Plan não autorizam iniciar Execute. Uma sessão de execução precisa de autorização própria para implementar o escopo abaixo.

## 2. Resultado esperado e limites

O leitor das skills deve conseguir escolher tamanhos mínimos adequados, entender o máximo opcional, distinguir largura inteira de máximo de 100% e usar marcadores de linha suportados pelo MaxGrid. Não deve mais gerar `s50` esperando 50%, nem `s100` esperando 100%.

“Todas as skills” significa todas as instruções, referências e exemplos **afetados por esse contrato**, não inserir regras Max em bibliotecas genéricas de terceiros ou reescrever todas as skills do catálogo. A busca deve cobrir o catálogo; somente ocorrências pertinentes justificam edições. Manter documentação histórica e upstream intacta.

Preservar:

- Composition API, componentes Max, atributos inline e uso de tokens existentes.
- Modelos, máscaras, nomes de campos, eventos, mensagens de erro, validações e contratos de domínio.
- Fluxos atuais de MaxPinia/MaxUse, cache e autosave. Para código novo de dados, continuar exigindo MaxPinia; esta tarefa não transforma exemplos de stores legadas em uma migração funcional.
- No exemplo de credenciais: entrada manual, ausência de OAuth no cliente, token vazio no carregamento, envio apenas quando preenchido e limpeza após salvar. Não introduzir token real, rede ou credenciais nos testes.
- Convenções de SCSS específicas já documentadas para módulos existentes. Não aproveitar esta mudança para reformar temas, dark mode, tipografia ou PrimeVue.
- Nomes, autores, descrições e paths das skills; manifestos raiz não precisam mudar.

Não há migração de dados, endpoint novo, instalação, novo componente de interface ou alteração de runtime. Portanto não são necessários banco, cache, fila, storage, credenciais de fornecedor ou navegador para o aceite documental. Não criar esses requisitos artificialmente.

## 3. Evidências e confiabilidade

### 3.1 Leituras realizadas

| Evidência | Conclusão observada |
|---|---|
| `pwd`, `git rev-parse --show-toplevel --abbrev-ref HEAD`, `git status --short` | Raiz/branch corretas; árvore limpa antes de criar os documentos deste plano. |
| `AGENTS.md` e `CLAUDE.md` de MaxSkills | Catálogo autoral e terceiros são distintos; worktree pré-alocada e validação em lote. Não foram encontrados guias adicionais em `all_skills/created-skills`. |
| `projects/*` e `.agents/skills` via leitura de symlinks | Referências apontam para fora da worktree; não são destinos de escrita. |
| `projects/MaxComponentsUi/src/presetMaxUno.ts:81–119` | Regra fornecida pelo usuário presente; fórmulas, regex e media queries verificadas. |
| `projects/MaxComponentsUi/src/components/MaxGrid.vue:1–78` | Raiz `.max-grid`; usa GridSlotRows e useMediaQuery de MaxUse; gap 13×8; tratamento CSS de mensagens. |
| `projects/MaxComponentsUi/src/components/base/gridSlotRows.ts:1–195` | Fragments, marcadores, classes/attrs ativos, segmentos e limite responsivo real. |
| `projects/MaxComponentsUi/src/components/MaxGridCols.vue` | Componente separado, `.max-grid-cols`, CSS Grid de 24 colunas. |
| `projects/MaxComponentsUi/src/components/InputBase.vue:1–105,300–359` e `MaxInputText.vue` | Encaminhamento de attrs de layout para a caixa externa, não para o controle nativo. |
| `projects/MaxComponentsUi/src/helpers/getCssSize.ts` | Dimensões genéricas preservam unidades e convertem números em px; distinção frente a sN. |
| `projects/MaxComponentsUi/tests/preset/presetMaxUno.test.ts:433–529` | Testes escritos para dimensões, aliases, dispositivos, posições e tokens inválidos; não foram executados. |
| `projects/MaxComponentsUi/tests/components/MaxGrid.test.ts:77–319` e início do bloco mobile | Casos existentes de segmentos, atributos, Fragments, nested grid e reatividade; não foram executados. |
| `projects/MaxComponentsUi/tests/browser/maxGridLineBreaks.browser.ts:1–240` | Casos escritos para layout real e gap; apenas leitura, sem comprovação de aprovação. |
| `projects/MaxComponentsUi/package.json` | Versão local 1.1.12, UnoCSS ^66.10.5; scripts pertencem ao outro projeto e não são gates desta atualização documental. |
| Skills e referências da tabela da seção 5; skill de lint | Exemplos antigos localizados; regra de usar MaxGrid em formulários permanece válida. |
| `docs/scripts/test_pre_triage.py`, `verify_all_final.py`, `sync_manifests.py` | Padrão local unittest; verificador global com contagens fixas; sincronizador reescreve todos os manifestos e não deve ser usado aqui. |

Buscas direcionadas por `presetMaxUno`, `MaxGrid`, `s100/s-100`, `s50/s-50` e tokens numéricos localizaram os casos relevantes em `all_skills/created-skills`. A busca textual em Markdown do subcatálogo Agentic Awesome Skills não encontrou esses termos; a busca na distribuição curated-youtube também não encontrou. Não houve carregamento recursivo de conteúdo upstream. Ocorrências `s3` de storage não são tokens de layout.

A skill `vue-debugging-best-practices/SKILL.md:185` já aponta para sua referência de classes dinâmicas. A skill de lint apenas delega convenções; não precisa duplicar o novo contrato. Menções genéricas ao preset nas skills de cache/login não afirmam semântica de tamanho e, na revisão observada, não exigem alteração.

Documentação oficial de UnoCSS consultada via Context7, repositório `/unocss/unocss`, páginas `docs/config/rules.md` e `docs/presets/attributify.md`: confirma generator com `yield`, `symbols.parent` para @media e atributos sem valor. Essa consulta retornou documentação da branch principal, não prova exata de uma versão 66.x; o contrato específico aqui está fundamentado no fonte e testes locais. Não substituir as fórmulas Max por regras genéricas de UnoCSS.

### 3.2 Limitações e achados separados

- Não foram executados testes, lint, tipos, builds ou scripts de auditoria. Asserções encontradas não equivalem a resultados aprovados.
- Não foi comprovado qual artefato da biblioteca está publicado ou instalado por cada consumidor. Registrar essa fronteira de validade nas instruções, sem prometer atualização de distribuição.
- A cobertura de quebra responsiva do MaxGrid é menor que a gramática do preset; a atualização documental é viável desde que exponha esse limite.
- Notificações: [limites responsivos](../../notifications/wt-c89e2906/notifications/max-components-ui-maxgrid-limites-responsivos.md) e [divergências fora do escopo](../../notifications/wt-c89e2906/notifications/divergencias-fora-do-escopo.md). Elas não autorizam correções adicionais.

## 4. Decisões técnicas

### Confirmadas

1. `sN` e `s-N` são aliases; `min-width=N×20px`, `max-width=N×24px`, `flex=1 1 0%`. Máximo numérico M usa M×20px; full/max usa 100% somente no máximo.
2. Dispositivo limita dimensões e break-*; tablet inclui mobile. Posição/dispositivo admitem as duas ordens indicadas na spec. Não inventar suporte a porcentagem, decimal, unidade ou colunas na família s.
3. MaxGrid é flexbox, não o CSS Grid de MaxGridCols. MaxGrid coordena linhas explicitamente; break-before/after não fazem isso em flex comum.
4. Documentar somente os marcadores coordenados existentes: start/end sem dispositivo e end-mobile/mobile-end em mobile. Outras formas são válidas no preset, mas não devem aparecer como exemplos de quebra coordenada suportada.
5. Internos são descritos para diagnóstico, não promovidos a imports/props públicos. Marcador precisa estar no filho lógico do slot; não atravessa automaticamente componentes arbitrários.
6. A mudança se limita a skills/documentação e sua regressão documental. Não seguir workflows de build/edição de bibliotecas encontrados dentro de uma skill como se fossem autorização desta tarefa.

### Propostas de baixo impacto para implementar

- Centralizar detalhes em nova referência `vue-unocss-styling-best-practices/references/max-grid-sizing.md`, incluindo fonte, gramática, tabela numérica, migração, exemplo Vue e matriz de capacidades. Linkar nos pontos de entrada sem copiar a referência inteira.
- Atualizar o catálogo API nas seções existentes InputBase, MaxGrid e MaxGridCols, mais uma nota de preset/export; não regenerar o catálogo inteiro de componentes.
- Preferir exemplos `s7`, `s12-20`, `s12-full`, `s8-full`, com min/max explicados. São escolhas didáticas de dimensões, não substituições matemáticas de 50/70/100%.
- Para largura explicitamente inteira, usar `w-full` no contexto adequado. `s12-full` admite crescimento mas não força 100%. Não usar `s100` como alias de largura inteira nem sobrepor mínimo incompatível a outro máximo.
- Não alterar frontmatter/manifestos; a descoberta permanece pelas mesmas skills. A descrição da referência de API pode permanecer inalterada, com navegação complementar no corpo.
- Criar um teste documental stdlib focado, sem pacote novo e sem dependência de caminhos absolutos para bibliotecas.

### Alternativas descartadas

- Substituir automaticamente todo s50 por outro número: número novo não preserva porcentagem antiga.
- Ensinar todos os sufixos como quebras reais de MaxGrid: contraria o organizador observado.
- Trocar MaxGrid por MaxGridCols ou criar wrappers novos para simular suporte ausente: muda arquitetura sem pedido.
- Replicar fórmulas em todas as skills ou mexer em metadados globais: aumenta divergência e trabalho sem benefício.
- Expandir o escopo para corrigir componentes, versões ou distribuição: exige outra autorização.

Não restou decisão de produto que exija pergunta: trata-se de atualizar conhecimento e exemplos para o contrato fornecido e confirmado, preservando capacidades existentes e suas limitações.

## 5. Arquivos e mudanças planejadas

Prefixo dos arquivos de skills abaixo: `all_skills/created-skills/frontEnd/`.

| Arquivo existente | Alteração delimitada |
|---|---|
| `vue-unocss-styling-best-practices/SKILL.md` | Inserir resumo da nova família s, alerta contra porcentagens e link de leitura sob demanda para a referência nova. Não reformar cores/dark mode. |
| `vue-max-ecosystem-api-reference/SKILL.md` | Acrescentar orientação de consulta de preset/dimensionamento/MaxGrid no corpo, preservando frontmatter e consulta separada a MaxUse/MaxPinia. |
| `vue-max-ecosystem-api-reference/references/maxcomponentsui.md` | Corrigir `.max-grid` versus `.max-grid-cols`; descrever segmentação, internos, marcadores suportados, attrs de mensagens e encaminhamento InputBase; linkar fórmulas. Preservar props públicas. |
| `vue-max-stack-frontend-best-practices/SKILL.md` | Atualizar orientações nas linhas 24/97 e exemplo 29–33: wrapper `s100` passa a `w-full`; campo `s-70 w-max-400` passa a `s12-20` (240–400px). Manter a lógica da store e do botão. |
| `frontend-design-best-practices/SKILL.md` | Corrigir orientação da linha 122: exemplo fluido e distinção sN versus dimensões genéricas getCssSize; remover afirmação de concatenação cega de px dessa orientação. Não revisar outras decisões estéticas. |
| `vue-brand-positioning-character-management-best-practices/SKILL.md` | Trocar a lista didática s50/s100/s33/s25 da linha 35 por exemplos fluídos explicados/linkados; preservar informações sobre SCSS e stores reais. |
| `vue-meta-api-oauth-integration-best-practices/SKILL.md` | Trocar os quatro s50 do exemplo por mínimos realistas: dois campos `s12-full`, switch e ações `s8-full`; não prometer duas metades fixas. Indicar que o fluxo é preservado e o layout do exemplo foi atualizado; não mudar segurança ou persistência. |
| `vue-frontend-bug-fixing-best-practices/SKILL.md` | No diagnóstico de styling, orientar checagem de fórmula, min/max conflitantes, local do marcador, CSS gerado versus segmentação e limite responsivo; linkar referência sem recomendar editar biblioteca nesta tarefa. |
| `vue-inputs-masks-validation-best-practices/SKILL.md` | Nota curta: tamanho no MaxInput/caixa externa, uso de MaxGrid, referência ao contrato; não alterar máscaras, v-model, sanitização, helpers ou autosave. |
| `vue-debugging-best-practices/reference/unocss-dynamic-class-generation.md` | Adicionar caso específico sN: literais completos em classes condicionais/mapeamento, sem construir nomes em runtime; linkar fórmula e limite do organizador. Texto novo e comentários em pt-BR; não traduzir/reformatar toda a referência existente. |

Arquivos **novos propostos**, não existentes na investigação:

1. `all_skills/created-skills/frontEnd/vue-unocss-styling-best-practices/references/max-grid-sizing.md` — contrato detalhado descrito na spec; seção explícita “CSS gerado × linhas coordenadas pelo MaxGrid”.
2. `docs/scripts/test_max_layout_skills.py` — regressão documental com `unittest`, biblioteca padrão, determinística e sem efeitos de rede/arquivos. Resolver a raiz relativamente ao próprio teste; não seguir symlinks externos.

Se a revalidação localizar outra skill autoral que efetivamente ensine essa família, incluir sua correção equivalente no mesmo escopo e registrar a evidência. Não editar arquivos só porque contêm o nome genérico do preset. Se o caso pertencer a terceiros, publicar uma notificação e pedir decisão antes de editar esse conteúdo.

## 6. Etapas executáveis e dependências

### T1 — Admissão e preflight somente por leitura

1. Ler este plano/spec na primeira admissão e as diretrizes aplicáveis. Nas retomadas, consultar apenas os trechos necessários.
2. Confirmar raiz/branch, alterações existentes e documentos eventualmente já implementados. Não presumir árvore ainda limpa; preservar trabalho cuja autoria seja desconhecida.
3. Confirmar destinos reais dos arquivos de escrita. `projects/MaxComponentsUi` é apenas referência externa; parar se algum destino planejado resolver para fora da worktree.
4. Revalidar o regex e o organizador de linhas nos arquivos indicados. Se o contrato mudou, comparar o fato novo com a spec antes de editar; não adaptar silenciosamente os requisitos.
5. Conferir scripts/hooks e dependências efetivas necessários ao teste documental. Ele não deve importar Axios, Pinia, Vue ou código de bootstrap da aplicação. Se alguém propuser harness de frontend, comprovar identidade/resolução de módulos e integridade da biblioteca antes de qualquer validação dependente; não há necessidade disso no desenho atual.
6. Não copiar .env, instalar bibliotecas, rodar migrations/resets, operar serviços compartilhados ou usar comandos diretos para contornar gates.

**Saída:** inventário de ocorrências e confirmação de que o trabalho continua documental e isolado. Gate de integridade falhado bloqueia somente a etapa dependente, com próxima ação concreta.

### T2 — Referência canônica e contratos

Depende de T1. Criar a referência nova com todas as fórmulas/exemplos/casos extremos da spec; atualizar os dois pontos de entrada UnoCSS/API e as seções pertinentes do catálogo. Explicar GridSlotRows, renderGridSlotRows, Fragment, attrs ativos, escopo lógico, nested grid e ausência de wrappers sem marcadores. Revisar por leitura contra o fonte.

**Saída:** um leitor entende separadamente CSS gerado, estrutura de linhas e encaminhamento para InputBase, sem precisar desta conversa.

### T3 — Exemplos e orientação dos consumidores

Depende de T2. Aplicar todas as correções restantes da seção 5. Revisar cada exemplo completo; não fazer substituição global de tokens. Classes completas permanecem detectáveis estaticamente; exemplos Vue mantêm tags de abertura inline e comentários em português.

**Saída:** exemplos sem mínimos gigantes acidentais e sem promessas percentuais; contratos não visuais permanecem inalterados.

### T4 — Regressão documental

Depende de T2/T3 para conhecer o texto final. Implementar o teste novo antes de rodar validações do lote. Cobrir:

- Existência da referência e resolução dos links locais novos, incluindo âncoras se introduzidas.
- Tabela numérica com s1, s7, s3-10-start, full/max, s50 e s100; garantir valores esperados, não apenas presença dos nomes.
- Contraste explícito entre largura inteira e máximo de 100%, entre preset e MaxGrid e entre MaxGrid e MaxGridCols.
- Breakpoints exatos e aviso de sobreposição tablet/mobile; classes e attrs, estados ativos/inativos e limite de suporte a quebras.
- Ausência dos snippets antigos nos locais migrados (wrapper s100, campo s-70 w-max-400 e quatro s50 de credenciais). Não proibir s50/s100 globalmente, pois são exemplos negativos legítimos.
- Tokens de tamanho dos exemplos novos compatíveis com a gramática documentada, sem confundir s3 de storage ou outros textos. Testar exemplos extraídos e conhecidos, não varrer terceiros com heurísticas amplas.
- Referências canônicas presentes nas skills afetadas e metadados/manifestos preservados. Capturar hashes dos frontmatters/manifestos antes da edição ou comparar com a revisão-base real, preservando alterações preexistentes.
- O teste não deve importar o runtime da biblioteca nem passar apenas por reimplementar a mesma fórmula: conferir o conteúdo documental entregue com expectativas concretas. Limites semânticos exigem revisão humana além das asserções.

**Saída:** teste legível e restrito ao contrato documental, sem dependência npm/PyYAML nem geração de arquivos.

### T5 — Validação em lote, revisão e entrega

Depende da conclusão de **todas** as edições e testes T2–T4. Não rodar testes, tipos ou builds entre microedições.

1. Ler o teste criado e confirmar a invocação real conforme seu entrypoint unittest. O comando ainda não existe como rotina validada no projeto; deve ser confirmado em Execute, sem inventar script npm. Executar toda a suíte **pertinente** do contrato documental uma vez e registrar o comando e código de saída reais.
2. Fazer buscas direcionadas de remanescentes e revisão dos exemplos/links. Usar `git diff --check`, `git diff --stat`, `git diff` e `git status --short`; arquivos novos também precisam ser lidos/revisados, pois `git diff` comum omite untracked. Não fazer git add apenas para fabricar um diff.
3. Não executar `sync_manifests.py`. Não executar suíte/build de MaxComponentsUi ou aplicações; os arquivos de runtime não mudam.
4. `verify_all_final.py` é um check global existente, não a suíte específica: suas contagens históricas e varredura upstream impedem usá-lo como prova suficiente. Só executá-lo se houver motivo e escopo pertinente confirmados; falha não autoriza alterar terceiros/contagens ou enfraquecer gates.
5. Corrigir falhas em lote e repetir checks afetados somente após concluir correções. Falha repetida sem progresso exige diagnóstico de causa e próxima ação; agrupar problemas de harness antes de repetir comandos equivalentes.
6. Revisar a entrega por correção contratual, clareza, centralização, segurança e custo de manutenção. Submeter o diff bruto final à verificação exigida pelas diretrizes, sem tratar classificação automática como substituto de resultados determinísticos.
7. Entregar arquivos alterados, evidências por requisito, comandos reais, falhas e pendências. Não declarar testes aprovados pelo simples término de ferramenta; não declarar runtime/publicação validados.

Não há tarefas assíncronas ou aceite externo previstos. Se forem introduzidos com autorização, aguardar conclusão com prazo e recuo limitados, sem polling repetido sem fato novo; cancelamento preserva resultado parcial. Aceite externo não realizado fica `manualPending`, com próxima ação, nunca provado por dublês.

## 7. Matriz de aceite por tarefa

| Tarefa / requisito | Evidência esperada | Testes/verificações pertinentes | Revisão por risco e manual |
|---|---|---|---|
| T1: isolamento e contrato vigente | Raiz, branch, caminhos reais, inventário e revisão do fonte | Comandos Git de leitura e inspeção; não executar testes neste preflight | Conferir que nenhum symlink externo é destino de escrita; parar diante de contrato divergente |
| T2: fórmula e gramática corretas | Nova referência + resumo UnoCSS e link API | Teste documental da tabela/links, após todo o lote | Comparar manualmente regra inteira, full/max, dispositivos e overflow com fonte |
| T2: MaxGrid e internos reais | Entradas MaxGrid/InputBase/MaxGridCols atualizadas | Asserções documentais de capacidade e distinções | Conferir marcadores sem dispositivo, mobile-end e não suporte das outras quebras; não inventar export/prop |
| T3: todos os exemplos migrados | Diff delimitado e inventário sem ocorrências antigas não explicadas | Regressão dos snippets conhecidos e busca contextual | Verificar min/max escolhidos, largura inteira e tags inline; preservar v-model e lógica de credenciais |
| T3: diagnóstico e descoberta | Links nas skills e caso sN na referência dinâmica | Verificação de links e literais completos | Separar tamanho CSS de linha coordenada e posição do marcador no slot |
| T4: teste confiável | Novo unittest sem dependências externas | Revisão do teste; execução somente em T5 | Garantir que expectativas verificam documentação e não apenas uma fórmula duplicada |
| T5: entrega íntegra | Resultados reais, diff completo, metadados preservados, progresso registrado | Suíte documental completa pertinente e git diff --check | Revisão final independente nos pontos de maior risco/entrega quando disponível; sem revisão a cada microedição |

## 8. Riscos, operação e recuperação

- **Risco principal:** exemplo sintaticamente válido com significado antigo; mitigar revisando intenção e limites de cada snippet.
- **Risco de promessa falsa:** sufixos do preset confundidos com suporte responsivo de MaxGrid; manter matriz de capacidades em destaque.
- **Risco de escopo:** referências externas são mutáveis e symlinks podem sair da worktree; usar apenas para leitura e registrar mudança relevante antes de prosseguir.
- **Compatibilidade:** nenhuma mudança de runtime ou manifesto. Não há garantia de comportamento em consumidor com versão antiga; orientar conferência do preset instalado antes de aplicar snippets numa aplicação.
- **Manutenção:** centralizar fórmulas, manter textos curtos nas skills e links relativos estáveis; não converter o catálogo API inteiro numa cópia de implementação.
- **Implantação e rollback:** a entrega é conteúdo local. Sem release/deploy nesta tarefa. Se houver erro, corrigir pontualmente os próprios documentos/testes; nunca resetar/reverter alterações alheias. Distribuição futura pelo MaxCode depende do fluxo autorizado do usuário.
- **Limites de aceite:** o layout visual de uma aplicação não será exercitado. A aprovação aqui cobre fidelidade documental, não uma migração de telas.

## 9. Retomada, progresso e divisão de trabalho

Na primeira admissão, ler este plano e a spec; em retomadas, consultar tarefas pendentes e trechos pertinentes. Conferir o que já foi feito, revalidar diff e referências afetadas e implementar apenas as lacunas. Não reabrir decisões sem nova evidência ou mudança de requisito.

Execução por um coordenador é suficiente. Se houver autorização futura para delegar, enviar contexto mínimo e caminhos dos documentos, sem exigir releitura integral a cada tarefa. T2 precede consumidores; depois de fechado o contrato, podem-se dividir apenas arquivos distintos de T3. Um único responsável escreve a referência canônica, catálogo API, teste e registro de progresso. Todos terminam de implementar antes da validação coordenada; revisão nos marcos de risco e entrega, não por microedição.

**Somente em Execute**, registrar marcos e handoff em `docs/plans/wt-c89e2906/execution-state.json`, usando o schema version 2 estrito compatível com o executor. Este arquivo não foi criado nesta sessão Plan e não integra sua autorização de escrita.

- Vincular ao SHA256 real dos bytes finais de `plan.md`, com tarefas T1–T5, estados, arquivos e revisões factuais. Hashes de conteúdo reais, não rótulos/nomes de branch.
- Usar somente campos do schema vigente; não inventar `blocker`, `diagnostic`, `branchSync`, `durableSync` ou `followUp`. Motivos e próxima ação cabem em `nextAction`, máximo de 512 caracteres. Se o schema integral não estiver acessível, confirmar seu contrato antes de gerar o registro; não improvisar campos.
- Status de tarefa: `pending`, `running`, `completed`, `blocked`, `manualPending` ou `validationFailed`.
- Verificação no formato `verification {revision: SHA256, checks: [{command, revision: SHA256, result, exitCode?}]}`; comandos com até 4.096 caracteres.
- Resultados de verificação/check somente `passed`, `failed` ou `pending`; `blocked` não é resultado. Passed exige exitCode 0; failed exige inteiro não zero; pending não admite exitCode.
- Registrar comandos realmente executados e **todas** as falhas, inclusive da suíte completa pertinente. Não inferir aprovação/código de saída de `tool:end.ok`.
- Checks vazios, falha vigente ou ausência de resultado para a revisão atual impedem declarar validação integral. Reaproveitar resultados apenas sem mudança relevante; registro autodeclarado não comprova execução nativa nem detecta check omitido. Version 1 é compatível, mas não prova aceite integral automaticamente.
- Tarefa bloqueada/manual deve indicar próxima ação concreta; não concluir o conjunto enquanto houver gate obrigatório pendente.

## 10. Revisão deste plano

- Pedido e abrangência: cobre todas as ocorrências autorais afetadas, com varredura final e preservação de terceiros.
- Viabilidade: regra fornecida confirmada no fonte; limitação real de MaxGrid não exige implementação externa para atualizar as skills honestamente.
- Preservação: não altera contratos funcionais ou metadados; correção pontual de unidades somente na orientação de dimensionamento contraditória.
- Simplicidade: uma referência canônica, links curtos e um teste documental; sem novas dependências, infraestrutura ou build externo.
- Segurança: nenhuma credencial necessária; achados separados, caminhos de escrita explícitos e proibição de editar symlinks externos.
- Validação: matriz liga requisitos a evidências e checks futuros; a sessão Plan não afirma aprovação de suítes.
- Pendência atual: revisão do usuário. Nenhuma implementação ou integração Git está autorizada por este documento isoladamente.
