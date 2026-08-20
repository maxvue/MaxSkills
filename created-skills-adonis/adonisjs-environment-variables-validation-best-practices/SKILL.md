---
name: adonisjs-environment-variables-validation-best-practices
description: Use when configuring, reviewing, or validating environment variables, updating start/env.ts, defining Env.schema schemas, troubleshooting missing or invalid env keys, or configuring environment variable injection across different deployment environments in AdonisJS v6. Triggers on start/env.ts modification, Env.schema validation, and env configuration.
author: Johnattas Conrady Gomes Santana
---
## Objetivo
Fornecer um conjunto abrangente de diretrizes e boas práticas para definir, validar e usar variáveis de ambiente em aplicações AdonisJS v6 usando `@adonisjs/core/env`.

## Instruções
1. **Defina o Schema em `start/env.ts`**:
   - Toda variável de ambiente usada no projeto deve ser declarada e validada em `start/env.ts` usando `Env.create`.
   - Use `Env.schema` para definir restrições para cada variável, garantindo que os tipos sejam convertidos corretamente em runtime (ex.: `Env.schema.number()`, `Env.schema.boolean()`).
2. **Acessando Variáveis de Ambiente**:
   - Importe o serviço `env` já validado por meio do path alias `#start/env`:
     ```typescript
     import env from '#start/env'
     ```
   - Sempre acesse as variáveis usando o método `env.get('KEY_NAME')` para se beneficiar da tipagem estática estrita e evitar chamadas cruas a `process.env`.
3. **Use os Validadores de Schema Corretos**:
   - `Env.schema.string()` para texto, com formatação opcional: `Env.schema.string({ format: 'url' })`, `Env.schema.string({ format: 'host' })`.
   - `Env.schema.number()` para converter automaticamente valores string (como `PORT` ou `DB_PORT`) em números JavaScript.
   - `Env.schema.boolean()` para converter valores como `"true"`, `"false"`, `"1"` ou `"0"` em boolean.
   - `Env.schema.enum(['val1', 'val2'] as const)` para um conjunto estrito de valores.
   - Use `.optional()` no final dos validadores para variáveis que não são obrigatórias (ex.: `Env.schema.string.optional()`).
   - Declare informações sensíveis (ex.: `APP_KEY`, tokens de API) com `Env.schema.string()` — da mesma forma que o próprio `start/env.ts` do projeto valida `APP_KEY`. O schema de validação instalado (`@poppinss/validator-lite`) expõe apenas `number`, `string`, `boolean` e `enum`; não existe um validador `Env.schema.secret()`, então não o chame (ele lança `Env.schema.secret is not a function`) e não presuma nenhum recurso de mascaramento de log a partir do schema.
4. **Manutenção do `.env.example`**:
   - Garanta que toda variável adicionada ao `start/env.ts` esteja documentada no arquivo `.env.example` da raiz com valores de placeholder, mantendo as credenciais locais em branco.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversa Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta própria skill esteja escrito.
- **Nunca** leia variáveis de ambiente diretamente usando `process.env.KEY_NAME`. Sempre use `env.get('KEY_NAME')`.
- **Não** adicione credenciais sensíveis, senhas de produção ou chaves de API reais a arquivos versionados como `start/env.ts` ou `.env.example`.
- **Nunca** ignore a validação de variáveis de ambiente em produção. A aplicação deve quebrar durante o bootstrap se uma variável obrigatória estiver ausente ou inválida.
- **Não** escreva funções parser customizadas para tipos básicos. Confie inteiramente na conversão de tipos do `Env.schema`.
