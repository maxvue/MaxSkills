---
name: laravel-electrical-calculations-dimensioning-best-practices
description: Use when performing or validating electrical sizing, calculating circuit breakers, sizing cables, verifying voltage drop, or resolving inverter and solar module specifications. Triggers on calls to getWireSize, getCircuitBrake, getInverter, or when handling NBR 5410 electrical standards.
---

# Objetivo
Garantir a execução padronizada e precisa de dimensionamento elétrico, seleção de disjuntores, dimensionamento de cabos e busca de inversores dentro do Engeapp, aproveitando helpers globais e tabelas do banco de dados em vez de cálculos manuais ou valores hardcoded.

# Instruções
1. **Dimensionamento de Cabos (Wire Sizing):**
   - Sempre use o helper global `getWireSize($currents, $options)`.
   - NÃO implemente fórmula customizada de resistência de cobre/alumínio ou cálculo de queda de tensão.
   - Mapeie corretamente o parâmetro `$options`:
     - `material`: Passe `'copper'` ou `'aluminum'`.
     - `length`: Distância do cabo em metros.
     - `voltage`: Tensão de operação (ex: 220, 380, 127).
     - `phases`: Quantidade de fases (1, 2 ou 3).
     - `type_line`: Método de instalação da NBR 5410 (ex: `'B1'`, `'B2'`).
     - `cables`: Número de condutores carregados.
     - `max_percent`: Percentual aceitável de queda de tensão (padrão: 2% para monofásico, 3% para trifásico).
   - Ao validar um cabo pré-selecionado, forneça a opção `wire` ou `wire_target` para simular sua perda de potência e verificar a conformidade via `$result->permitido`.

2. **Seleção de Disjuntores:**
   - Sempre use o helper global `getCircuitBrake($currents, $limit_percent = 80)` (ou seu alias `getCircuitBraker`).
   - O primeiro parâmetro `$currents` pode ser um float, string ou array (se for array, seleciona a corrente máxima).
   - O `$limit_percent` especifica a capacidade máxima de carga (padrão é 80%).
   - Confie nessa função para encontrar o próximo valor comercial padrão de disjuntor disponível (ex: 10A, 13A, 16A, 20A, 25A, 32A, 40A, 50A, 63A, 80A, 100A, 125A).

3. **Dimensionamento e Busca de Inversores:**
   - Use o helper `getInverter($brand_name, $model, $power)` para buscar e retornar um model `App\Models\Equipment\Inverter` do banco de dados.
   - Evite query builders diretos no banco de dados para encontrar potência ou nome do modelo do inversor, a menos que a busca padrão do helper seja insuficiente.
   - Use `defaultAmountCircuitsMicroInverters($amount_micro_inverters, $max_inverter_group)` para distribuir microinversores uniformemente entre os circuitos.

4. **Conversões de Tensão e Fase:**
   - Use `toPhasePhase($voltage)` e `toPhaseNeutral($voltage)` ao converter entre tensões fase-fase e fase-neutro.
   - Use `voltageBetweenPhases($phase1, $phase2, $lag = 120)` para calcular a tensão de linha sob uma defasagem específica.
   - Mapeie strings de fase para números usando `getPhaseNumberByName($name)` e vice-versa usando `getPhaseName($number, $abbrev)`.
   - Use `getPoleName($numberPhases)` para determinar a descrição de polos correspondente (ex: Bipolar, Tripolar).

# Exemplos
### Cálculo de dimensionamento de cabo:
```php
$result = getWireSize(25.4, [
    'material' => 'copper',
    'length' => 30,
    'voltage' => 220,
    'phases' => 3,
    'type_line' => 'B1',
    'cables' => 3
]);

// $result conterá:
// - wire_size (ex: 6.0)
// - drop_voltage
// - efficiency
// - loss
```

### Simulação de conformidade de cabo:
```php
$result = getWireSize(40, [
    'material' => 'aluminum',
    'length' => 15,
    'voltage' => 220,
    'wire_target' => 10
]);
```

### Encontrando um disjuntor comercial:
```php
$breaker = getCircuitBrake([15.5, 24.2, 19.8], 80); // Retorna 32
```

## Restrições
- **Sem Cálculos Manuais:** Nunca deixe constantes de queda de tensão hardcoded (0.0172 ou 0.0283) nem escreva loops de fórmula customizados para encontrar seções de cabo. Sempre delegue ao `getWireSize`.
- **Cache do Banco de Dados:** Não limpe nem contorne os mecanismos de cache do `db_abnt_wire`. O helper cuida do cache automaticamente.
- **Tipagem Estrita:** Garanta que as correntes de entrada sejam convertidas ou casteadas apropriadamente antes de passá-las aos helpers. Se array ou null forem possíveis, deixe o helper normalizar ou tratar valores vazios de forma elegante (ex: retornando 0 ou null).
- **Normas:** Todos os cálculos devem estar alinhados à NBR 5410. Não invente valores customizados para disjuntores comerciais padrão.
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
