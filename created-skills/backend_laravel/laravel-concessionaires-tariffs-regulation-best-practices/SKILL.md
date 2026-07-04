---
name: laravel-concessionaires-tariffs-regulation-best-practices
description: Use when creating, modifying, or querying energy concessionaires (concessionárias), subsidiaries, regional units, electrical regulations (ANEEL rules), or tariff data (group A/B, green/blue tax flags, TUSD/TE distribution tariffs) in Laravel. Triggers on calculations involving power distribution costs, energy concessionaire CRUDs, and regulation data validations.
---

# Boas Práticas de Concessionárias de Energia, Tarifas e Regulação

## Objetivo
Estabelecer padrões limpos, consistentes e arquiteturalmente sólidos para o gerenciamento de concessionárias de energia (distribuidoras), suas subsidiárias, tarifas locais e regulações da ANEEL (Agência Nacional de Energia Elétrica) no backend Laravel do Engeapp. Isso garante cálculos precisos de viabilidade financeira (payback, economia) para projetos solares e evita discrepâncias fiscais ou de lógica.

## Instruções

### 1. Estrutura de Models e Relacionamentos
Mantenha claro o mapeamento hierárquico das concessionárias de energia:
- **ConcessionaireCompany**: Representa a holding corporativa (ex: Energisa, Equatorial). Usa ULIDs (`HasUlids`), mapeia para `concessionaires_company`.
- **ConcessionaireSubsidiary**: Representa as unidades operacionais regionais (ex: Energisa Sul-Sudeste). Herda ULIDs, mapeia para `concessionaires_subsidiaries`. Abriga locais de atendimento (cidades, estados), urls e templates de configuração (como templates de placa: `placa1`, `placa2`).
- **ConcessionaireSubsidiaryRegulation**: Define os padrões técnicos, classes de conexão, tensão e fases. Mapeia para `concessionaires_subsidiaries_regulations`. Inclui relacionamentos com arquivos e limites de dados.
- **ConcessionaireSubsidiaryRegulationData**: Parâmetros granulares (limite de disjuntor, seções de condutores, tensão fase-neutro). Ordene os resultados globalmente por `circuit_breaker` usando boot hooks.

### 2. Padrões de DTO e Validação (Spatie Laravel Data)
Ao validar ou transferir payloads de configuração de tarifas, use DTOs do Spatie Laravel Data:
- Agrupe as estruturas de tarifa em categorias distintas:
  - **Grupo A (Alta Tensão)**: Consumidores de alta tensão. Exigem campos para tarifa de ponta, tarifa de fora de ponta e cobranças de demanda (demanda contratada). Garanta que os componentes TUSD e TE sejam validados separadamente.
  - **Grupo B (Baixa Tensão)**: Consumidores convencionais de baixa tensão (residencial, comercial, rural). Exigem campos para TUSD de tarifa única, TE e taxas de iluminação pública (COSIP/CIP).
- Valide os campos regulatórios brasileiros usando regras estritas:
  - Configurações de fase (`amount_phases`: 1, 2 ou 3).
  - Valores de tensão (`voltage_phase_neutral`: tipicamente 127V ou 220V).

### 3. Cálculos de Tarifa e Representação Monetária
- **Sem Float para Dinheiro**: Todos os cálculos de tarifa (TUSD, TE, custos de demanda, bandeiras tarifárias) devem evitar operações brutas de ponto flutuante. Use valores inteiros representando centavos (R$ 0,01 = 1) ou decimais de alta precisão (ex: wrapper `BCMath`) com até 4 ou 6 casas decimais (as tarifas no Brasil são definidas com 4-6 decimais, ex: R$ 0,654321 / kWh).
- **Separe TUSD e TE**: Distribuição (TUSD - Tarifa de Uso do Sistema de Distribuição) e Energia (TE - Tarifa de Energia) devem ser tratados como componentes independentes. Eles têm tratamentos fiscais diferentes (ICMS, PIS, COFINS) e taxas de compensação regulatória diferentes.
- **Bandeiras Tarifárias**: Implemente um serviço para recuperar ou aplicar as bandeiras tarifárias ativas da ANEEL (Verde, Amarela, Vermelha Patamar 1, Vermelha Patamar 2) sobre o componente TE.
- **Regras de Compensação de GD**: Cálculos de payback para Geração Distribuída devem respeitar as regulações ativas da ANEEL (ex: regras de transição da Lei 14.300, cobranças do TUSD Fio B).

### 4. Separação de Responsabilidades
- **Sem Lógica de Cálculo em Models**: Os models Eloquent devem representar apenas a estrutura do banco de dados e os relacionamentos.
- **Actions / Service Classes**: Coloque cálculos de payback, aplicações de tarifa e modelos de compensação da ANEEL dentro de service classes específicas (ex: `App\Services\Financial\PaybackCalculatorService`).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** use floats brutos para colunas de banco de dados que armazenam tarifas ou totais monetários. Use `decimal(12, 6)` ou `integer` representando centavos.
- **NÃO** faça hardcode de taxas TUSD/TE dentro de controllers ou services. Sempre busque-as no banco de dados ou nos arrays de config do DTO associados à `ConcessionaireSubsidiary` do cliente.
- **NÃO** duplique a lógica de cálculo entre controllers. Centralize em classes Service/Action.
- **NUNCA** realize operações brutas de banco de dados sem transações ao atualizar múltiplas configurações de tarifa de concessionária de uma só vez.
