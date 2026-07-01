# PROPOSTA DE SKILL: laravel-ai-structured-outputs-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when defining, modifying, or testing structured JSON outputs for AI agents using the Laravel aiSDK. Triggers on classes implementing HasStructuredOutput, defining schema() methods, using Illuminate\Contracts\JsonSchema\JsonSchema, structuring nested JSON properties, validating AI returned structures, and handling JSON parsing fallbacks.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp extrai dados complexos de datasheets de inversores/módulos, boletos e documentos usando agentes de IA baseados no Laravel aiSDK. Atualmente, a falta de padrões rígidos para a definição de schemas JSON e validação do retorno estruturado do Gemini pode levar a falhas silenciosas de parse, dados ausentes em colunas de banco de dados e quebras de interface no front-end Vue 3.
* **Recursos:**
  - Padrões de escrita de esquemas JSON robustos com a interface `Illuminate\Contracts\JsonSchema\JsonSchema`.
  - Convenções de definição de campos obrigatórios (`required`) e descrições semânticas detalhadas (`description`) para mitigar erros do LLM.
  - Regras de tratamento de tipos específicos (números sem unidades, formatações de string e booleanos).
  - Padrões de fallback resilientes e gerenciamento de exceções caso a resposta estruturada falhe ou não atenda ao schema.
  - Testes de validação de schemas de saída usando Pest.
* **Objetivo:** Fornecer diretrizes sólidas e padronizadas para definição, modelagem de dados e validação de saídas estruturadas em JSON (Structured Outputs) retornadas pelo Gemini através do Laravel aiSDK.
* **Casos de uso:**
  - Extração de especificações elétricas e dimensionais de datasheets de equipamentos solares.
  - Leitura estruturada de dados de cabeçalho, código de barras e valores de boletos bancários.
  - Validação de dados pessoais e de concessionárias de energia a partir de documentos de identificação digitalizados.
* **Workflows:**
  - `agent-ai-create`
* **Skills próprias utilizadas:**
  - `laravel-ai-agent-creator` — Utilizará as diretrizes de arquitetura de agentes e atributos PHP 8 definidos nessa skill para construir agentes com saídas estruturadas.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-ai-agent-creator` — Será estendida com guias práticos para os agentes que retornam dados estruturados.
* **Benefícios:** Garantia de integridade de dados salvos no banco, redução de erros de parse em background, melhoria de UX no front-end por conta de payloads JSON determinísticos e maior facilidade para os desenvolvedores modelarem novos agentes.
