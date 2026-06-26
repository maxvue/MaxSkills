---
name: typescript-documentation-best-practices
description: Use when generating TypeScript documentation — JSDoc annotations, TypeDoc API reference, architectural decision records (ADRs), and doc patterns for AdonisJS v6 controllers/services e composables Vue 3. Triggers on documenting public APIs, setting up doc CI/CD pipelines, and validating JSDoc with ESLint.
---

# Boas Práticas de Documentação em TypeScript

## Objetivo

Gerar documentação TypeScript pronta para produção com uma arquitetura em camadas para múltiplos públicos. Use anotações JSDoc para documentação inline, TypeDoc para geração de referência de API e ADRs para rastrear decisões de design, além de padrões alinhados ao stack-alvo (AdonisJS v6 no backend e Vue 3 no front).

Capacidades principais:
- Configuração do TypeDoc e geração de documentação de API
- Padrões JSDoc para todas as construções do TypeScript
- Criação e manutenção de ADRs
- Padrões de documentação para controllers/services AdonisJS v6 e composables Vue 3
- Regras de validação do ESLint para qualidade da documentação
- Configuração de pipeline com GitHub Actions

## Instruções

### Referência rápida

| Ferramenta | Propósito | Comando |
|------|---------|---------|
| TypeDoc | Geração de documentação de API | `npx typedoc` |
| Compodoc | Documentação Angular | `npx compodoc -p tsconfig.json` |
| ESLint JSDoc | Validação de documentação | `eslint --ext .ts src/` |

Tags JSDoc:

| Tag | Caso de Uso |
|-----|----------|
| `@param` | Documentar parâmetros |
| `@returns` | Documentar valores de retorno |
| `@throws` | Documentar condições de erro |
| `@example` | Fornecer exemplos de código |
| `@remarks` | Adicionar notas de implementação |
| `@see` | Referência cruzada de itens relacionados |
| `@deprecated` | Marcar APIs depreciadas |

### 1. Configurar o TypeDoc

```bash
npm install --save-dev typedoc typedoc-plugin-markdown
```

```json
{
  "entryPoints": ["src/index.ts"],
  "out": "docs/api",
  "theme": "markdown",
  "excludePrivate": true,
  "readme": "README.md"
}
```

### 2. Adicionar comentários JSDoc

```typescript
/**
 * Serviço para gerenciar a autenticação de usuários
 *
 * @remarks
 * Lida com autenticação baseada em sessão+cookie (guard `web` do AdonisJS),
 * com sessões persistidas em banco e validade de 30 dias. Hashing de senha
 * via scrypt (driver padrão do AdonisJS Hash).
 *
 * Notas de segurança:
 * - Senhas com hash via scrypt (driver padrão do AdonisJS)
 * - Sessão emitida via cookie HttpOnly + SameSite; sem tokens no front
 *
 * @example
 * ```typescript
 * const authService = new AuthService()
 * await authService.login(ctx, credentials)
 * ```
 */
export class AuthService {
  /**
   * Autentica um usuário e inicia a sessão (guard `web`)
   * @param ctx - HttpContext da requisição AdonisJS
   * @param credentials - Credenciais de login do usuário
   * @returns Usuário autenticado
   * @throws {InvalidCredentialsError} Se as credenciais forem inválidas
   */
  async login(ctx: HttpContext, credentials: LoginCredentials): Promise<User> {
    // Implementação
  }
}
```

### 3. Criar um ADR

```markdown
# ADR-001: Configuração do Modo Strict do TypeScript

## Status
Aceito

## Contexto
Qual é o problema que motiva esta decisão?

## Decisão
Qual mudança estamos propondo?

## Consequências
O que se torna mais fácil ou mais difícil?
```

### 4. Configurar pipeline de CI/CD

```yaml
name: Documentation
on:
  push:
    branches: [main]
    paths: ['src/**', 'docs/**']

jobs:
  generate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run docs:generate
      - run: npm run docs:validate
```

### 5. Validar a documentação

```json
{
  "rules": {
    "jsdoc/require-description": "error",
    "jsdoc/require-param-description": "error",
    "jsdoc/require-returns-description": "error",
    "jsdoc/require-example": "warn"
  }
}
```

**Se a validação falhar:** revise os erros do ESLint, corrija os comentários JSDoc (adicione descrições faltantes, adicione `@param`/`@returns`/`@throws` onde ausentes), execute novamente `eslint --ext .ts src/` até que todos os erros passem antes de commitar.

## Restrições

Boas práticas:

1. **Documente APIs públicas**: Todos os métodos, classes e interfaces públicos
2. **Use `@example`**: Forneça exemplos executáveis para funções complexas
3. **Inclua `@throws`**: Documente todos os erros possíveis
4. **Adicione `@see`**: Faça referência cruzada de funções/tipos relacionados
5. **Use `@remarks`**: Adicione detalhes e notas de implementação
6. **Documente generics**: Explique restrições e uso de generics
7. **Inclua notas de desempenho**: Documente complexidade de tempo/espaço
8. **Adicione avisos de segurança**: Destaque considerações de segurança
9. **Mantenha atualizado**: Atualize a documentação quando o código mudar
10. **Não documente código óbvio**: Foque no porquê, não no quê

Restrições e avisos:

- **Membros privados**: Use `@private` ou exclua da saída do TypeDoc
- **Tipos complexos**: Documente restrições de generics e parâmetros de tipo
- **Breaking changes**: Use `@deprecated` com orientação de migração
- **Informações de segurança**: Nunca inclua segredos ou credenciais na documentação
- **Validade dos links**: Garanta que as referências `@see` apontem para locais válidos
- **Código de exemplo**: Todos os exemplos devem ser executáveis e testados
- **Versionamento**: Mantenha a documentação sincronizada com as versões do código

Referências (padrões detalhados):
- **[references/jsdoc-patterns.md](references/jsdoc-patterns.md)** — Padrões JSDoc para interfaces, funções, classes, generics e uniões
- **[references/framework-patterns.md](references/framework-patterns.md)** — Padrões de documentação para controllers/services AdonisJS v6 e composables Vue 3
- **[references/adr-patterns.md](references/adr-patterns.md)** — Templates e exemplos de ADR
- **[references/pipeline-setup.md](references/pipeline-setup.md)** — Configuração de pipeline de CI/CD para documentação
- **[references/validation.md](references/validation.md)** — Regras do ESLint e checklists de validação
- **[references/typedoc-configuration.md](references/typedoc-configuration.md)** — Opções completas de configuração do TypeDoc
- **[references/examples.md](references/examples.md)** — Exemplos de código adicionais

## Exemplos

### Documentando um composable Vue 3

```typescript
/**
 * Composable para acessar dados paginados de usinas via store MaxPinia
 *
 * @remarks
 * O GET ao backend é feito pela store `@maxvue/max-pinia` (cache +
 * salvamento automático debounced); o composable não faz requisições manuais.
 * A rota é um caminho string `/api/...` resolvido por `apiGetRoute`.
 *
 * @example
 * ```vue
 * <script setup lang="ts">
 * const { data, isLoading, error } = usePaginatedUsinas({ page: 1, limit: 10 })
 * </script>
 * ```
 *
 * @param options - Opções de paginação e filtro
 * @returns Refs reativas com itens, estado de carregamento e erro
 */
export function usePaginatedUsinas(
  options: PaginationOptions
): UsePaginatedResult<Usina> {
  // Implementação via store @maxvue/max-pinia
}
```

### Documentando uma função utilitária

```typescript
/**
 * Valida endereços de e-mail usando a especificação RFC 5322
 *
 * @param email - Endereço de e-mail a validar
 * @returns Verdadeiro se o formato do e-mail for válido
 *
 * @example
 * ```typescript
 * isValidEmail('user@example.com'); // true
 * isValidEmail('invalid-email');      // false
 * ```
 *
 * @performance
 * O(n) onde n é o comprimento da string do e-mail
 *
 * @see {@link https://tools.ietf.org/html/rfc5322} Especificação RFC 5322
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}
```

### Documentação de controller NestJS

```typescript
/**
 * Endpoints de API REST para gerenciamento de usuários
 *
 * @remarks
 * Todos os endpoints exigem autenticação via token Bearer.
 * Rate limiting: 100 requisições por minuto por usuário.
 *
 * @example
 * ```bash
 * curl -H "Authorization: Bearer <token>" https://api.example.com/users/123
 * ```
 *
 * @security
 * - Todos os endpoints usam HTTPS
 * - Tokens JWT expiram após 1 hora
 * - Dados sensíveis são redigidos dos logs
 */
@Controller('users')
export class UsersController {
  /**
   * Recupera um usuário pelo ID
   * @param id - UUID do usuário
   * @returns Perfil do usuário (senha excluída)
   */
  @Get(':id')
  async getUser(@Param('id') id: string): Promise<UserProfile> {
    // Implementação
  }
}
```
