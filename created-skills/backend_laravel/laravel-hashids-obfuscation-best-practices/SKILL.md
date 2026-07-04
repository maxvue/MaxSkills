---
name: laravel-hashids-obfuscation-best-practices
description: Use when implementing, configuring, or debugging ID obfuscation in Laravel Eloquent models, API routes, or controllers using the vinkla/hashids package. Triggers on route model binding customization, ID masking in API resources, and database ID obfuscation/decoding.
---

# Objetivo
Estabelecer padrões robustos e consistentes para ofuscação de IDs de banco de dados usando o pacote `vinkla/hashids` no backend Laravel. Isso protege IDs sequenciais do banco (chaves primárias auto-incrementadas) contra exposição pública em URLs e respostas de API, mitigando coleta de dados (scraping) e vulnerabilidades de Insecure Direct Object Reference (IDOR), enquanto preserva a performance do banco de dados.

# Instruções

## 1. Configuração do Pacote
- Verifique os valores de configuração em `config/hashids.php`.
- Defina um salt seguro e único para a aplicação. NÃO deixe o salt hardcoded; carregue-o do arquivo `.env` via `config('hashids.connections.main.salt')`.
- Mantenha um comprimento mínimo para os hashes gerados (ex: `12` ou `16` caracteres) para evitar brute-force.

## 2. A Trait `HasHashid`
- Crie uma trait reutilizável `App\Traits\HasHashid` para models Eloquent que exigem ofuscação de ID.
- Implemente um accessor de atributo `hashid` usando a facade `Hashids` para codificar a chave primária do model.
- Sobrescreva os métodos nativos `getRouteKeyName` e `getRouteKey` para usar o hashid customizado no Route Model Binding implícito.
- Sobrescreva o método `resolveRouteBinding` para decodificar o hashid com segurança e realizar uma consulta no banco de dados. Se o hash for inválido ou não puder ser decodificado, lance uma `ModelNotFoundException` para retornar automaticamente uma resposta `404 Not Found`.

## 3. Integração com API Resources e DTOs
- Ao exportar atributos do model via Eloquent API Resources, substitua o `id` cru do banco pela string ofuscada `hashid`.
- Se estiver usando `laravel-data` para Data Transfer Objects (DTOs), defina as propriedades de identificador como `string` e preencha-as com o `hashid` do model.
- Garanta que as definições TypeScript derivadas dos DTOs representem corretamente essas propriedades como `string` para corresponder às expectativas do frontend.

## 4. Validação de Entrada e Form Requests
- Para validar hashids recebidos, implemente uma regra de validação customizada (ex: `ValidHashid`) ou decodifique o hashid inline dentro do Form Request antes de prosseguir para a lógica do controller.
- Evite passar strings de hashid cruas para consultas internas ao banco de dados. Sempre decodifique o valor para sua representação inteira antes de executar consultas.

# Exemplos

### Implementação de Model usando a Trait `HasHashid`
```php
<?php

namespace App\Traits;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Vinkla\Hashids\Facades\Hashids;

trait HasHashid
{
    /**
     * Retorna o nome da route key para o model.
     */
    public function getRouteKeyName(): string
    {
        return 'hashid';
    }

    /**
     * Retorna o valor da route key (o hashid codificado).
     */
    public function getRouteKey(): string
    {
        return $this->hashid;
    }

    /**
     * Accessor para o atributo hashid.
     */
    public function getHashidAttribute(): string
    {
        return Hashids::connection($this->getHashidsConnectionName())->encode($this->getKey());
    }

    /**
     * Resolve o route model binding implícito.
     *
     * @param mixed $value
     * @param string|null $field
     * @return Model|null
     *
     * @throws ModelNotFoundException
     */
    public function resolveRouteBinding($value, $field = null): ?Model
    {
        // Decodifica apenas ao resolver por hashid
        if ($field === 'hashid' || (is_null($field) && $this->getRouteKeyName() === 'hashid')) {
            $decoded = Hashids::connection($this->getHashidsConnectionName())->decode((string) $value);

            if (empty($decoded)) {
                throw (new ModelNotFoundException())->setModel(get_class($this));
            }

            return $this->where($this->getKeyName(), $decoded[0])->firstOrFail();
        }

        return parent::resolveRouteBinding($value, $field);
    }

    /**
     * Retorna o nome da conexão Hashids associada a este model.
     */
    protected function getHashidsConnectionName(): string
    {
        return 'main';
    }
}
```

### Regra de Validação Customizada para Validação de Request
```php
<?php

namespace App\Rules;

use Closure;
use Illuminate\Contracts\Validation\ValidationRule;
use Vinkla\Hashids\Facades\Hashids;

class ValidHashid implements ValidationRule
{
    /**
     * Cria uma nova instância da regra.
     *
     * @param class-string<\Illuminate\Database\Eloquent\Model> $modelClass
     */
    public function __construct(
        protected string $modelClass,
        protected string $connection = 'main'
    ) {}

    /**
     * Executa a regra de validação.
     */
    public function validate(string $attribute, mixed $value, Closure $fail): void
    {
        if (!is_string($value)) {
            $fail(__('The :attribute must be a valid hashid.'));
            return;
        }

        $decoded = Hashids::connection($this->connection)->decode($value);

        if (empty($decoded)) {
            $fail(__('The :attribute is invalid.'));
            return;
        }

        // Verifica se o registro realmente existe no banco de dados
        $model = new $this->modelClass;
        $exists = $model->where($model->getKeyName(), $decoded[0])->exists();

        if (!$exists) {
            $fail(__('The selected :attribute does not exist.'));
        }
    }
}
```

## Restrições
- **NÃO altere os tipos de coluna do schema do banco de dados.** A chave primária física do banco deve permanecer um inteiro (ou bigint) rápido e auto-incrementado, para performance de indexação e joins de relacionamento.
- **NÃO deixe a configuração de salt hardcoded.** Todos os salts devem ser resolvidos a partir de variáveis de ambiente (`.env`) através dos arquivos de configuração, para manter a segurança entre os deploys.
- **NÃO exponha IDs crus do banco em respostas de API** para models que utilizam essa trait. Garanta que API Resources e DTOs mapeiem explicitamente a propriedade `id` para o atributo `hashid` do model.
- **Nunca faça joins SQL internos usando hashids.** Sempre decodifique o hashid para a chave inteira crua antes de rodar operações manuais no banco ou consultas customizadas.
- **Trate falhas de decodificação de forma elegante.** Hashes inválidos ou adulterados devem disparar imediatamente uma `ModelNotFoundException` (resultando em uma resposta 404), em vez de lançar exceções genéricas de offset de array do PHP.
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
