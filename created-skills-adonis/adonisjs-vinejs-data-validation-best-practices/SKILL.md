---
name: adonisjs-vinejs-data-validation-best-practices
description: Use when defining, editing, validating, or reviewing VineJS validation schemas in AdonisJS v6. Triggers on schema builders (`vine.object`, `vine.compile`), custom validation rules (CPF, CNPJ, phone, postal code), localization of validation messages, and handling schema-inferred TypeScript types.
author: Johnattas Conrady Gomes Santana
---
# Melhores Práticas de Validação de Dados com VineJS no AdonisJS v6

## Objetivo
Estabelecer padrões limpos, otimizados para desempenho e padronizados para a definição de esquemas de validação de dados usando o VineJS no AdonisJS v6, cobrindo regras de validação personalizadas para formatos brasileiros (CPF, CNPJ, CEP, Telefone) e inferência de tipos robusta com TypeScript.

## Instruções

### 1. Estrutura de Arquivos e Localização
* Agrupe os esquemas de validação em arquivos dedicados na pasta `app/validators/`, em vez de declará-los diretamente em controllers.
* Exporte tanto o validador compilado quanto o tipo TypeScript inferido a partir do arquivo do validador.

Exemplo: `app/validators/auth.ts`
```typescript
import vine from '@vinejs/vine'
import type { Infer } from '@vinejs/vine/types'

export const loginValidator = vine.compile(
  vine.object({
    email: vine.string().email().normalizeEmail(),
    password: vine.string(),
    remember: vine.boolean().optional(),
  })
)

export type LoginPayload = Infer<typeof loginValidator>
```

### 2. Compilação e Execução de Esquemas
* **Sempre compile esquemas fora do ciclo de requisição** utilizando `vine.compile()`. A compilação de esquemas exige processamento de CPU; compilá-la uma única vez no escopo global do módulo maximiza o desempenho.
* Execute a validação nos controllers utilizando `request.validateUsing()`:
  ```typescript
  import { loginValidator } from '#validators/auth'

  export default class AuthController {
    async login({ request, response }: HttpContext) {
      const payload = await request.validateUsing(loginValidator)
      // payload está tipado como LoginPayload
    }
  }
  ```

### 3. Regras Brasileiras Personalizadas (CPF, CNPJ, CEP, Telefone)
Para validar formatos comuns no mercado brasileiro, crie regras customizadas e registre-as em um arquivo de pré-carregamento (preload):

1. **Defina a Regra em `start/validator.ts`**:
   ```typescript
   import vine, { VineString } from '@vinejs/vine'
   import type { FieldContext } from '@vinejs/vine/types'
   
   // Função utilitária para validação de CPF
   function isValidCpf(cpf: string): boolean {
     const cleanCpf = cpf.replace(/\D/g, '')
     if (cleanCpf.length !== 11 || /^(\d)\1{10}$/.test(cleanCpf)) return false
     
     let sum = 0
     for (let i = 0; i < 9; i++) sum += parseInt(cleanCpf.charAt(i)) * (10 - i)
     let rev = 11 - (sum % 11)
     if (rev === 10 || rev === 11) rev = 0
     if (rev !== parseInt(cleanCpf.charAt(9))) return false
     
     sum = 0
     for (let i = 0; i < 10; i++) sum += parseInt(cleanCpf.charAt(i)) * (11 - i)
     rev = 11 - (sum % 11)
     if (rev === 10 || rev === 11) rev = 0
     if (rev !== parseInt(cleanCpf.charAt(10))) return false
     
     return true
   }

   export const cpfRule = vine.createRule((value: unknown, options, field: FieldContext) => {
     if (typeof value !== 'string') return
     
     if (!isValidCpf(value)) {
       field.report('O campo {{ field }} deve ser um CPF válido', 'cpf', field)
     }
   })

   // Registra o macro no prototipo correto (VineString) — API publica do VineJS v6
   VineString.macro('cpf', function (this: VineString) {
     return this.use(cpfRule())
   })
   ```

2. **Declaration Merging em `contracts/validator.ts`** (ou em um arquivo `.d.ts`) para tipagem no TypeScript:
   ```typescript
   import '@vinejs/vine'

   declare module '@vinejs/vine' {
     interface VineString {
       cpf(): this
       cnpj(): this
       cep(): this
       phone(): this
     }
   }
   ```

3. **Uso nos Esquemas**:
   ```typescript
   import vine from '@vinejs/vine'

   export const userProfileValidator = vine.compile(
     vine.object({
       cpf: vine.string().cpf(),
       phone: vine.string().phone().optional(),
     })
   )
   ```

### 4. Localização de Mensagens de Erro
* Configure um `SimpleMessagesProvider` global em `start/validator.ts` para traduzir mensagens genéricas de validação:
  ```typescript
  import vine, { SimpleMessagesProvider } from '@vinejs/vine'

  vine.messagesProvider = new SimpleMessagesProvider({
    'required': 'O campo {{ field }} é obrigatório',
    'string': 'O campo {{ field }} deve ser uma string',
    'email': 'O campo {{ field }} deve ser um e-mail válido',
    'minLength': 'O campo {{ field }} deve ter no mínimo {{ min }} caracteres',
    'maxLength': 'O campo {{ field }} deve ter no máximo {{ max }} caracteres',
    'confirmed': 'A confirmação do campo {{ field }} não coincide',
  })
  ```
* Para projetos com múltiplos idiomas, utilize a integração com o pacote `@adonisjs/i18n`, que automaticamente gerencia o provedor de mensagens com base nos dicionários de tradução em `resources/lang/`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NUNCA chame `vine.compile()` dentro de métodos de controllers. Sempre declare e compile esquemas de validação no escopo do módulo.
* NUNCA use blocos manuais de try/catch nos controllers apenas para lidar com erros de validação. Deixe o handler global de exceções do AdonisJS capturar `E_VALIDATION_ERROR` (Unprocessable Entity) e formatar a resposta JSON.
* NUNCA ignore a segurança de tipagem com TypeScript. Exporte sempre o tipo utilitário usando `Infer<typeof validator>` para compartilhamento seguro com outras partes da aplicação.
* NUNCA defina validações duplicadas inline. Se a lógica de verificação de formatos comuns (como CPF ou CNPJ) for usada em múltiplos locais, implemente-a como uma regra customizada no VineJS.
