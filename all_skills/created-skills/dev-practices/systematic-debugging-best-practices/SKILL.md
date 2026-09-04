---
name: systematic-debugging-best-practices
description: "Use when investigating unexpected behavior, test failures, build errors, or performance issues. Enforces root-cause analysis before proposing fixes based on log evidence. Covers systematic debugging methodology and log inspection."
author: Johnattas Conrady Gomes Santana
---
# Metodologia Sistemática de Depuração

## Objetivo

Encontrar e corrigir bugs de forma sistemática usando técnicas comprovadas. Sem adivinhação — siga as evidências e sempre encontre a causa raiz antes de corrigir.

A Lei de Ferro:

```
NENHUMA CORREÇÃO SEM ANTES INVESTIGAR A CAUSA RAIZ
```

Se você não completou a Fase 1, não pode propor correções.

Use esta metodologia quando:

- O usuário reportar um bug ou comportamento inesperado
- Ocorrerem falhas de teste ou erros de build
- O desempenho degradar
- Os problemas forem intermitentes ou acontecerem em produção
- Antes de propor "correções rápidas"
- Especialmente sob pressão de tempo (emergências tornam a adivinhação tentadora)

## Instruções

### Fase 1 — Investigação da Causa Raiz

**Complete esta fase antes de tentar qualquer correção.**

#### 1.1 Reproduza o Bug

```
1. Obtenha os passos exatos para reproduzir
2. Tente reproduzir localmente
3. Anote o que dispara o problema (toda vez? aleatoriamente?)
4. Documente a mensagem de erro completa e o stack trace
5. Identifique o ambiente: dev / staging / prod, navegador, SO
```

#### 1.2 Reúna Evidências

```bash
# Logs da aplicação (Laravel 13) — canal 'daily', arquivos datados
ls -t storage/logs/laravel-*.log | head -1 | xargs tail -f

# Console do navegador
# DevTools → aba Console
```

Verifique: stack trace completo, tipo e mensagem do erro, números de linha, timestamps, quais dados estavam sendo processados.

No front-end (SPA Vue 3), o erro raramente aparece no log do PHP: a requisição passa por uma store MaxPinia. Inspecione o objeto `status` da store para saber se a falha foi na rede ou nos dados — `store.status.server.get.is_success` (e o par `.save` para persistência) revela se a chamada `apiGetRoute`/`apiPostRoute` retornou sucesso. Confira também a aba Network do DevTools para o status HTTP da rota resolvida pelo Ziggy.

#### 1.3 Verifique Mudanças Recentes

- O que mudou que poderia causar isso? (`git diff`, commits recentes)
- Novas dependências, mudanças de configuração, diferenças de ambiente.

#### 1.4 Rastreie o Fluxo de Dados

Para erros no fundo da pilha de chamadas — rastreie de trás para frente:

```
Sintoma: "Cannot read property 'name' of undefined"
↓ Onde: userStore.data.profile.name
↓ Por quê: userStore.data é null
↓ Por quê: apiGetRoute('user.data') não populou a store
↓ Por quê: status.server.get.is_success continuou false (401 na Network)
↓ Causa raiz: o guard renderizou a tela antes de waitRequest() resolver
```

No engeapp as rotas são NOMES Ziggy pontilhados (`'user.data'`, não `/api/...`).

#### 1.5 Reúna Evidências em Sistemas com Múltiplos Componentes

Quando o sistema tem múltiplas camadas (no engeapp: componente Vue → store MaxPinia → rota Ziggy → controller Laravel → Eloquent/MySQL), instrumente cada fronteira ANTES de propor correções:

- **Vue/MaxPinia** — inspecione `store.data` e `store.status.server.get` (`is_requested`/`is_success`/`is_error`/`error`).
- **Fronteira HTTP** — aba Network do DevTools, status da rota resolvida pelo Ziggy (nome pontilhado via `apiGetRoute`).
- **Laravel** — `ls -t storage/logs/laravel-*.log | head -1 | xargs tail -f` (canal `daily`).
- **Eloquent/MySQL** — `DB::listen` / query log, ou Telescope.

Execute uma vez para reunir evidências que mostrem ONDE quebra, depois analise para encontrar o componente que falha.

### Fase 2 — Análise de Padrões

1. Encontre exemplos funcionais no mesmo código-base similares ao que está quebrado.
2. Leia implementações de referência COMPLETAMENTE — não passe os olhos.
3. Liste cada diferença entre o que funciona e o que está quebrado (por menor que seja).
4. Mapeie todas as dependências: configuração, ambiente, estado.

### Fase 3 — Hipótese e Teste

**Método científico:**

1. Declare UMA hipótese clara: *"Acho que X é a causa raiz porque Y."*
2. Faça a MENOR mudança possível para testá-la.
3. Uma variável por vez — não empilhe várias correções.
4. Verifique antes de continuar.
   - Funcionou? → Fase 4.
   - Não funcionou? → Formule uma NOVA hipótese (ver regra de Restrições).

### Fase 4 — Corrigir e Verificar

#### Implementar

1. Corrija a causa raiz, não o sintoma:
   - ❌ `userStore.data?.profile?.name || 'Unknown'` ← esconde o problema
   - ✅ Garanta que a store carregou (`status.server.get.is_success`) antes de renderizar

2. Uma mudança por vez (ver regra de Restrições). Sem refatoração "já que estou aqui".

3. Adicione um teste de regressão primeiro. No engeapp o backend é testado com Pest (Laravel 13):
   ```php
   it('mantém o usuário na sessão após o login', function () {
       $user = User::factory()->create();
       $this->post(route('login'), ['email' => $user->email, 'password' => 'password'])
           ->assertRedirect();
       $this->assertAuthenticatedAs($user);
   });
   ```

Se a correção não funcionar, volte à Fase 1 com a nova informação e formule uma NOVA hipótese (ver regra de Restrições e a regra das 3 tentativas).

#### Localizar quando quebrou

Para descobrir o commit que introduziu a regressão, use `git bisect` (marcando `bad` no estado atual e `good` num commit antigo que funcionava). Para estreitar o ponto de falha no código, uma busca binária com checkpoints (logs temporários antes/depois do trecho suspeito) delimita o intervalo. Remova a instrumentação depois de encontrar a causa.

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Nunca proponha uma correção antes de completar a Fase 1 (causa raiz, não sintoma).
- Mude UMA variável por vez; nunca empilhe várias correções.

**Sinais de alerta — pare e volte à Fase 1:** "correção rápida por agora, investigo depois"; "só tente mudar X e veja se funciona"; "provavelmente é X, deixa eu corrigir"; "não entendo, mas isso pode funcionar"; empilhar várias mudanças de uma vez. E a regra das 3 tentativas: se após 3 correções fracassadas cada uma revela um novo problema em outro lugar, PARE e questione a arquitetura — é problema estrutural, não bug pontual.
