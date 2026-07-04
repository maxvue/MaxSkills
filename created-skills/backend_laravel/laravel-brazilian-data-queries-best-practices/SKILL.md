---
name: laravel-brazilian-data-queries-best-practices
description: Use when designing, implementing, or debugging services that query Brazilian corporate and postal data (CNPJ and CEP). Triggers on third-party API integration (ViaCep, ReceitaWS, BrasilAPI, CepAberto), handling fallback mechanisms, normalizing responses, and caching address or registry data.
---

# Boas Práticas de Consultas a Dados Brasileiros no Laravel

## Objetivo
Fornecer diretrizes sólidas, estratégias de fallback resilientes, padrões de tratamento de erros, normalização de respostas e mecanismos de cache para integrar consultas a APIs postais (CEP) e corporativas (CNPJ) brasileiras em aplicações Laravel dentro do ecossistema Engeapp.

## Instruções

### 1. Diretrizes de Consulta de CEP (Código de Endereçamento Postal)

#### A. Estratégia de Fallback Resiliente
Sempre tente consultar os serviços de CEP na seguinte ordem:
1. **ViaCEP**: Confiável, gratuito, mas pode apresentar latência.
2. **BrasilAPI**: Rápido, agrega múltiplas fontes internamente.
3. **AwesomeAPI**: Backup secundário gratuito e responsivo.

Implemente uma classe de serviço ou action (ex: `GetAddressFromCepAction`) que itere por esses provedores quando ocorrer um erro de conexão ou de servidor.

#### B. Estratégia de Cache
Para otimizar a performance e respeitar os limites das APIs:
- Armazene consultas bem-sucedidas no cache por **90 dias (3 meses)**.
- Use uma chave de cache estruturada: `brazilian-queries:cep:{cep}`.
- Exemplo de implementação:
  ```php
  use Illuminate\Support\Facades\Cache;
  use Illuminate\Support\Facades\Http;

  $cepClean = preg_replace('/[^0-9]/', '', $cep);

  $address = Cache::remember("brazilian-queries:cep:{$cepClean}", now()->addMonths(3), function () use ($cepClean) {
      return $this->queryCepWithFallbacks($cepClean);
  });
  ```

#### C. Normalização de Respostas
Independentemente da API utilizada, mapeie a resposta para uma estrutura padrão:
```php
[
    'cep'          => '01001-000',
    'street'       => 'Praça da Sé',
    'neighborhood' => 'Sé',
    'city'         => 'São Paulo',
    'state'        => 'SP',
    'ibge_code'    => '3550308',
]
```

---

### 2. Diretrizes de Consulta de CNPJ (Registro Corporativo)

#### A. Ordem de Fallback & Limites de Taxa
Consulte os serviços de CNPJ na seguinte sequência:
1. **BrasilAPI (CNPJ)**: Opção principal e estável usando dados públicos da Receita Federal.
2. **ReceitaWS**: Bom fallback, mas possui um limite de taxa de 3 consultas por minuto no plano gratuito. Garanta que você capture e trate códigos de status 429.

#### B. Cache e Persistência em Banco Local
- Faça cache das respostas da API por **90 dias (3 meses)** usando `brazilian-queries:cnpj:{cnpj}`.
- Para fluxos críticos de negócio, armazene os dados de registro permanentemente em uma tabela `companies` no banco de dados local. Verifique essa tabela antes de realizar qualquer requisição a uma API externa.

#### C. Normalização de Respostas
Normalize as respostas de CNPJ para um formato consistente:
```php
[
    'cnpj'         => '00.000.000/0001-91',
    'legal_name'   => 'BANCO DO BRASIL SA',
    'trade_name'   => 'BANCO DO BRASIL',
    'status'       => 'ATIVA',
    'opening_date' => '1808-10-12', // formato Y-m-d
    'address'      => [
        'street'       => 'SBS Quadra 1 Bloco G Lote 32',
        'number'       => '32',
        'complement'   => 'Lote 32',
        'neighborhood' => 'Asa Sul',
        'city'         => 'Brasília',
        'state'        => 'DF',
        'cep'          => '70070-110',
    ]
]
```

---

### 3. Tratamento de Exceções & Logging
- Siga as diretrizes em `laravel-exception-handling-logging`.
- Envolva requisições HTTP externas em blocos `try/catch` direcionados a `Illuminate\Http\Client\RequestException` e `Illuminate\Http\Client\ConnectionException`.
- Registre falhas usando a facade `Log`:
  ```php
  use Illuminate\Support\Facades\Log;

  Log::warning("CEP API provider failed. Attempting fallback.", [
      'provider' => 'viacep',
      'cep' => $cep,
      'error' => $exception->getMessage()
  ]);
  ```
- Lance uma exceção customizada `BrazilianDataQueryException` apenas quando todos os provedores de API falharem.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** execute requisições cURL brutas diretamente; sempre use o cliente `Http` do Laravel.
- **NÃO** armazene endpoints de API ou credenciais diretamente no código; gerencie-os via valores de `config()` mapeados para o `.env`.
- **NÃO** realize requisições a APIs externas dentro de loops. Implemente cache ou processamento em blocos (chunking).
- **NÃO** ignore os limites de taxa dos planos gratuitos (ex: ReceitaWS 3 requisições/minuto). Verifique os códigos de status e aplique delays ou fallback imediatamente.
