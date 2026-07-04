---
name: systematic-debugging-best-practices
description: Use when reporting a bug, investigating unexpected behavior, test failures, build errors, performance degradation, or intermittent production issues, and before proposing any fix. Enforces root-cause investigation before attempting a fix — no guessing, follow the evidence.
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
# Logs da aplicação
tail -f logs/app.log

# Console do navegador
# DevTools → aba Console
```

Verifique: stack trace completo, tipo e mensagem do erro, números de linha, timestamps, quais dados estavam sendo processados.

#### 1.3 Verifique Mudanças Recentes

- O que mudou que poderia causar isso? (`git diff`, commits recentes)
- Novas dependências, mudanças de configuração, diferenças de ambiente.

#### 1.4 Rastreie o Fluxo de Dados

Para erros no fundo da pilha de chamadas — rastreie de trás para frente:

```
Sintoma: "Cannot read property 'name' of undefined"
↓ Onde: user.profile.name
↓ Por quê: user.profile é undefined
↓ Por quê: a API não retornou profile
↓ Por quê: o ID do usuário era null
↓ Causa raiz: o login não definiu o ID do usuário na sessão
```

#### 1.5 Reúna Evidências em Sistemas com Múltiplos Componentes

Quando o sistema tem múltiplas camadas (CI → build → assinatura, API → serviço → banco de dados), adicione instrumentação de diagnóstico em cada fronteira ANTES de propor correções:

```bash
echo "=== Vars na camada 1: ===" && env | grep MY_VAR || echo "UNSET"
echo "=== Estado na camada 2: ===" && ...
```

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
   - Não funcionou? → Formule uma NOVA hipótese. Não adicione mais correções por cima.

### Fase 4 — Corrigir e Verificar

#### Implementar

1. Corrija a causa raiz, não o sintoma:
   - ❌ `user?.profile?.name || 'Unknown'` ← esconde o problema
   - ✅ Garanta que `user.profile` esteja populado antes de renderizar

2. UMA mudança por vez. Sem refatoração "já que estou aqui".

3. Adicione um teste de regressão primeiro:
   ```javascript
   test('login define o ID do usuário na sessão', async () => {
     const user = await login({ email: 'test@example.com', password: 'pass' });
     expect(session.userId).toBe(user.id);
   });
   ```

#### Se a Correção Não Funcionar

- < 3 tentativas: Volte à Fase 1 com a nova informação.
- ≥ 3 tentativas: **PARE e questione a arquitetura** — cada correção que revela um novo problema em um lugar diferente é um problema arquitetural, não um bug.

#### Prevenção de Regressão

```javascript
// Depuração por busca binária — estreite o espaço
console.log('CHECKPOINT 1'); // Antes do código suspeito
console.log('CHECKPOINT 2'); // Depois do código suspeito

// Git bisect para "quando isso quebrou?"
git bisect start
git bisect bad   // o atual está quebrado
git bisect good abc123  // este commit antigo funcionava
```

### Ferramentas de Depuração

```
Browser DevTools:
  Console → logs e erros
  Sources → breakpoints, passo a passo
  Network → chamadas de API e respostas
  Application → cookies, storage, cache

Node.js:
  node --inspect app.js  (depois chrome://inspect)

VS Code:
  .vscode/launch.json com type: "node"

Git:
  git bisect  → encontre o commit que introduziu o bug
```

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Nunca proponha uma correção antes de completar a investigação da causa raiz na Fase 1.
- Corrija a causa raiz, não o sintoma.
- Mude UMA variável por vez; nunca empilhe várias correções.
- Após 3 tentativas de correção fracassadas, pare e questione a arquitetura em vez de tentar "mais uma correção".

Sinais de alerta — pare e volte à Fase 1:

- "Correção rápida por agora, investigo depois"
- "Só tente mudar X e veja se funciona"
- "Provavelmente é X, deixa eu corrigir isso"
- "Não entendo totalmente, mas isso pode funcionar"
- Adicionar várias mudanças de uma vez
- "Mais uma tentativa de correção" (quando já tentou 2+)
- Cada correção revela um novo problema em um lugar diferente

## Exemplos

Padrões comuns de bugs:

```javascript
// Null/undefined
const name = user?.profile?.name || 'Unknown'; // correção opcional
// Melhor: valide que profile existe antes de renderizar

// Condição de corrida
const data = await fetchData(); // use await, não dispare e esqueça

// Erro de índice (off-by-one)
for (let i = 0; i < array.length; i++) { ... } // não <=

// Coerção de tipo
if (count === 0) { ... } // não ==

// Async sem await
const result = await asyncFn(); // não asyncFn()
```
