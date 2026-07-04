---
name: laravel-power-of-attorney-generation-best-practices
description: Use when creating, reviewing, or debugging Power of Attorney (procurações) generation logic, formatting client or partner addresses for legal documents, or generating PDFs for solar energy project concessionaires in the backend.
---

# laravel-power-of-attorney-generation-best-practices

## Objetivo
Fornecer diretrizes sólidas e padrões estruturados para criar, formatar e validar a lógica de geração de Procurações (Power of Attorney) e para formatar endereços de clientes ou sócios em documentos legais no backend Laravel.

## Instruções
1. **Mapeamento do Tipo de Cliente (PF vs PJ)**:
   - Sempre verifique o tipo da entidade do cliente (campo `entity`: `PF` ou `PJ`).
   - Para `PJ` (Pessoa Jurídica), inclua os dados da empresa (CNPJ, endereço), o nome do representante legal (`partner_name`), o documento do representante (`partner_document`) e o endereço de residência do representante (`partner_location`).
   - Para `PF` (Pessoa Física), inclua os dados do indivíduo (CPF, pronomes que consideram o gênero, endereço de residência).

2. **Formatação de Endereço**:
   - Use as relações `Location` e `Address` para compor strings de endereço limpas.
   - Formate os endereços padrão como: `[Rua], [Número], [Complemento (se existir)], [Bairro], município de [Cidade], CEP: [CEP]`.
   - Implemente fallbacks seguros (ex: usando um helper de conteúdo ou 'S/N' para números de casa/edifício ausentes).

3. **Gerenciamento de Status**:
   - Defina o status inicial do `ProjectPowerOfAttorneyDocument` como `editing` na criação.
   - Suporte as transições de status padrão no fluxo de assinatura: `editing`, `sent`, `delivered`, `opened`, `viewed`, `signed`.

4. **Geração de PDF e Integração de Assinatura**:
   - Use `Barryvdh\DomPDF\Facade\Pdf` para renderizar os templates HTML.
   - Suporte dois templates de PDF: `blank` (para assinatura física/manual) e `digital` (com blocos de assinatura digital usando frameworks legais como a Lei 14.063/2020 e links de validação).
   - Formate as datas dinamicamente usando um formato de data/hora localizado e traduzido (ex: `now()->translatedFormat(...)` em português).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO deixe fixos (hardcode) os dados regionais da concessionária ou do projetista (designer); sempre resolva-os através de relações (ex: `$project->concessionaire`, `$project->designer`).
- NÃO gere HTML com CPFs ou CNPJs crus e não formatados; sempre aplique funções helper de formatação/sanitização (ex: `formatCpfCnpj`).
- NÃO prossiga com a geração do PDF se campos cruciais de cliente/localização estiverem null; use verificações de validação para garantir dados limpos previamente.
