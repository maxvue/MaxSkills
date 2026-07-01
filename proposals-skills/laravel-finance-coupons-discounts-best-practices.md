# PROPOSTA DE SKILL: laravel-finance-coupons-discounts-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
  - Nível 1: Apenas SKILL.md (básica)
  - Nível 2: Requer pasta `resources/` (textos pesados/templates)
  - Nível 3: Requer pasta `examples/` (inputs/outputs de few-shot)
  - Nível 4: Requer pasta `scripts/` (lógicas delegadas Bash/Python/Node)
* **Wake Word (YAML Description):** Use when creating, modifying, applying, or validating discount coupons (cupons de desconto), referral usage rules, or financial discounts (descontos financeiros) in Laravel. Triggers on coupon validation logic, payment discount adjustments, coupon-project associations, and discount expiration checks.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp oferece cupons de desconto para integradores e clientes reduzirem os custos de faturas ou taxas de projetos. A lógica de cupons envolve restrições complexas: data de validade, limites de uso globais, limites por integrador/empresa solar, e escopo de usuários. É vital ter padrões técnicos claros no backend Laravel para garantir a segurança dessas operações, prevenindo resgates indevidos ou duplicados.
* **Recursos:** Estrutura e padrões para validação de cupons (active, expired, limit_use, reference_use), registro de histórico de uso com `FinanceDiscountsCouponUse`, tratamento seguro de transações financeiras ao aplicar cupons para evitar race conditions de resgate concorrente, e integração com relacionamentos Eloquent (Project, Payments).
* **Objetivo:** Estabelecer diretrizes e padrões de melhores práticas para criação, validação, aplicação segura e auditoria de cupons de desconto e descontos financeiros no ecossistema Engeapp/Laravel.
* **Casos de uso:** Implementação e validação de cupons de desconto ao finalizar a compra/checkout de projetos, verificação automática de limites de uso por integrador solar, aplicação de descontos condicionais em cobranças de parcelas de projetos, e rastreamento e auditoria de cupons aplicados por meio de logs/relatórios financeiros.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-code-generators-best-practices` — Utilizará as convenções de models Eloquent para gerenciar os relacionamentos entre FinanceDiscountCoupons, FinanceDiscountsCouponUse e Payments/Project.
  - `laravel-database-transactions-concurrency` — Utilizará as regras de transação e lock de banco para evitar double-spending ou race condition de uso concorrente de cupons de desconto no checkout.
  - `laravel-brazilian-localization-best-practices` — Utilizará as regras de precisão decimal do BRL para aplicar e descontar valores percentuais ou fixos sem erros de arredondamento centesimal.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:**
  - `laravel-api-idempotency-best-practices` — Será beneficiada por garantir que requisições repetidas de checkout com cupom não gerem múltiplos descontos ou utilizações espúrias.
* **Benefícios:** Eliminação de brechas de uso indevido de cupons, cálculos de descontos financeiros consistentes sem discrepâncias de centavos, código modular, legível e altamente testável para a área de faturamento e cupons da plataforma.
