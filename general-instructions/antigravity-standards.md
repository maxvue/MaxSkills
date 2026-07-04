# Padrões Oficiais de Skills Google Antigravity

Este arquivo documenta as melhores práticas de arquitetura e estrutura para o desenvolvimento de Skills no ecossistema Google Antigravity, baseadas nas diretrizes oficiais (Codelabs).

## Estrutura Obrigatória (SKILL.md)
Toda skill **deve** conter um arquivo principal `SKILL.md` com as seguintes características:

1. **YAML Frontmatter (A "Wake Word")**: 
   Todo arquivo `SKILL.md` deve iniciar com um bloco YAML delimitado por `---` contendo obrigatoriamente:
   - `name`: Nome da skill (kebab-case, ex: `banco-de-dados`).
   - `description`: O campo MAIS IMPORTANTE. Serve como gatilho semântico (wake word) para o agente. Deve ser extremamente descritivo detalhando exatamente quando e por que o agente deve usar essa skill.

2. **Corpo em Markdown Obrigatório**:
   Após o frontmatter, o markdown deve ter seções claras:
   - **Goal:** Declaração concisa do que a skill faz.
   - **Instructions:** Passo a passo detalhado para o agente realizar a tarefa.
   - **Examples (Opcional):** Demonstrações de uso de "few-shot".
   - **Constraints:** Restrições claras sobre o que o agente NÃO deve fazer (regras negativas de segurança). A primeira bullet desta seção é **sempre obrigatória e fixa em todas as skills**: o idioma padrão de conversação Agente↔Humano é **Português (pt-BR), sempre, sem exceção**, independentemente do idioma em que o corpo da skill foi escrito (EN em `created-skills/`, PT em `created-skills-pt-br/`). Essa regra rege como o agente fala com o usuário, não como a skill é redigida.

## Níveis de Arquitetura de Skills (Divulgação Progressiva)

Para evitar inflação no contexto e "alucinações" do LLM, as skills devem ser estruturadas baseadas na sua complexidade em diferentes Níveis:

* **Nível 1 (Básico):**
  Apenas o arquivo `SKILL.md`. Usado para instruções simples e conceituais de uso geral.

* **Nível 2 (Utilização de Recursos - `resources/` ou `references/`):**
  Quando a skill exige a injeção de textos estáticos muito grandes (ex: Templates de Contrato, Cabeçalhos de Licença Legal, grandes blocos Boilerplate).
  - O texto não deve ficar dentro do `SKILL.md`.
  - Crie uma pasta `resources/` com arquivos `.txt` ou `.md` contendo o conteúdo. O agente lerá este arquivo apenas quando for utilizar a skill.

* **Nível 3 (Aprendizado por Exemplo - `examples/`):**
  Quando a skill converte ou formata padrões exatos (ex: Converter JSON para uma tipagem estrita no Backend).
  - Explicar tudo no prompt é ineficaz. LLMs operam melhor com correspondência de padrões.
  - Crie uma pasta `examples/` contendo arquivos com o estado de entrada (`input_data.json`) e o estado desejado (`output_model.py`).

* **Nível 4 (Lógica Procedural - `scripts/`):**
  Quando a skill precisa validar estados externos, executar algoritmos complexos não triviais ao LLM, ou lidar com ações perigosas no sistema (ex: Executar dump de banco de dados).
  - Crie uma pasta `scripts/` com arquivos Bash (`.sh`), Python (`.py`), Node (`.js`), etc.
  - No `SKILL.md`, instrua o Agente a utilizar a tool `run_command` para executar estes scripts quando a skill for ativada.
