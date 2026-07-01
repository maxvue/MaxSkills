# PROPOSTA DE SKILL: laravel-qrcode-generation-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when generating, customizing, rendering, or testing QR Codes in the Laravel backend using endroid/qr-code. Triggers on QR Code generation, SVG/PNG outputs, base64 encoding for APIs/Blade, and adding logos or labels to QR Codes.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp processa emissões de cobranças Pix e boletos híbridos que exigem a exibição e geração dinâmica de QR Codes customizados de alta qualidade, garantindo leitura rápida e compatibilidade.
* **Recursos:** Geração de QR Codes nos formatos PNG e SVG, inclusão de logos customizados e labels textualizadas, renderização direta em formato Base64 para integração com APIs ou views Blade, otimização por cacheamento e escrita de testes automatizados.
* **Objetivo:** Fornecer diretrizes sólidas e padrões estruturados para a geração, customização, renderização e testes de QR Codes utilizando o pacote endroid/qr-code no backend Laravel.
* **Casos de uso:** Exibição de QR Codes para pagamentos Pix, compartilhamento rápido de links para propostas comerciais, geração de códigos para download de aplicativos e links para autenticação.
* **Workflows:** [bug-fix-back-end]
* **Skills próprias utilizadas:**
  - `laravel-pest-testing-best-practices` — Utilizará os padrões e melhores práticas de escrita de testes com Pest para validar a integridade da geração e renderização do QR Code.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** laravel-inter-payments-integration, laravel-efi-payments-integration
* **Benefícios:** Padronização completa na geração de QR Codes no ecossistema Engeapp, facilitação de integrações com gateways de pagamento Pix e boletos e ampla testabilidade através do Pest.
