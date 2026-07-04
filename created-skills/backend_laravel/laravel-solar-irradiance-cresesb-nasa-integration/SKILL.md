---
name: laravel-solar-irradiance-cresesb-nasa-integration
description: Use when integrating with solar irradiance APIs (NASA POWER, CRESESB), fetching solar radiation indices by coordinates or ZIP code, or implementing photovoltaic energy generation estimation algorithms in Laravel. Triggers on requests involving solar radiation data, solar generation forecasting, or climatological data integrations.
---

# Integração de Irradiância Solar CRESESB & NASA no Laravel

## Objetivo
Padronizar a integração de APIs de irradiância solar (NASA POWER e CRESESB) e a implementação de cálculos de geração de energia solar no Laravel, garantindo cálculos precisos, arquitetura de serviços limpa e cache otimizado com Redis.

## Instruções

1. **Configuração dos Connectors (NASA POWER & CRESESB)**:
   - Implemente os connectors de integração HTTP em `app/Http/Integrations/SolarIrradiance/` (ex: `NasaPowerConnector.php`, `CresesbConnector.php`).
   - Estenda a classe connector nativa `BaseApi`, especificando o mapeamento de endpoints em `EndPoints.json` e a validação de inputs em `Attributes.json` de acordo com `laravel-api-integration-patterns`.
   - A configuração de endpoint do NASA POWER deve consultar dados de climatologia usando os parâmetros de latitude e longitude.
   - A integração com o CRESESB deve fazer o parse/fetch dos dados de radiação solar usando as coordenadas ou o código postal.

2. **Modelagem de Dados (Spatie Laravel Data)**:
   - Defina uma classe DTO `App\Data\SolarIrradianceData` estendendo `Spatie\LaravelData\Data` para representar os valores médios diários mensais de irradiação solar ($kWh/m²/dia$) de janeiro a dezembro:
     ```php
     namespace App\Data;

     use Spatie\LaravelData\Data;

     class SolarIrradianceData extends Data
     {
         public function __construct(
             public float $january,
             public float $february,
             public float $march,
             public float $april,
             public float $may,
             public float $june,
             public float $july,
             public float $august,
             public float $september,
             public float $october,
             public float $november,
             public float $december,
         ) {}
     }
     ```

3. **Estratégia de Cache Geográfico (Redis)**:
   - Para evitar chamadas redundantes a APIs externas e problemas de rate-limiting, implemente cache sobre as buscas por coordenadas.
   - Arredonde a latitude e a longitude para 2 casas decimais antes de gerar a chave de cache:
     ```php
     $roundedLat = round($latitude, 2);
     $roundedLon = round($longitude, 2);
     $cacheKey = "solar_irradiance:{$roundedLat}:{$roundedLon}";
     ```
   - Armazene as respostas no Redis usando a facade Cache do Laravel com um TTL longo (ex: 30 dias), já que a climatologia solar média mensal muda muito lentamente.

4. **Serviço de Cálculo Solar**:
   - Centralize os cálculos em `App\Services\SolarCalculationService` usando injeção de dependência:
     ```php
     namespace App\Services;

     use App\Data\SolarIrradianceData;

     class SolarCalculationService
     {
         /**
          * Calcula a geração de energia estimada para um mês específico.
          *
          * Fórmula: E = Pwp * Hday * days * PR
          */
         public function calculateMonthlyGeneration(
             float $installedCapacityKw,
             float $monthlyDailyAverageIrradiance,
             int $daysInMonth,
             float $performanceRatio = 0.80
         ): float {
             return $installedCapacityKw * $monthlyDailyAverageIrradiance * $daysInMonth * $performanceRatio;
         }
     }
     ```
   - Padronize o valor default do `performanceRatio` ($PR$) em $0.80$ (representando $20\%$ de perdas do sistema, incluindo eficiência do inversor, coeficientes de temperatura, cabeamento e sujeira/soiling).

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** faça chamadas HTTP diretas usando clientes brutos `Illuminate\Support\Facades\Http`. Todas as integrações devem herdar de `BaseApi`.
- **NÃO** use coordenadas não arredondadas nas chaves de cache. Coordenadas brutas levam a cache misses e esgotamento de recursos.
- **NÃO** deixe variáveis de cálculo como o Performance Ratio ($PR$) fixas globalmente no código sem permitir que o usuário ou a configuração do sistema as sobrescrevam dinamicamente.
- **NÃO** coloque transações de banco de dados ou lógica de persistência dentro dos connectors de integração.
