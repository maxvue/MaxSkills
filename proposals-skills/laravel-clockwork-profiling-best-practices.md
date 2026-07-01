# PROPOSTA DE SKILL: laravel-clockwork-profiling-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
* **Wake Word (YAML Description):** Use when configuring, integrating, or utilizing the Clockwork profiling tool (itsgoingd/clockwork) in Laravel to debug HTTP requests, database queries, memory usage, cache performance, and custom timeline logs. Triggers on clockwork settings, custom profiling block implementations, and performance optimizations using Clockwork telemetry data.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp possui rotinas de processamento complexas, como análise de datasheets com IA e cálculos de dimensionamento elétrico, que necessitam de depuração fina de performance em desenvolvimento. O Clockwork viabiliza telemetria detalhada de banco de dados, requisições HTTP e memória através de ferramentas de console ou extensões de navegador de forma leve.
* **Recursos:**
  - Configuração do Middleware Clockwork para monitoramento de rotas HTTP.
  - Implementação de monitoramento de performance com cronômetros customizados (`clockwork()->startEvent()`, `clockwork()->endEvent()`).
  - Análise de queries executadas, cache performance e consumo de memória.
  - Proteção de segurança para desativação completa do Clockwork em ambiente de produção (`CLOCKWORK_ENABLE=false`).
* **Objetivo:** Fornecer diretrizes e padrões consistentes para depuração, profiling e otimização de performance no Laravel utilizando o Clockwork no ecossistema Engeapp.
* **Casos de uso:**
  - Monitorar o tempo gasto na extração de texto de PDF de faturas de concessionárias.
  - Rastrear consultas N+1 executadas durante o carregamento de listagens complexas de homologação.
  - Identificar picos de consumo de memória durante o dimensionamento elétrico em lote.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizará os padrões de manipulação de exceções para integrar alertas críticos nos logs do Clockwork.
  - `laravel-services-best-practices` — Padronizará a injeção do profiling do Clockwork dentro dos Services de integração.
* **Skills auxiliares:** laravel-specialist
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Detecção ágil de gargalos de processamento local, melhoria no tempo de resposta das requisições e redução de vazamento de memória em rotinas complexas.
