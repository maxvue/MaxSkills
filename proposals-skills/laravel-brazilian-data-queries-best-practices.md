# PROPOSTA DE SKILL: laravel-brazilian-data-queries-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when designing, implementing, or debugging services that query Brazilian corporate and postal data (CNPJ and CEP). Triggers on third-party API integration (ViaCep, ReceitaWS, BrasilAPI, CepAberto), handling fallback mechanisms, normalizing responses, and caching address or registry data.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp consome dados cadastrais públicos brasileiros em diversas partes da aplicação. A ausência de regras estritas de resiliência (fallbacks) contra falhas de APIs externas e um cacheamento inconsistente de consultas recorrentes sobrecarregam a rede e geram problemas na experiência do usuário.
* **Recursos:** Estratégia de fallbacks sucessivos entre múltiplas APIs de consulta brasileiras (ViaCep, OpenCep, BrasilAPI, AwesomeAPI, ReceitaWS, OpenCNPJ e CnpjAberto), padronização de tratamento de erros, normalização dos retornos de dados cadastrais (ex: estrutura padrão de endereço e status de CNPJ) e políticas de cache temporário (3 meses) e permanente em banco de dados local.
* **Objetivo:** Fornecer diretrizes robustas para a integração segura, performática e tolerante a falhas de APIs brasileiras de CEP e CNPJ no Laravel.
* **Casos de uso:** Auto-preenchimento de endereços em formulários a partir do CEP inserido, obtenção automatizada de dados corporativos ao digitar o CNPJ da empresa, e contingência imediata de rede quando as APIs primárias de consulta falharem.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-exception-handling-logging` — Utilizada para estruturar os logs de falhas das chamadas externas e fallbacks das APIs brasileiras de CEP e CNPJ.
  - `laravel-cache-best-practices` — Utilizada para gerenciar a expiração e geração de chaves únicas do cache dos retornos das APIs no Redis ou repositório padrão.
* **Skills auxiliares:** laravel-expert, php-pro
* **Skills beneficiadas:**
  - `laravel-base-api-integration-patterns` — A nova skill estende os padrões de consumo de APIs externas aplicando regras específicas para serviços públicos brasileiros.
* **Benefícios:** Maior disponibilidade do serviço de consulta de CEP e CNPJ devido aos fallbacks, economia de consumo de quotas de APIs pagas graças ao cache de 3 meses, e consistência de dados normalizados de endereços e cadastros salvos.
