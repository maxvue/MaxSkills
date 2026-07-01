---
name: adonisjs-environment-variables-validation-best-practices
description: Use when configuring, reviewing, or validating environment variables, updating start/env.ts, defining Env.schema schemas, troubleshooting missing or invalid env keys, or configuring environment variable injection across different deployment environments in AdonisJS v6. Triggers on start/env.ts modification, Env.schema validation, and env configuration.
---

## Objetivo
Fornecer um conjunto completo de diretrizes e boas práticas para definir, validar e utilizar variáveis de ambiente em aplicações AdonisJS v6 usando `@adonisjs/core/env`.

## Instruções
1. **Definir Esquema em `start/env.ts`**:
   - Cada variável de ambiente utilizada no projeto deve ser declarada e validada no arquivo `start/env.ts` usando `Env.create`.
   - Utilize `Env.schema` para definir restrições para cada variável, garantindo que os tipos sejam convertidos corretamente em runtime (ex: `Env.schema.number()`, `Env.schema.boolean()`).
2. **Acessando Variáveis de Ambiente**:
   - Importe o serviço `env` validado através do alias de caminho `#start/env`:
     ```typescript
     import env from '#start/env'
     ```
   - Sempre acesse as variáveis utilizando o método `env.get('KEY_NAME')` para se beneficiar da tipagem estática estrita e evitar chamadas diretas a `process.env`.
3. **Utilizar os Validadores de Esquema Corretos**:
   - `Env.schema.string()` para texto, com formatação opcional: `Env.schema.string({ format: 'url' })`, `Env.schema.string({ format: 'host' })`.
   - `Env.schema.number()` para converter automaticamente valores de string (como `PORT` ou `DB_PORT`) para números do JavaScript.
   - `Env.schema.boolean()` para converter valores como `"true"`, `"false"`, `"1"` ou `"0"` para booleanos.
   - `Env.schema.enum(['val1', 'val2'] as const)` para um conjunto estrito de valores.
   - Use `.optional()` ao final dos validadores para variáveis que não são obrigatórias (ex: `Env.schema.string.optional()`).
   - Use `Env.schema.secret()` para informações sensíveis (ex: `APP_KEY`, tokens de API) para evitar que sejam exibidas em logs durante a inicialização da aplicação ou em dumps de depuração.
4. **Manutenção do `.env.example`**:
   - Certifique-se de que cada variável adicionada ao `start/env.ts` esteja documentada no arquivo `.env.example` na raiz do projeto com valores de exemplo, deixando as credenciais locais em branco.

## Restrições
- **Nunca** leia variáveis de ambiente diretamente usando `process.env.KEY_NAME`. Sempre use `env.get('KEY_NAME')`.
- **Não** adicione credenciais sensíveis, senhas de produção ou chaves de API reais em arquivos controlados por versão, como `start/env.ts` ou `.env.example`.
- **Nunca** ignore a validação das variáveis de ambiente em produção. A aplicação deve falhar (crash) durante a inicialização se uma variável obrigatória estiver ausente ou inválida.
- **Não** escreva funções personalizadas de conversão para tipos básicos. Confie inteiramente na conversão de tipos do `Env.schema`.
