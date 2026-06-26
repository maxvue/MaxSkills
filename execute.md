# CRIAÇÃO OU ATUALIZAÇÃO DE SKILLS PARA A IDE GOOGLE ANTIGRAVITY 2.0

## INSTRUÇÕES GERAIS SOBRE A CRIAÇÃO DE SKILLS
1. **Idioma Principal e Localização:** Você deve criar ou melhorar as skills obrigatoriamente dentro da subpasta de categoria apropriada (`backend-node/`, `front-end-vue/` ou `general/` para skills transversais) em `created-skills/categoria/nome-da-skill/SKILL.md` utilizando o idioma **Inglês**. *(A categoria `backend-laravel/` foi descontinuada em 2026-06-25 — o stack canônico é AdonisJS + Vue.)*
2. **Cópia Localizada:** Uma cópia idêntica em estrutura e conteúdo da skill criada ou atualizada deve ser gerada na subpasta correspondente de `created-skills-pt-br/categoria/nome-da-skill/SKILL.md` no idioma **Português Brasileiro**.

---

## FASE 1 — PLANEJAMENTO
1. **Padrões Antigravity:** Leia o arquivo `general-instructions/antigravity-standards.md` para compreender a arquitetura e os níveis estruturais das skills.
2. **Proposta:** Obter o arquivo da proposta elaborada na pasta `proposals-skills/`.
3. **Skill Existente:** Se a proposta for do tipo `ATUALIZAR`, obter o arquivo da skill existente na pasta `created-skills/`.
4. **Contexto e padrões:** Utilizando as instruções do arquivo `general-instructions/planning-sub-agents.md`, obter os padrões de código em relação à skill.
5. **Workflows:** Analisar os workflows citados no planejamento inicial (pasta `global-workflows/`) para auxiliar na criação/atualização da skill.
6. **Skills de Terceiros:** Analisar as skills de terceiro citadas na proposta para auxiliar na criação/atualização da skill.
7. **Vue:** Se o uso desta skill for em arquivos `.vue`, considerar as instruções em `general-instructions/vue-components.md`.
8. Elabore o plano de forma detalhada conforme a proposta e os dados obtidos e **execute diretamente** as fases seguintes sem aguardar aprovação.

---

## FASE 2 — PRÉ-EXECUÇÃO
1. Antes de iniciar a execução, atualize o arquivo `list-skills.yaml` modificando (ou criando, se não existir) o item correspondente, definindo o status como `EXECUTANDO`.

---

## FASE 3 — EXECUÇÃO
1. Ao criar o arquivo `SKILL.md`, você DEVE utilizar a estrutura oficial do Google Antigravity:
   - Inicie o arquivo com **YAML Frontmatter** definindo `name` (kebab-case) e `description` (frase de ativação semântica detalhada, ou *wake word*).
   - O corpo do arquivo DEVE conter obrigatoriamente as subseções, sempre em nível `##`, além de `## Examples` se houver. **O idioma dos cabeçalhos segue a pasta (padrão bilíngue):**
     - Pasta `created-skills/` (**EN, original/canônica**): `## Goal`, `## Instructions`, `## Constraints`.
     - Pasta `created-skills-pt-br/` (**PT, espelho traduzido**): `## Objetivo`, `## Instruções`, `## Restrições`.
   - **Atenção:** apenas o corpo e os cabeçalhos das seções são traduzidos no espelho PT. O campo `description` (wake word) permanece **idêntico e em Inglês** nas duas versões (ver Fase 3.2).

2. **Qualidade da Wake Word (description):** O campo `description` no frontmatter é o campo **MAIS IMPORTANTE** da skill. Ele funciona como gatilho semântico para o roteador do agente decidir quando carregar a skill. Siga estas diretrizes:

   **❌ Exemplos RUINS de description (vagos e genéricos):**
   ```
   description: Ferramentas de banco de dados.
   description: Ajuda com componentes Vue.
   description: Boas práticas de AdonisJS.
   ```

   **✅ Exemplos BONS de description (específicos e acionáveis):**
   ```
   description: Use when creating, reviewing, or debugging background jobs and queues in AdonisJS v6 with BullMQ, configuring workers, handling job retries and failures, or optimizing queue throughput. Triggers on job dispatch, queue config, retry/backoff logic, and worker monitoring.
   description: Formats git commit messages according to Conventional Commits specification. Use this when the user asks to commit changes or write a commit message.
   description: Adds the standard open-source license header to new source files. Use involves creating new code files that require copyright attribution.
   ```

   **Regras para uma boa wake word:**
   - Deve começar com um verbo de ação ou "Use when..."
   - Deve listar cenários específicos de ativação
   - Deve mencionar tecnologias, arquivos ou padrões concretos envolvidos
   - Deve ter entre 20 e 60 palavras
   - Idioma: SEMPRE em **Inglês**

3. **Otimize o contexto:** Não insira templates longos, textos densos ou scripts no `SKILL.md`. Em vez disso, crie subpastas na raiz da skill:
   - `scripts/` para códigos executáveis (Bash, Python, Node).
   - `resources/` ou `references/` para textos grandes, templates ou documentação base.
   - `examples/` fornecendo arquivos de `input` e `output` se a skill envolver conversão ou padronização de dados.

4. Todas as referências a arquivos auxiliares dentro do `SKILL.md` devem utilizar **caminhos relativos** corretos à raiz da skill (ex: `resources/TEMPLATE.md`).

5. Execute as alterações necessárias (criação ou atualização) nas subpastas de `created-skills/` e `created-skills-pt-br/` seguindo as diretrizes do plano aprovado.

---

## FASE 4 — VALIDAÇÃO PÓS-CRIAÇÃO
Antes de finalizar, execute esta checklist de validação obrigatória:

- [ ] O arquivo `SKILL.md` possui **YAML Frontmatter** válido com `name` e `description`?
- [ ] A `description` (wake word) segue as regras de qualidade definidas na Fase 3?
- [ ] O corpo contém as seções obrigatórias em nível `##` e no idioma da pasta? (EN: `Goal`/`Instructions`/`Constraints`; PT: `Objetivo`/`Instruções`/`Restrições`)
- [ ] A `description` (wake word) está em **Inglês e idêntica** entre a versão EN e a cópia PT?
- [ ] Os blocos de código (```) estão todos **fechados** (nº par de cercas)?
- [ ] Se há referências a arquivos auxiliares, os **caminhos relativos** estão corretos?
- [ ] Se é Nível 2+, as pastas auxiliares (`resources/`, `examples/`, `scripts/`) existem e estão preenchidas?
- [ ] A cópia em `created-skills-pt-br/` foi criada com conteúdo traduzido?
- [ ] A skill não duplica o propósito de outra skill já existente?

---

## FASE 5 — INTEGRAÇÃO COM WORKFLOWS
Após a validação, verifique o campo **"Workflows"** da proposta. Para cada workflow listado:

> **⚠️ ATENÇÃO — CAMINHO PROTEGIDO:**
> A pasta `global-workflows/` no repositório é um **symlink** que aponta para `~/.gemini/config/global_workflows/`.
> Este é um caminho protegido pelo sistema. Para editá-lo, você **DEVE**:
> 1. Solicitar **permissão de escrita** (write_file) para o caminho absoluto `/home/johnattas/.gemini/config/global_workflows/`.
> 2. Utilizar o **caminho absoluto completo** do arquivo ao editá-lo (ex: `/home/johnattas/.gemini/config/global_workflows/agent-ai-create.md`).
> 3. **NÃO** tente editar via o caminho relativo do symlink — use sempre o caminho absoluto.
1. Localize o arquivo do workflow na pasta `global-workflows/` (usando o caminho absoluto `/home/johnattas/.gemini/config/global_workflows/`).
2. Verifique se o workflow já possui uma seção `## SKILLS UTILIZADAS ##`.
   - Se **não existir**: Crie a seção no final do arquivo (antes do bloco `---` de fechamento, se houver).
   - Se **já existir**: Adicione a nova skill à lista existente, evitando duplicatas.
3. Insira o nome da skill criada no formato de lista Markdown:

```markdown
## SKILLS UTILIZADAS ##
- nome-da-skill-criada
```

**Exemplo prático:** Se a proposta lista o workflow `agent-ai-create` e a skill criada é `adonisjs-ai-agents-best-practices`, o arquivo `global-workflows/agent-ai-create.md` deve receber:

```markdown
## SKILLS UTILIZADAS ##
- adonisjs-ai-agents-best-practices
```

> **IMPORTANTE:** Não modifique o conteúdo existente do workflow. Apenas adicione ou atualize a seção `## SKILLS UTILIZADAS ##`.

---

## FASE 6 — FINALIZAÇÃO
1. Após a conclusão e validação das alterações, atualize o arquivo `list-skills.yaml` alterando o status do item correspondente para `CONCLUIDA`.