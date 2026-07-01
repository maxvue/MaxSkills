# PROPOSTA DE SKILL: laravel-global-helpers-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when creating, modifying, refactoring, or testing global helper functions (Helpers) or utility classes in the Laravel backend. Triggers on helper autoload, global function declarations, and custom utility utilities.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp possui 18 arquivos de helpers globais autocarregados via composer.json, gerando potenciais problemas de colisão de nomes, inconsistências de nomenclatura (como NumbersHelpers.php vs. numbersHelper.php), falta de encapsulamento e riscos de vazamento de estado sob o ciclo de vida persistente do Laravel Octane.
* **Recursos:** Convenções de nomenclatura de arquivos e funções; obrigatoriedade de proteção de declarações de funções globais com wrapper `function_exists`; uso estratégico de classes utilitárias estáticas (Utility classes) sob namespaces em vez de funções globais para melhor autocompletação de IDE; diretrizes de statelessness sob Laravel Octane; e padronização de testes de helpers com o Pest.
* **Objetivo:** Padronizar a criação e manutenção de helpers globais e classes utilitárias no Engeapp, assegurando código limpo, modular, stateless e 100% testado.
* **Casos de uso:** Criação de novos utilitários de manipulação de dados (formatação elétrica, strings, CPF/CNPJ, bancos), refatoração de helpers legados duplicados ou com lógica quebrada e depuração de conflitos no escopo global.
* **Workflows:**
  - `bug-fix-back-end`
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizará as diretrizes de testes unitários do Pest para estruturar asserções limpas e isoladas das funções utilitárias.
* **Skills auxiliares:** laravel-specialist, php-clean-code
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Eliminação de erros de colisão em ambiente produtivo, facilidade de autocompletação da IDE por meio de namespaces, prevenção de memory leaks sob Laravel Octane, melhor cobertura de testes unitários e organização coerente de arquivos utilitários no projeto.
