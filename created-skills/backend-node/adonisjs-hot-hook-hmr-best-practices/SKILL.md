---
name: adonisjs-hot-hook-hmr-best-practices
description: Use when configuring, debugging, or coding with hot-hook or Hot Module Replacement (HMR) in AdonisJS v6. Triggers on changes to hotHook boundaries in package.json, configuring controller/middleware reloading, handling memory leaks, or resolving container binding updates during development.
---

# Melhores Práticas de Hot-Hook HMR no AdonisJS v6

## Objetivo
Fornecer diretrizes e padrões para configurar, desenvolver e depurar aplicações AdonisJS v6 utilizando `hot-hook` para substituição de módulos a quente (HMR) no backend. Esta skill garante ciclos rápidos de desenvolvimento, prevenindo vazamentos de memória (memory leaks), listeners de eventos duplicados e inconsistências de bindings no contêiner IoC durante as recargas.

## Instruções

### 1. Configuração de Boundaries (Fronteiras) no `package.json`
Para maximizar a eficiência e a estabilidade do HMR, defina adequadamente os limites (`boundaries`) do `hot-hook` no seu `package.json`. Módulos que inicializam listeners de rede, pools de banco de dados ou configurações globais da aplicação devem ficar de fora das boundaries.
- Limite as boundaries a módulos transientes e sem estado (stateless), tais como **controllers**, **middlewares**, **validators** e **services** simples.
- Não adicione arquivos de bootstrap da aplicação, providers de serviços ou configurações de banco de dados nos limites de HMR.

Exemplo de configuração no `package.json`:
```json
{
  "hotHook": {
    "boundaries": [
      "app/controllers/**/*.ts",
      "app/middleware/**/*.ts",
      "app/validators/**/*.ts"
    ]
  }
}
```

### 2. Resolução no Contêiner IoC e Injeção de Dependência
O HMR funciona re-importando os módulos modificados e substituindo as instâncias. Se um singleton de ciclo de vida longo mantiver uma referência a uma instância que sofreu HMR, essa referência ficará desatualizada (stale).
- **Evite fazer cache de instâncias recarregáveis por HMR** dentro de singletons ou providers globais da aplicação.
- **Resolva dependências dinamicamente** ou use registros do tipo transiente/fábrica no contêiner IoC, em vez de fazer cache de instâncias de classes importadas.
- Ao resolver dependências dentro de middlewares ou controllers, permita que o contêiner IoC gerencie a resolução a cada requisição para garantir que a versão mais atualizada da classe seja injetada.

### 3. Prevenção de Vazamento de Memória e Recursos
Quando o `hot-hook` substitui um módulo, o contexto de execução anterior é descartado, mas bindings externos (como timers, conexões de rede abertas e listeners de eventos globais) continuam ativos no processo.
- **Limpe listeners ativos**: Remova listeners de eventos globais (`process.on`, `emitter.on`) e limpe timers ativos (`setInterval`, `setTimeout`) quando um módulo for descarregado.
- **Hooks de descarte (dispose)**: Utilize `import.meta.hot` (se fornecido ou suportado pelo ambiente do hot-hook) para registrar funções de retorno de limpeza de recursos.

### 4. Gerenciamento de Estado
Arquivos dentro das boundaries do HMR terão seu estado local (no escopo do módulo) reiniciado após cada re-importação.
- Se você precisar de um estado que persista através de recargas quentes, posicione esse estado em um módulo fora das boundaries do `hot-hook` ou associe-o de forma segura ao objeto `global`.

---

## Examples

### Exemplo 1: Prevenindo Vazamento de Listeners de Eventos
Ao registrar ganchos (hooks) ou listeners globais de eventos dentro de um módulo recarregável por HMR, certifique-se de limpar listeners anteriormente registrados para evitar que executem múltiplas vezes.

```typescript
import router from '@adonisjs/core/services/router'

// Armazenando a referência da função do listener para poder limpá-la
function onRouteResolved(route: any) {
  console.log(`Rota resolvida: ${route.pattern}`)
}

// Limpa o listener existente antes de registrar um novo
router.off('route:resolved', onRouteResolved)
router.on('route:resolved', onRouteResolved)
```

### Exemplo 2: Resolução Dinâmica no Contêiner (Evitando Referências Desatualizadas)
Evite armazenar instâncias de classes recarregáveis por HMR em propriedades estáticas ou parâmetros de construtor de um singleton de longa duração.

**Incorreto (Referência desatualizada após o recarregamento por HMR):**
```typescript
import { inject } from '@adonisjs/core'
import UserService from '#services/user_service' // UserService está dentro da boundary do HMR

@inject()
export default class UserProfileController {
  // Armazenar a instância no construtor da classe pode fazer cache da definição antiga da classe
  constructor(protected userService: UserService) {}

  async show({ response }: HttpContext) {
    const users = await this.userService.all()
    return response.ok(users)
  }
}
```

**Correto (Resolvendo sob demanda ou usando DI transiente adequada do IoC):**
Garanta que os serviços injetados sejam registrados como transientes no contêiner ou aproveite a injeção automática do AdonisJS a cada ciclo de requisição para obter a classe atualizada.

---

## Restrições
- **Nunca** inclua arquivos com lógica de conexão de banco de dados, instanciação de cliente Redis ou inicialização do servidor HTTP no array `hotHook.boundaries`.
- **Nunca** registre listeners de eventos permanentes no escopo global de um módulo recarregado por HMR sem uma estratégia explícita de desmontagem/limpeza.
- Não utilize estado global dentro de controllers e middlewares; o estado deve ser gerenciado por meio de sessão, banco de dados ou tokens sem estado para evitar resets inesperados de dados durante as atualizações do HMR.
