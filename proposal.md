# WORKFLOW PARA CRIAÇÃO DE UMA PROPOSTA DE SKILL

## INSTRUÇÕES GERAIS SOBRE A CRIAÇÃO DE PROPOSTAS
1. **Idioma:** A proposta deverá ser elaborada em Português Brasileiro.
2. **Localização:** O arquivo da proposta de skill deverá ser criado na pasta `proposals-skills/`.

---

## FASE 1 — PLANEJAMENTO — Localização de necessidades e definição de propósito.

### 1.1 — Verificação de Duplicatas (OBRIGATÓRIO)
Antes de qualquer análise, o agente **DEVE** verificar se já existe uma proposta semelhante:
1. Listar **todos** os arquivos da pasta `proposals-skills/` e ler o resumo de cada proposta existente.
2. Consultar o arquivo `list-skills.yaml` para verificar se existe um item com nome, objetivo ou escopo similar.
3. Verificar na pasta `created-skills/` se já existe uma skill criada que cobre o mesmo propósito.

**Regra de decisão:**
- Se existir uma proposta ou skill com propósito **idêntico ou muito semelhante**: **PARE** e informe ao usuário que a proposta já existe, indicando o arquivo correspondente. Sugira como alternativa a criação de uma proposta do tipo `ATUALIZAR` para a skill existente.
- Se existir uma proposta ou skill com propósito **parcialmente sobreposto**: Informe ao usuário sobre a sobreposição e peça orientação sobre como proceder (fundir, atualizar a existente, ou criar uma nova com escopo diferenciado).
- Se não houver sobreposição: Prossiga para o próximo passo.

### 1.2 — Análise de Necessidades
1. **Skills Existentes:** Verificar as skills já existentes na pasta `created-skills/`.
2. **Necessidades:** Utilizando as instruções do arquivo `general-instructions/planning-sub-agents.md`, analisar o projeto em busca de deficiências ou necessidades não cobertas pelas skills existentes.
3. **Tipo de Proposta:** Definir se será necessário criar uma nova skill (`CRIAR`) ou modificar/atualizar uma skill existente (`ATUALIZAR`). Evite criar skills com propósitos semelhantes — caso necessário, atualize as skills existentes.
4. **Workflows:** Analisar os workflows existentes na pasta `global-workflows/` e definir quais workflows farão uso desta skill.
5. **Skills Beneficiadas:** Procurar nas skills próprias (da pasta `created-skills/`) aquelas que serão beneficiadas com a skill objeto deste planejamento.
6. **Skills de Terceiros:** Procurar por skills de terceiros (pasta `.agents/skills/`) que podem auxiliar na elaboração desta skill.

### 1.3 — Análise de Dependências de Skills Próprias (OBRIGATÓRIO)
Verifique se esta nova skill fará **uso direto** de alguma skill própria já criada (das pastas `created-skills/` e `created-skills-adonis/`).

1. Liste todas as skills existentes em `created-skills/` e leia o `Goal` de cada uma.
2. Para cada skill encontrada, avalie se a skill que está sendo proposta precisará **consumir, referenciar ou estender** o conhecimento dela durante sua execução.
3. Se houver dependências identificadas:
   - Registre-as no campo **"Skills próprias utilizadas"** do template da proposta.
   - Para cada dependência, descreva brevemente **como** a skill proposta fará uso dela (ex: "Utilizará as regras de tipagem da skill `typescript-standards` para validar os tipos gerados").
   - No momento da **criação da skill** (workflow `execute.md`), o agente deverá ler o conteúdo completo dessas skills dependentes para incorporar seus padrões.

---

## FASE 2 — CRIAÇÃO DA PROPOSTA — Elaborar a proposta utilizando os dados obtidos na FASE 1.

1. Crie **imediatamente** o arquivo da proposta na pasta `proposals-skills/` utilizando o template obrigatório abaixo. **Não** solicite aprovação — a proposta em si é o documento que será avaliado posteriormente.
2. **Idioma:** Use estritamente o **Português Brasileiro** para arquivos de proposta.

### Template Obrigatório da Proposta:

```markdown
# PROPOSTA DE SKILL: nome-da-skill

* **Tipo de proposta:** CRIAR | ATUALIZAR
* **Nível da Skill:** 1 | 2 | 3 | 4
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Frase descritiva detalhada para ativação semântica da skill pelo LLM.
* **Estrutura de Diretórios:** Especificar pastas e arquivos auxiliares além do SKILL.md.
* **Necessidade:** Detalhar quais necessidades do ecossistema (Pasta projects) serão beneficiadas.
* **Recursos:** Detalhar os recursos a serem implementados.
* **Objetivo:** Detalhar o objetivo desta skill.
* **Casos de uso:** Detalhar os casos de uso práticos dentro do projeto.
* **Workflows:** Listar todos os workflows que farão uso desta skill.
* **Skills próprias utilizadas:** Listar as skills próprias (das pastas `created-skills/` e `created-skills-adonis/`) que esta skill fará uso direto durante sua execução, com breve descrição de como serão utilizadas.
* **Skills auxiliares:** Listar as skills de terceiros que auxiliarão a criação ou atualização.
* **Skills beneficiadas:** Listar as skills próprias que serão beneficiadas.
* **Benefícios:** Detalhar os benefícios envolvidos na elaboração desta skill.
```

### Exemplo Preenchido:

```markdown
# PROPOSTA DE SKILL: adonisjs-bullmq-queue-management-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, reviewing, or debugging background jobs and queues in AdonisJS v6 with BullMQ, configuring workers and queue connections, handling job retries, backoff and failures, or optimizing queue throughput. Triggers on job dispatch, queue config, retry/backoff logic, and worker monitoring.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp processa integrações com IA e relatórios em background via filas, necessitando de padrões claros para evitar falhas silenciosas.
* **Recursos:** Padrões de retry, backoff, rate limiting, chunking e monitoramento.
* **Objetivo:** Fornecer diretrizes sólidas para criação e manutenção de jobs e filas BullMQ no AdonisJS.
* **Casos de uso:** Jobs de processamento de IA, envio de notificações, geração de relatórios.
* **Workflows:** []
* **Skills próprias utilizadas:**
  - `adonisjs-best-practices` — Utilizará as convenções de comandos Ace e estrutura de serviços para padronizar dispatch e monitoramento dos jobs.
* **Skills auxiliares:** Nenhuma no momento.
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Redução de falhas silenciosas, melhor rastreabilidade e throughput das filas.
```

---

## FASE 3 — FINALIZAÇÃO DA PROPOSTA
1. Atualizar o arquivo `list-skills.yaml`, inserindo ou atualizando corretamente o item correspondente a esta proposta utilizando as instruções do arquivo `update-list.md`.
2. **Status inicial:** O item inserido deve ter o status `AGUARDANDO EXECUÇÃO`.
