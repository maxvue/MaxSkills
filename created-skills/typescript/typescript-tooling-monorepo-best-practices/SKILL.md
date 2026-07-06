---
name: typescript-tooling-monorepo-best-practices
description: "Use ao resolver problemas reais de ferramental TypeScript/JavaScript — desempenho do compilador (tsc lento), project references com composite por pacote, migração de JS para TS, erros de resolução de módulos, interop ESM/CJS e depuração de tsc. Foca no stack real: ESM-first, moduleResolution bundler, ESLint + typescript-eslint e Vitest. Aciona em tsconfig, velocidade de build e erros de tipo."
---

# Boas Práticas de Ferramental, Monorepo e Migração em TypeScript

## Objetivo

Aplicar expertise profunda e prática em TypeScript e JavaScript a problemas do mundo real: programação em nível de tipos, otimização de desempenho, gerenciamento de monorepo, estratégias de migração e decisões de ferramental moderno, com base nas melhores práticas atuais.

## Instruções

### Quando acionado

0. Se o problema exigir expertise ultra-específica, recomende a troca e pare:
   - Internos profundos de bundlers webpack/vite/rollup → um especialista de build dedicado
   - Migração ESM/CJS complexa ou análise de dependências circulares → um especialista de módulos dedicado
   - Profiling de desempenho de tipos ou internos do compilador → um especialista de tipos dedicado

   Exemplo de saída:
   "Isto requer expertise profunda em bundlers. Por favor, acione um especialista de build dedicado. Parando aqui."

1. Analise a configuração do projeto de forma abrangente. **Use as ferramentas internas primeiro (Read, Grep, Glob) para melhor desempenho. Comandos de shell são alternativas.**

   ```bash
   # Versões principais e configuração
   npx tsc --version
   node -v
   # Detectar ecossistema de ferramental (prefira parsear o package.json)
   node -e "const p=require('./package.json');console.log(Object.keys({...p.devDependencies,...p.dependencies}||{}).join('\n'))" 2>/dev/null | grep -E 'biome|eslint|prettier|vitest|jest|turborepo|nx' || echo "No tooling detected"
   # Verificar monorepo (precedência fixa)
   (test -f pnpm-workspace.yaml || test -f lerna.json || test -f nx.json || test -f turbo.json) && echo "Monorepo detected"
   ```

   Após a detecção, adapte a abordagem:
   - Combine o estilo de import (absoluto vs relativo)
   - Respeite a configuração existente de baseUrl/paths
   - Prefira os scripts existentes do projeto a ferramentas cruas
   - Considere project references antes de mudanças amplas no tsconfig

   > **Realidade dos projetos de referência (engeapp, MaxUse, MaxPinia, MaxComponentsUi):** são pacotes npm **separados**, não um monorepo gerenciado — não há `turbo.json`/`nx.json`/`pnpm-workspace.yaml`/`lerna.json`. As libs `Max*` publicáveis definem `composite: true` **por pacote** no próprio `tsconfig.json`; o app engeapp usa `moduleResolution: "bundler"` sem `composite`. O ferramental real é **ESLint + typescript-eslint + Vitest** (nenhum projeto usa Biome). As seções sobre monorepo (Nx/Turborepo) e Biome abaixo são **orientação genérica** — aplique-as apenas se o projeto atual realmente adotar essas ferramentas.

2. Identifique a categoria específica do problema e o nível de complexidade.

3. Aplique a estratégia de solução apropriada da expertise abaixo.

4. Valide minuciosamente:

   ```bash
   # Abordagem de falha rápida (evite processos de longa duração)
   npm run -s typecheck || npx tsc --noEmit
   npm test -s || npx vitest run --reporter=basic --no-watch
   # Apenas se necessário e se o build afeta saídas/config
   npm run -s build
   ```

   **Nota de segurança:** Evite processos watch/serve na validação. Use apenas diagnósticos de execução única.

### Type-level avançado (fora de escopo)

Para programação em nível de tipos — generics, tipos condicionais/mapeados/template literal, branded types, inferência (`satisfies`/`as const`), configuração `strict` do compilador e testes de tipo com `expectTypeOf` — veja a skill **typescript-advanced-types-best-practices**. Esta skill foca no ferramental que envolve esses tipos (desempenho do compilador, monorepo, migração, resolução de módulos).

### Estratégias de otimização de desempenho

**Desempenho de verificação de tipos**

```bash
# Diagnosticar verificação de tipos lenta
npx tsc --extendedDiagnostics --incremental false | grep -E "Check time|Files:|Lines:|Nodes:"

# Correções comuns para "Type instantiation is excessively deep"
# 1. Substituir interseções de tipos por interfaces
# 2. Dividir uniões grandes (>100 membros)
# 3. Evitar restrições genéricas circulares
# 4. Usar aliases de tipo para quebrar a recursão
```

**Padrões de desempenho de build**
- Ative `skipLibCheck: true` apenas para verificação de tipos de bibliotecas (frequentemente melhora muito o desempenho em projetos grandes, mas evite mascarar problemas de tipagem da aplicação)
- Use `incremental: true` com cache `.tsbuildinfo`
- Configure `include`/`exclude` com precisão
- Para monorepos: Use project references com `composite: true`

### Resolução de problemas do mundo real

**"The inferred type of X cannot be named"**
- Causa: Export de tipo faltando ou dependência circular
- Prioridade de correção:
  1. Exporte o tipo necessário explicitamente
  2. Use o helper `ReturnType<typeof function>`
  3. Quebre dependências circulares com imports type-only
- Recurso: https://github.com/microsoft/TypeScript/issues/47663

**Declarações de tipo faltando** — correção rápida com declarações ambient:

```typescript
// types/ambient.d.ts
declare module 'some-untyped-package' {
  const value: unknown;
  export default value;
  export = value; // se a interoperabilidade CJS for necessária
}
```
- Mais detalhes: [Guia de Arquivos de Declaração](https://www.typescriptlang.org/docs/handbook/declaration-files/introduction.html)

**"Excessive stack depth comparing types"**
- Causa: Tipos circulares ou profundamente recursivos
- Prioridade de correção:
  1. Limite a profundidade de recursão com tipos condicionais
  2. Use `interface` extends em vez de interseção de tipos
  3. Simplifique as restrições genéricas

```typescript
// Ruim: Recursão infinita
type InfiniteArray<T> = T | InfiniteArray<T>[];

// Bom: Recursão limitada
type NestedArray<T, D extends number = 5> =
  D extends 0 ? T : T | NestedArray<T, [-1, 0, 1, 2, 3, 4][D]>[];
```

**Mistérios de resolução de módulos** — "Cannot find module" mesmo com o arquivo existindo:
  1. Verifique se `moduleResolution` corresponde ao seu bundler
  2. Verifique o alinhamento de `baseUrl` e `paths`
  3. Para monorepos: Garanta o protocolo de workspace (workspace:*)
  4. Tente limpar o cache: `rm -rf node_modules/.cache .tsbuildinfo`

**Mapeamento de paths em runtime**
- Os paths do TypeScript só funcionam em tempo de compilação, não em runtime
- Soluções de runtime no Node.js:
  - ts-node: Use `ts-node -r tsconfig-paths/register`
  - Node ESM: Use alternativas de loader ou evite paths TS em runtime
  - Produção: Pré-compile com os paths resolvidos

### Expertise em migração

**Migração de JavaScript para TypeScript**

```bash
# Estratégia de migração incremental
# 1. Ative allowJs e checkJs (mescle no tsconfig.json existente):
# Adicione ao tsconfig.json existente:
# {
#   "compilerOptions": {
#     "allowJs": true,
#     "checkJs": true
#   }
# }

# 2. Renomeie os arquivos gradualmente (.js -> .ts)
# 3. Adicione tipos arquivo por arquivo com assistência de IA
# 4. Ative os recursos do modo strict um a um

# Ajudantes automatizados (se instalados/necessários)
command -v ts-migrate >/dev/null 2>&1 && npx ts-migrate migrate . --sources 'src/**/*.js'
command -v typesync >/dev/null 2>&1 && npx typesync  # Instala pacotes @types faltantes
```

**Decisões de migração de ferramentas**

| De | Para | Quando | Esforço de Migração |
|------|-----|------|-----------------|
| ESLint + Prettier | Biome | Precisa de muito mais velocidade, ok com menos regras | Baixo (1 dia) |
| TSC para linting | Apenas type-check | Tem 100+ arquivos, precisa de feedback mais rápido | Médio (2-3 dias) |
| Lerna | Nx/Turborepo | Precisa de cache, builds paralelos | Alto (1 semana) |
| CJS | ESM | Node 18+, ferramental moderno | Alto (varia) |

### Project references e múltiplos pacotes

> Orientação genérica. Nos projetos de referência **não há monorepo gerenciado** (sem Nx/Turborepo). Cada lib publicável (`MaxUse`, `MaxPinia`, `MaxComponentsUi`) é um pacote independente que ativa `composite: true` no **seu próprio** `tsconfig.json`.

**Configuração correta de `composite` (por pacote referenciado)**

O padrão do TypeScript é definir `composite: true` **em cada pacote referenciado**, não em um tsconfig raiz agregador. É assim que as libs `Max*` fazem:

```jsonc
// packages/ui/tsconfig.json (cada pacote referenciado)
{
  "compilerOptions": {
    "composite": true,
    "declaration": true,
    "declarationMap": true,
    "moduleResolution": "bundler"
  }
}
```

Um tsconfig raiz opcional apenas **agrega** as referências, sem `composite` próprio:

```jsonc
// tsconfig.json raiz (apenas agrega — não compila código próprio)
{
  "files": [],
  "references": [
    { "path": "./packages/core" },
    { "path": "./packages/ui" },
    { "path": "./apps/web" }
  ]
}
```

Compile a árvore com `tsc --build` (ou `tsc -b`), que respeita as referências e a ordem de dependência.

**Se algum dia adotar um runner de monorepo (genérico, não usado hoje):**
- **Turborepo** para estrutura simples, foco em velocidade, poucos pacotes
- **Nx** para dependências complexas, grafo/visualização e plugins

### Ferramental moderno: ESLint (real) vs Biome (genérico)

> **Nos projetos de referência o padrão é ESLint + typescript-eslint** (com `eslint-plugin-vue` nos pacotes Vue e `@stylistic/eslint-plugin`); nenhum usa Biome. Mantenha ESLint ao trabalhar neles.

**Permaneça com ESLint quando (caso destes projetos):**
- Trabalhar com Vue (suporte limitado do Biome; usa-se `eslint-plugin-vue`)
- Precisar de regras/plugins específicos ou regras customizadas
- Precisar de linting type-aware (o Biome ainda não tem isso)

**Biome só faria sentido (genérico) quando:**
- Velocidade for crítica e você quiser uma única ferramenta lint + format
- Projeto TypeScript-first sem Vue e sem necessidade das regras acima

### Maestria em depuração

**Ferramentas de depuração via CLI**

```bash
# Depurar arquivos TypeScript diretamente (se as ferramentas estiverem instaladas)
command -v tsx >/dev/null 2>&1 && npx tsx --inspect src/file.ts
command -v ts-node >/dev/null 2>&1 && npx ts-node --inspect-brk src/file.ts

# Rastrear problemas de resolução de módulos
npx tsc --traceResolution > resolution.log 2>&1
grep "Module resolution" resolution.log

# Depurar desempenho de verificação de tipos (use --incremental false para um trace limpo)
npx tsc --generateTrace trace --incremental false
# Analisar o trace (se instalado)
command -v @typescript/analyze-trace >/dev/null 2>&1 && npx @typescript/analyze-trace trace

# Análise de uso de memória
node --max-old-space-size=8192 node_modules/typescript/lib/tsc.js
```

**Classes de erro customizadas**

```typescript
// Classe de erro adequada com preservação de stack
class DomainError extends Error {
  constructor(
    message: string,
    public code: string,
    public statusCode: number
  ) {
    super(message);
    this.name = 'DomainError';
    Error.captureStackTrace(this, this.constructor);
  }
}
```

### Melhores práticas atuais

**Strict por padrão** — ative o conjunto completo de flags `strict` no tsconfig. Para os valores canônicos e o racional de cada flag, veja a skill typescript-advanced-types-best-practices (seção "Configuração Estrita").

**Abordagem ESM-first**
- Defina `"type": "module"` no package.json
- Use `.mts` para arquivos ESM de TypeScript se necessário
- Configure `"moduleResolution": "bundler"` para ferramentas modernas
- Use imports dinâmicos para CJS: `const pkg = await import('cjs-package')`
  - Nota: `await import()` requer função assíncrona ou top-level await em ESM
  - Para pacotes CJS em ESM: Pode precisar de `(await import('pkg')).default` dependendo da estrutura de exports do pacote e das configurações do seu compilador

### Árvores de decisão rápidas

"Qual ferramenta devo usar?"

```
Apenas verificação de tipos? -> tsc
Verificação de tipos + velocidade de linting crítica? -> Biome
Verificação de tipos + linting abrangente? -> ESLint + typescript-eslint
Teste de tipos? -> Vitest expectTypeOf
Ferramenta de build? -> Projeto com <10 pacotes? Turborepo. Senão? Nx
```

"Como corrijo este problema de desempenho?"

```
Verificação de tipos lenta? -> skipLibCheck, incremental, project references
Builds lentos? -> Verifique a config do bundler, ative o cache
Testes lentos? -> Vitest com threads, evite verificação de tipos nos testes
Language server lento? -> Exclua node_modules, limite arquivos no tsconfig
```

## Checklist de revisão de código

Foco nestes aspectos específicos do domínio ao revisar TypeScript.

Segurança de tipos:
- [ ] Sem tipos `any` implícitos (use `unknown` ou tipos adequados)
- [ ] Verificações estritas de null ativadas e tratadas corretamente
- [ ] Asserções de tipo (`as`) justificadas e mínimas
- [ ] Restrições genéricas definidas adequadamente
- [ ] Uniões discriminadas para tratamento de erros
- [ ] Tipos de retorno declarados explicitamente para APIs públicas

Boas práticas de TypeScript:
- [ ] Prefira `interface` a `type` para formatos de objetos (melhores mensagens de erro)
- [ ] Use const assertions para tipos literais
- [ ] Aproveite type guards e predicados
- [ ] Evite ginástica de tipos quando houver solução mais simples
- [ ] Tipos de template literal usados apropriadamente
- [ ] Branded types para primitivos de domínio

Considerações de desempenho:
- [ ] A complexidade de tipos não causa compilação lenta
- [ ] Sem profundidade excessiva de instanciação de tipos
- [ ] Evite tipos mapeados complexos em caminhos quentes (hot paths)
- [ ] Use `skipLibCheck: true` no tsconfig
- [ ] Project references configuradas para monorepos

Sistema de módulos:
- [ ] Padrões consistentes de import/export
- [ ] Sem dependências circulares
- [ ] Uso adequado de barrel exports (evite over-bundling)
- [ ] Compatibilidade ESM/CJS tratada corretamente
- [ ] Imports dinâmicos para code splitting

Padrões de tratamento de erros:
- [ ] Result types ou uniões discriminadas para erros
- [ ] Classes de erro customizadas com herança adequada
- [ ] Fronteiras de erro type-safe
- [ ] Cases de switch exaustivos com o tipo `never`

Organização de código:
- [ ] Tipos co-localizados com a implementação
- [ ] Tipos compartilhados em módulos dedicados
- [ ] Evite augmentation global de tipos quando possível
- [ ] Uso adequado de arquivos de declaração (.d.ts)

## Restrições

- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.

Limitações de escopo:
- Use esta skill apenas quando a tarefa corresponder claramente ao escopo descrito acima.
- Sempre valide que as mudanças não quebram a funcionalidade existente antes de considerar o problema resolvido.
- Não trate a saída como substituto para validação, testes ou revisão especializada específicos do ambiente.
- Pare e peça esclarecimentos se entradas obrigatórias, permissões, limites de segurança ou critérios de sucesso estiverem faltando.

## Exemplos

Recursos especializados para estudo mais profundo:

Desempenho:
- [TypeScript Wiki Performance](https://github.com/microsoft/TypeScript/wiki/Performance)
- [Type instantiation tracking](https://github.com/microsoft/TypeScript/pull/48077)

Padrões avançados:
- [Type Challenges](https://github.com/type-challenges/type-challenges)
- [Type-Level TypeScript Course](https://type-level-typescript.com)

Ferramentas:
- [Biome](https://biomejs.dev) - Linter/formatter rápido
- [TypeStat](https://github.com/JoshuaKGoldberg/TypeStat) - Correção automática de tipos TypeScript
- [ts-migrate](https://github.com/airbnb/ts-migrate) - Kit de ferramentas de migração

Testes:
- [Vitest Type Testing](https://vitest.dev/guide/testing-types)
- [tsd](https://github.com/tsdjs/tsd) - Teste de tipos standalone
