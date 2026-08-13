---
name: laravel-power-of-attorney-generation-best-practices
description: "Use when creating, reviewing, or debugging Power of Attorney PDF generation in Laravel via PowerAttorneyService, formatting legal addresses, and rendering DomPDF documents. Covers document generation and DomPDF rendering."
---
# laravel-power-of-attorney-generation-best-practices

## Objetivo
Fornecer diretrizes sólidas e padrões estruturados para criar, formatar e validar a lógica de geração de Procurações (Power of Attorney) e para formatar endereços de clientes ou sócios em documentos legais no backend Laravel.

## Ponto de entrada (código real)
Toda a lógica vive em `App\Services\Signature\PowerAttorneyService` (`app/Services/Signature/PowerAttorneyService.php`), operando sobre o modelo `App\Models\Project\ProjectPowerOfAttorneyDocument`. Ancore qualquer alteração nestes três métodos — abra-os antes de editar:
- `generateData(string $project_id): ProjectPowerOfAttorneyDocument` — carrega o `Project` com as relações necessárias, define `type_signature = 'digital'` e `status = 'editing'`, monta o `text_content` (HTML) conforme PF/PJ e persiste o documento.
- `getAddress(?Location $location): ?string` — helper que compõe a string de endereço a partir de `location.address.cep.city`; retorna `null` se a cidade não existir.
- `createPdf(ProjectPowerOfAttorneyDocument $power_of_attorney, string $type_document): File` — renderiza o HTML em PDF (DomPDF), salva no disco remoto do projeto e cria o registro `File`.

## Instruções
1. **Mapeamento do Tipo de Cliente (PF vs PJ)**:
   - Sempre verifique o tipo da entidade do cliente (campo `entity`: `PF` ou `PJ`).
   - Para `PJ` (Pessoa Jurídica), inclua os dados da empresa (CNPJ, endereço), o nome do representante legal (`partner_name`), o documento do representante (`partner_document`) e o endereço de residência do representante (`partner_location`).
   - Para `PF` (Pessoa Física), inclua os dados do indivíduo (CPF, pronomes que consideram o gênero, endereço de residência).

2. **Formatação de Endereço (`getAddress`)**:
   - Use as relações `Location` → `Address` → `cep` → `city` para compor strings de endereço limpas (padrão adotado em `getAddress`).
   - Formate os endereços padrão como: `[Rua], [Número], [Complemento (se existir)], [Bairro], município de [Cidade], CEP: [CEP]`.
   - Implemente fallbacks seguros: use o helper `getContent(...)` e o literal `'S/N'` para números de casa/edifício ausentes (ver `getAddress`).

3. **Formatação de Data (`generateData`)**:
   - Em `generateData`, formate a data do rodapé usando `now()->translatedFormat('l, d \\d\\e F \\d\\e Y')`, concatenada com a cidade do projeto.

4. **Gerenciamento de Status**:
   - Em `generateData`, defina o status inicial do `ProjectPowerOfAttorneyDocument` como `editing` e `type_signature` como `digital`.
   - Suporte as transições de status padrão no fluxo de assinatura: `editing`, `sent`, `delivered`, `opened`, `viewed`, `signed`.

5. **Geração de PDF e Integração de Assinatura (`createPdf`)**:
   - Use `Barryvdh\DomPDF\Facade\Pdf` (`Pdf::loadHTML(...)`) para renderizar o HTML.
   - O modo do PDF é decidido apenas pelo parâmetro `string $type_document`: o único valor literal testado no código é `'digital'` (renderiza os blocos de assinatura digital com a Lei 14.063/2020 e o link `https://validar.iti.gov.br`, e grava `Procuração Digital - Aguardando Validação.pdf`). QUALQUER outro valor cai no ramo físico/manual (linhas de assinatura em branco, arquivo `Procuração - Em Branco.pdf`). Por convenção, o controller chama `createPdf` com o literal `'blank'` para o modo físico — essa string existe e é usada, mas o service não a trata de forma especial: ele só verifica se o valor é diferente de `'digital'`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO deixe fixos (hardcode) os dados regionais da concessionária ou do projetista (designer); sempre resolva-os através de relações (ex: `$project->concessionaire`, `$project->designer`). Nota: o `generateData()` atual ainda viola isso — usa fallbacks fixos para `designer_name`/`designer_document` e grava o endereço do projetista como string totalmente literal em vez de resolvê-lo por relação; trate como débito técnico a corrigir, não como padrão a seguir.
- NÃO gere HTML com CPFs ou CNPJs crus e não formatados; sempre aplique funções helper de formatação/sanitização (ex: `formatCpfCnpj`).
- NÃO prossiga com a geração do PDF se campos cruciais de cliente/localização estiverem null; use verificações de validação para garantir dados limpos previamente.
