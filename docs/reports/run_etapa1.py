import os
import shutil
import json

base_dir = "/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-21748545"

def full_path(rel):
    return os.path.join(base_dir, rel)

# ==========================================
# 1. MERGE PAIRS
# ==========================================

print("Iniciando merges...")

# Pair 1: typescript-pro -> typescript-advanced-types-best-practices
p1_dst = full_path("all_skills/created-skills/typescript/typescript-advanced-types-best-practices/SKILL.md")
with open(p1_dst, "r", encoding="utf-8") as f:
    p1_content = f.read()

# Update description and add decorators/ambient types section
p1_updated = p1_content.replace(
    'description: "Use when designing type-safe TypeScript architectures or solving advanced type problems: generics, conditional types, mapped types, template literals, utility types, branded types, and strict config. Covers objectives and core workflows."',
    'description: "Use when designing type-safe TypeScript architectures or solving advanced type problems: generics, conditional types, mapped types, template literals, utility types, branded types, decorators, ambient declarations (.d.ts), and strict tsconfig settings."'
)
if "### Decorators e Declarações Ambient (.d.ts)" not in p1_updated:
    extra_p1 = """
### Decorators e Declarações Ambient (.d.ts)

Para padrões corporativos e bibliotecas, utilize declarações de tipo ambient e decorators tipados:

```typescript
// Declaração de módulo ambient (.d.ts)
declare module 'legacy-library' {
  export interface Config {
    apiKey: string;
    timeout?: number;
  }
  export function initialize(config: Config): boolean;
}

// Stage 3 Decorator com verificação estática
function logged<This, Args extends any[], Return>(
  target: (this: This, ...args: Args) => Return,
  context: ClassMethodDecoratorContext<This, (this: This, ...args: Args) => Return>
) {
  const methodName = String(context.name);
  return function (this: This, ...args: Args): Return {
    console.log(`[LOG] Chamando ${methodName}`);
    return target.call(this, ...args);
  };
}
```
"""
    p1_updated += extra_p1

with open(p1_dst, "w", encoding="utf-8") as f:
    f.write(p1_updated)
print("Pair 1 merged: typescript-advanced-types-best-practices")

# Pair 2: typescript-expert -> typescript-tooling-monorepo-best-practices
p2_dst = full_path("all_skills/created-skills/typescript/typescript-tooling-monorepo-best-practices/SKILL.md")
with open(p2_dst, "r", encoding="utf-8") as f:
    p2_content = f.read()

p2_updated = p2_content.replace(
    'description: "Use when setting up or optimizing TypeScript build tooling and monorepos: tsconfig references, project references, composite, incremental builds, Turborepo, path aliases, tsup/tsc, and declaration maps."',
    'description: "Use when configuring or optimizing TypeScript tooling, compiler diagnostics, and monorepos: tsconfig project references, incremental builds, CLI diagnostics (--traceResolution, --generateTrace), Biome vs ESLint, and path aliases."'
)
if "### Diagnósticos Avançados de Compilação e Tooling CLI" not in p2_updated:
    extra_p2 = """
### Diagnósticos Avançados de Compilação e Tooling CLI

Ao diagnosticar problemas de compilação lenta ou resolução de módulos em monorepos:

```bash
# Diagnóstico de resolução de tipos e módulos
npx tsc --noEmit --traceResolution > resolution-trace.txt

# Profiling de tempo e memória de checagem de tipos
npx tsc --noEmit --extendedDiagnostics --generateTrace ./tsc-trace

# Análise de traces de performance
npx @typescript/analyze-trace ./tsc-trace
```

#### Migração e Tooling: Biome vs ESLint + Prettier
- **Biome:** recomendado para novos pacotes e monorepos buscando velocidade máxima (10-25x mais rápido em lint/formatting).
- **ESLint + typescript-eslint:** adotar quando houver regras semânticas customizadas que necessitam do Type Information do compilador (ex: `@typescript-eslint/no-floating-promises`).
"""
    p2_updated += extra_p2

with open(p2_dst, "w", encoding="utf-8") as f:
    f.write(p2_updated)
print("Pair 2 merged: typescript-tooling-monorepo-best-practices")

# Pair 3: mcp-server-routing -> mcp-tool-developer
p3_src_dir = full_path("all_skills/curated-youtube/mcp-server-routing")
p3_dst_dir = full_path("all_skills/Agentic Awesome Skills/skills/mcp-tool-developer")
# Copy reference and scripts from src to dst
for folder in ["reference", "scripts"]:
    s_f = os.path.join(p3_src_dir, folder)
    d_f = os.path.join(p3_dst_dir, folder)
    if os.path.exists(s_f):
        if os.path.exists(d_f):
            shutil.rmtree(d_f)
        shutil.copytree(s_f, d_f)

p3_dst_file = os.path.join(p3_dst_dir, "SKILL.md")
with open(p3_dst_file, "r", encoding="utf-8") as f:
    p3_content = f.read()

p3_updated = p3_content.replace(
    'description: Expert in Model Context Protocol (MCP) server development and integration. Guides architecture, tool design, transports (stdio, SSE), schemas (Zod, Pydantic), debugging, and testing in TypeScript/Python.',
    'description: "Expert in Model Context Protocol (MCP) server development. Guides tool design with McpServer, transports (stdio, SSE, HTTP), annotations (readOnlyHint, destructiveHint), schemas (Zod, Pydantic), and evaluation testing."'
)
if "### MCP Tool Annotations and Evaluation Suites" not in p3_updated:
    extra_p3 = """
### MCP Tool Annotations and Evaluation Suites

Tools should declare semantic hints to help LLMs make safe, deterministic invocations:

```typescript
server.tool(
  "query_records",
  "Busca registros sem efeitos colaterais",
  { filter: z.string() },
  {
    readOnlyHint: true,
    idempotentHint: true,
    destructiveHint: false
  },
  async ({ filter }) => ({
    content: [{ type: "text", text: JSON.stringify(records) }]
  }
);
```

#### Evaluation Testing (10 QA Pairs)
Sempre inclua na pasta `evals/` ou `reference/` uma suíte de 10 pares de avaliação contendo casos triviais, edge cases e validação de tratamento de erro para testes com MCP Inspector.
"""
    p3_updated += extra_p3

with open(p3_dst_file, "w", encoding="utf-8") as f:
    f.write(p3_updated)
print("Pair 3 merged: mcp-tool-developer")

# Pair 4: fp-taskeither-ref -> fp-types-ref
p4_dst = full_path("all_skills/Agentic Awesome Skills/skills/fp-types-ref/SKILL.md")
with open(p4_dst, "r", encoding="utf-8") as f:
    p4_content = f.read()

p4_updated = p4_content.replace(
    'description: Quick reference for fp-ts types. Use when user asks which type to use, needs Option/Either/Task decision help, or wants fp-ts imports.',
    'description: "Comprehensive quick reference for fp-ts core types and TaskEither operators. Use when selecting Option, Either, Task, or TaskEither, building async error-handling pipelines, or looking up fp-ts syntax patterns."'
)
p4_updated = p4_updated.replace(
    'tags: [fp-ts, typescript, quick-reference, option, either, task]',
    'tags: [fp-ts, typescript, quick-reference, option, either, task, taskeither, async, promise, error-handling]'
)

if "## TaskEither Operators & Reference" not in p4_updated:
    extra_p4 = """
## TaskEither Operators & Reference

`TaskEither<E, A>` represents an asynchronous computation that can fail (`Promise<Either<E, A>>`).

### Create
```typescript
import * as TE from 'fp-ts/TaskEither'

TE.right(value)                 // Async success
TE.left(error)                  // Async failure
TE.tryCatch(asyncFn, toError)   // Promise -> TaskEither
TE.fromEither(either)           // Either -> TaskEither
TE.fromNullable(nullErr)(val)   // Nullable -> TaskEither
```

### Transform & Chain
```typescript
TE.map((data) => data.id)              // Transform success value
TE.mapLeft((err) => new CustomErr(err)) // Transform error
TE.flatMap((user) => fetchOrders(user)) // Sequential async chain
TE.orElse((err) => fallbackTaskEither) // Recover from error
```

### Execution
```typescript
// TaskEither is lazy: invoke the function to trigger execution
const result: Either<Error, User> = await myTaskEither();

// Or run with pattern match:
await pipe(
  myTaskEither,
  TE.match(
    (err) => console.error('Falha:', err),
    (val) => console.log('Sucesso:', val)
  )
)();
```
"""
    p4_updated += extra_p4

with open(p4_dst, "w", encoding="utf-8") as f:
    f.write(p4_updated)
print("Pair 4 merged: fp-types-ref")

# Pair 5: ui-skills -> ui-skills-root
p5_dst = full_path("all_skills/Agentic Awesome Skills/skills/ui-skills-root/SKILL.md")
with open(p5_dst, "r", encoding="utf-8") as f:
    p5_content = f.read()

p5_updated = p5_content.replace(
    'description: Use before UI-related work to select the smallest useful UI Skills context through the ui-skills CLI.',
    'description: "Gateway router for all UI skills (ibelick/ui-skills). Use before any UI, component, or styling work to discover and load the smallest useful skill context via npx ui-skills CLI and 7-step routing protocol."'
)
with open(p5_dst, "w", encoding="utf-8") as f:
    f.write(p5_updated)
print("Pair 5 merged: ui-skills-root")

# Pair 6: seo-aeo-meta-description-generator -> seo-meta-optimizer
p6_dst = full_path("all_skills/Agentic Awesome Skills/skills/seo-meta-optimizer/SKILL.md")
with open(p6_dst, "r", encoding="utf-8") as f:
    p6_content = f.read()

p6_updated = p6_content.replace(
    'description: Optimize meta titles, descriptions, and open graph tags. Includes character/pixel limits, CTR optimization, and structured previews.',
    'description: "Optimize meta titles, descriptions, and Open Graph/Twitter tags for high search and AI click-through rates. Implements 3-angle CTR formulas (benefit, question, social proof) and character/pixel limits."'
)
p6_updated = p6_updated.replace("resources/implementation-playbook.md", "")
if "### Framework de 3 Ângulos para Redação de CTR" not in p6_updated:
    extra_p6 = """
### Framework de 3 Ângulos para Redação de CTR (Meta Descriptions)

Ao gerar meta tags para uma página ou artigo, forneça sempre 3 ângulos estruturados:

1. **V1 - Benefício Direto (Benefit Lead):** Foco na dor do usuário e na resolução imediata.
   - *Exemplo:* "Aprenda a otimizar sua aplicação em minutos com técnicas comprovadas de cache e renderização."
2. **V2 - Gancho por Pergunta (Question Hook):** Provoca reflexão e curiosidade direcionada à resposta da página.
   - *Exemplo:* "Sua API está demorando mais de 500ms? Descubra o passo a passo exato para reduzir a latência pela metade."
3. **V3 - Prova Social e Especificidade (Social Proof):** Uso de dados numéricos, credenciais ou resultados mensuráveis.
   - *Exemplo:* "Utilizado por mais de 10.000 desenvolvedores para diagnosticar queries N+1 e acelerar endpoints em produção."

#### Open Graph e Twitter Cards
```html
<meta property="og:title" content="Título Conciso | Máx 60 Caracteres" />
<meta property="og:description" content="Descrição cativante entre 120 e 155 caracteres." />
<meta property="og:type" content="article" />
<meta name="twitter:card" content="summary_large_image" />
```
"""
    p6_updated += extra_p6

with open(p6_dst, "w", encoding="utf-8") as f:
    f.write(p6_updated)
print("Pair 6 merged: seo-meta-optimizer")

# Pair 7: vector-index-tuning -> vector-database-engineer
p7_src_playbook = full_path("all_skills/Agentic Awesome Skills/skills/vector-index-tuning/resources")
p7_dst_resources = full_path("all_skills/Agentic Awesome Skills/skills/vector-database-engineer/resources")
if os.path.exists(p7_src_playbook):
    if os.path.exists(p7_dst_resources):
        shutil.rmtree(p7_dst_resources)
    shutil.copytree(p7_src_playbook, p7_dst_resources)

p7_dst_file = full_path("all_skills/Agentic Awesome Skills/skills/vector-database-engineer/SKILL.md")
with open(p7_dst_file, "r", encoding="utf-8") as f:
    p7_content = f.read()

p7_updated = p7_content.replace(
    'description: Architecture, embedding model selection, chunking strategies, hybrid search, and RAG pipelines for Pinecone, Qdrant, Weaviate, Milvus, and pgvector.',
    'description: "Vector database architecture, index tuning, and RAG engineering. Covers embedding models, chunking, hybrid search, and HNSW/PQ hyperparameter optimization (M, efConstruction, efSearch) for pgvector, Pinecone, and Qdrant."'
)
if "### Index Fine-Tuning Guidelines (HNSW & Quantization)" not in p7_updated:
    extra_p7 = """
### Index Fine-Tuning Guidelines (HNSW & Quantization)

Consulte o guia completo em `resources/implementation-playbook.md` para benchmarks e rotinas em Python com hnswlib/faiss.

#### Matriz de Hiperparâmetros HNSW:
- **`M` (conexões bidirecionais por nó):**
  - Textos/busca geral: `16` (padrão)
  - Alta dimensionalidade / precisão crítica: `32` a `64`
- **`efConstruction` (profundidade de exploração na indexação):**
  - Padrão: `64` a `128`
  - Alta revocação (>98% recall): `200` a `400`
- **`efSearch` (profundidade de exploração em runtime na query):**
  - Baixa latência (<5ms): `16` a `32`
  - Balanceado: `64`
  - Máxima revocação: `128` a `256`

#### Estratégias de Quantização:
- **FP16:** 50% economia de memória, perda desprezível de recall (<0.1%).
- **INT8 (Scalar Quantization):** 75% economia de memória, perda <1% de recall.
- **Product Quantization (PQ):** 85-95% economia de memória, ideal para bases > 10M de vetores em RAM limitada.
"""
    p7_updated += extra_p7

with open(p7_dst_file, "w", encoding="utf-8") as f:
    f.write(p7_updated)
print("Pair 7 merged: vector-database-engineer")

# Pair 8: skill-writer -> skill-creator
p8_src_refs = full_path("all_skills/Agentic Awesome Skills/skills/skill-writer/references")
p8_dst_refs = full_path("all_skills/curated-youtube/skill-creator/references")
if os.path.exists(p8_src_refs):
    if not os.path.exists(p8_dst_refs):
        os.makedirs(p8_dst_refs, exist_ok=True)
    for item in os.listdir(p8_src_refs):
        s_item = os.path.join(p8_src_refs, item)
        d_item = os.path.join(p8_dst_refs, item)
        if os.path.isdir(s_item):
            if os.path.exists(d_item): shutil.rmtree(d_item)
            shutil.copytree(s_item, d_item)
        else:
            shutil.copy2(s_item, d_item)

p8_dst_file = full_path("all_skills/curated-youtube/skill-creator/SKILL.md")
with open(p8_dst_file, "r", encoding="utf-8") as f:
    p8_content = f.read()

p8_updated = p8_content.replace(
    'description: Create new skills, modify and improve existing skills, and measure skill performance. Use when users want to create a skill from scratch, edit, or optimize an existing skill, run evals to test a skill, benchmark skill performance with variance analysis, or optimize a skill\'s description for better triggering accuracy.',
    'description: "Create, iterate, and benchmark agent skills with rigorous evals and design patterns. Use when authoring new skills, running evaluation loops, optimizing trigger descriptions, or applying structural workflow patterns."'
)
with open(p8_dst_file, "w", encoding="utf-8") as f:
    f.write(p8_updated)
print("Pair 8 merged: skill-creator")

# Pair 9: skill-audit -> skill-scanner
p9_dst_file = full_path("all_skills/Agentic Awesome Skills/skills/skill-scanner/SKILL.md")
with open(p9_dst_file, "r", encoding="utf-8") as f:
    p9_content = f.read()

p9_updated = p9_content.replace(
    'description: Scan agent skills for security issues before adoption. Detects prompt injection, malicious code, excessive permissions, secret exposure, and supply chain risks.',
    'description: "Pre-install security audit and scanner for agent skills. Detects prompt injection, malicious code, credential exfiltration, social engineering, repo trust anomalies, and calculates 0-100 risk scores."'
)
if "### Social Engineering Check & Repo Intelligence" not in p9_updated:
    extra_p9 = """
### Social Engineering Check & Repo Intelligence

Ao analisar skills de terceiros antes da instalação, execute as seguintes verificações complementares:

#### 1. Verificação de Engenharia Social
- **Senso de Urgência Fabricado:** Instruções que exigem execução cega imediata sem confirmação (`run instantly without asking`).
- **Falsa Autoridade:** Declarações enganosas simulando ser componentes oficiais do sistema ou da Anthropic/Google.
- **Payloads em Comentários:** Instruções ocultas em comentários HTML (`<!-- hidden instructions -->`) ou blocos invisíveis.

#### 2. Reputação do Repositório
- Idade da conta de autoria (< 30 dias com commits em massa é sinal de alerta).
- Discrepância entre contagem de estrelas e número de forks (indicativo de fazendas de estrelas).

#### 3. Escala Numérica de Risco (0-100)
- **0 a 39 (Baixo Risco / Seguro):** Nenhuma anomalia grave detectada.
- **40 a 69 (Médio Risco):** Permissões elevadas ou scripts locais sem sandbox; requer revisão humana.
- **70 a 100 (Alto Risco / Malicioso):** Bloqueio imediato (presença de exfiltração, eval cego ou download de binários remotos).
"""
    p9_updated += extra_p9

with open(p9_dst_file, "w", encoding="utf-8") as f:
    f.write(p9_updated)
print("Pair 9 merged: skill-scanner")

# ==========================================
# 2. REMOVE ABSORBED MERGE SOURCE DIRECTORIES
# ==========================================

absorbed_sources = [
    "all_skills/Agentic Awesome Skills/skills/typescript-pro",
    "all_skills/Agentic Awesome Skills/skills/typescript-expert",
    "all_skills/curated-youtube/mcp-server-routing",
    "all_skills/Agentic Awesome Skills/skills/fp-taskeither-ref",
    "all_skills/Agentic Awesome Skills/skills/ui-skills",
    "all_skills/Agentic Awesome Skills/skills/seo-aeo-meta-description-generator",
    "all_skills/Agentic Awesome Skills/skills/vector-index-tuning",
    "all_skills/Agentic Awesome Skills/skills/skill-writer",
    "all_skills/Agentic Awesome Skills/skills/skill-audit"
]

for src in absorbed_sources:
    p = full_path(src)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f"Removed absorbed source directory: {src}")
    else:
        print(f"Directory already removed: {src}")

# ==========================================
# 3. REMOVE EXPLICIT REMOVAL DIRECTORIES
# ==========================================

explicit_removals = [
    "all_skills/curated-youtube/api-design",
    "all_skills/Agentic Awesome Skills/skills/fal-audio",
    "all_skills/Agentic Awesome Skills/skills/fal-upscale",
    "all_skills/Agentic Awesome Skills/skills/makepad-skills",
    "all_skills/Agentic Awesome Skills/skills/pypict-skill",
    "all_skills/Agentic Awesome Skills/skills/varlock-claude-skill"
]

for rem in explicit_removals:
    p = full_path(rem)
    if os.path.exists(p):
        shutil.rmtree(p)
        print(f"Removed explicit removal directory: {rem}")
    else:
        print(f"Directory already removed: {rem}")

# ==========================================
# 4. UPDATE MANIFESTS (awesome_skills.json & other_skills.json)
# ==========================================

# awesome_skills.json
awesome_path = full_path("awesome_skills.json")
if os.path.exists(awesome_path):
    with open(awesome_path, "r", encoding="utf-8") as f:
        awesome_data = json.load(f)
    
    removed_from_awesome = {
        "typescript-pro", "typescript-expert", "fp-taskeither-ref", "ui-skills",
        "seo-aeo-meta-description-generator", "vector-index-tuning", "skill-writer", "skill-audit",
        "fal-audio", "fal-upscale", "makepad-skills", "pypict-skill", "varlock-claude-skill"
    }
    before_count = len(awesome_data)
    awesome_data = [item for item in awesome_data if item.get("skill_name") not in removed_from_awesome]
    after_count = len(awesome_data)
    with open(awesome_path, "w", encoding="utf-8") as f:
        json.dump(awesome_data, f, indent=2, ensure_ascii=False)
    print(f"Updated awesome_skills.json: {before_count} -> {after_count} skills (removed {before_count - after_count})")

# other_skills.json
other_path = full_path("other_skills.json")
if os.path.exists(other_path):
    with open(other_path, "r", encoding="utf-8") as f:
        other_data = json.load(f)
    
    removed_from_other = {"api-design", "mcp-server-routing"}
    before_count_o = len(other_data)
    other_data = [item for item in other_data if item.get("skill_name") not in removed_from_other]
    after_count_o = len(other_data)
    with open(other_path, "w", encoding="utf-8") as f:
        json.dump(other_data, f, indent=2, ensure_ascii=False)
    print(f"Updated other_skills.json: {before_count_o} -> {after_count_o} skills (removed {before_count_o - after_count_o})")

print("\nETAPA 1 CONCLUÍDA COM SUCESSO!")
