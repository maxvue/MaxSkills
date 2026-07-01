# PROPOSTA DE SKILL: laravel-ai-agent-creator

* **Tipo de proposta:** CRIAÇÃO
* **Necessidade:** O ecossistema Engeapp faz uso de Agentes de IA construídos com o Laravel aiSDK e necessita de um padrão rígido e documentado para criar, manter e testar esses agentes (conforme definido na pasta app/Ai e nos comandos customizados), garantindo coesão no uso de configurações de LLM e ferramentas.
* **Recursos:** Padrões de definição de atributos obrigatórios (`#[Provider]`, `#[Model]`, `#[Temperature]`, etc.), implementação de interfaces (`HasTools`, `HasStructuredOutput`), modelos de uso do bloco HereDoc para as instruções em texto, integração com Jobs e a trait `HasAgentAiRequest`.
* **Objetivo:** Fornecer diretrizes padronizadas e rigorosas de código para a criação de classes de agentes de IA baseados no Laravel aiSDK.
* **Casos de uso:** Criação de um novo subagente de inteligência artificial para automatizar tarefas internas, integração estruturada com novos LLMs ou processamento em background de interações de IA.
* **Workflows:** agent-ai-create
* **Lista de workflows:**
  - `agent-ai-create`: Workflow principal que guiará a criação prática dos agentes fazendo uso das regras definidas nesta skill.
* **Skills auxiliares:**
  - `laravel-specialist`
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Maior organização, consistência na injeção de dependências e prevenção de falhas de timeout, limite de tokens e inconsistências nas instruções aos provedores LLMs.
