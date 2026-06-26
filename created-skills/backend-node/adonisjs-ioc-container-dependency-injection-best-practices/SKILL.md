---
name: adonisjs-ioc-container-dependency-injection-best-practices
description: Use when designing, reviewing, or debugging dependency injection, IoC container bindings, or service provider setups in an AdonisJS application. Triggers on constructor injections, the @inject decorator, registrations in AppProvider, swaps in tests, and resolving service instances from the container.
---

# Melhores Práticas para IoC Container e Injeção de Dependência no AdonisJS

## Objetivo
Estabelecer convenções e padrões estritos para o gerenciamento de Injeção de Dependência (DI) e do Container de Inversão de Controle (IoC) em aplicações AdonisJS v6, garantindo separação limpa de código, gerenciamento robusto de memória e facilidade na criação de mocks para testes.

## Instruções

### 1. Uso de Injeção via Construtor e do Decorator `@inject`
- Sempre prefira a Injeção via Construtor em vez de instanciação manual (usando `new Classe()`) ou importação direta de instâncias singleton caso uma classe dependa de outros serviços.
- Adicione o decorator `@inject()` do `@adonisjs/core` nas declarações de classes para permitir a resolução automática de dependências.
- Certifique-se de que as opções do TypeScript `emitDecoratorMetadata` e `experimentalDecorators` estejam habilitadas no `tsconfig.json`.
- Não passe parâmetros para o `@inject()` a menos que esteja injetando um token/símbolo específico ou resolvendo a partir de um resolvedor de container customizado. Para classes típicas e serviços principais, o `@inject()` sem parâmetros é preferencial, pois o container infere os tipos a partir dos metadados do TypeScript.

### 2. Registro de Bindings em Service Providers
- Use o método `register` do `AppProvider` (localizado em `providers/app_provider.ts`) para registrar os bindings do container.
- Use `this.app.container.bind` para bindings transientes (uma nova instância é resolvida a cada chamada).
- Use `this.app.container.singleton` para singletons (a classe é instanciada apenas uma vez e a mesma instância é retornada nas resoluções subsequentes).
- Para integrações externas complexas (por exemplo, Stripe, Meta API), configure e instancie-as dentro do provider puxando a configuração do serviço de config, em vez de instanciá-las dinamicamente no código de negócios.

### 3. Resolução de Dependências e Tratamento de Contexto
- Evite usar o `app.container.make` global dentro de serviços ou controllers. Confie na injeção automática via construtor.
- Ao resolver dependências dinamicamente durante uma requisição HTTP, use o resolvedor de container local da requisição (`ctx.containerResolver`) para garantir o isolamento do contexto e prevenir vazamentos de memória.

### 4. Prevenção de Vazamento de Memória e Poluição de Estado em Singletons
- Serviços registrados como singletons devem ser *stateless* (sem estado). Nunca armazene dados específicos da requisição (como o usuário atual, payload da requisição ou cabeçalhos HTTP) em propriedades de instância de um singleton.
- Se um serviço precisar do contexto da requisição, passe o `HttpContext` ou as propriedades relevantes (como `User`) explicitamente como argumentos para os métodos do serviço.
- Se propriedades de instância forem necessárias para cache ou estado temporário, garanta que elas não cresçam indefinidamente e que tenham escopo e limpeza adequados.

### 5. Substituição (Swapping) e Mocks em Testes
- Não use monkey-patching ou bibliotecas complexas de mock. Use o método nativo `app.container.swap` fornecido pelo AdonisJS para substituir implementações de serviços durante os testes com Japa.
- Sempre restaure os bindings do container no hook de desmontagem/limpeza (teardown/cleanup) do grupo de testes para evitar a poluição de testes subsequentes. Use `app.container.restore`.

## Examples

### Injeção via Construtor (Constructor Injection)
```typescript
import { inject } from '@adonisjs/core'
import { HttpContext } from '@adonisjs/core/http'
import { UserService } from '#services/user_service'

@inject()
export default class UsersController {
  constructor(
    protected userService: UserService,
    protected ctx: HttpContext
  ) {}

  async index() {
    const users = await this.userService.all()
    return this.ctx.view.render('users/index', { users })
  }
}
```

### Binding no AppProvider
```typescript
import { ApplicationService } from '@adonisjs/core/types'
import { StripeService } from '#services/stripe_service'

export default class AppProvider {
  constructor(protected app: ApplicationService) {}

  register() {
    // Registrando StripeService como um Singleton
    this.app.container.singleton(StripeService, () => {
      const config = this.app.config.get('stripe')
      return new StripeService(config)
    })
  }
}
```

### Substituição (Swapping) em Testes (Japa)
```typescript
import { test } from '@japa/runner'
import app from '@adonisjs/core/services/app'
import { StripeService } from '#services/stripe_service'

class FakeStripeService {
  async charge(amount: number) {
    return { id: 'ch_fake', status: 'succeeded', amount }
  }
}

test.group('Processo de Faturamento', (group) => {
  group.each.setup(() => {
    // Substitui o StripeService original pelo nosso Fake
    app.container.swap(StripeService, () => new FakeStripeService())

    // Restaura o original após a execução do teste
    return () => app.container.restore(StripeService)
  })

  test('processa o checkout com sucesso', async ({ client }) => {
    const response = await client.post('/checkout').json({ amount: 100 })
    response.assertStatus(200)
  })
})
```

## Restrições
- **Nunca** instancie classes manualmente (por exemplo, `const service = new PaymentService()`) se elas próprias requererem injeção de dependências.
- **Nunca** armazene estados mutáveis específicos de requisições dentro de instâncias singleton.
- **Nunca** chame `app.container.swap` no código de produção. A substituição (swapping) é estritamente restrita a ambientes de teste.
- **Não** polua o `AppProvider` com código de implementação direto. Mantenha os bindings do container limpos e aproveite as importações de módulos.
