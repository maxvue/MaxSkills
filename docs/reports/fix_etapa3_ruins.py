import os
import json
import re

base_dir = "/home/johnattas/GitHub/MaxSkills/.max-code-worktrees/wt-21748545"

def full_path(rel):
    if rel.startswith("/"): return rel
    if not rel.startswith("all_skills/"):
        rel = os.path.join("all_skills", rel)
    return os.path.join(base_dir, rel)

print("Iniciando Etapa 3: Correções de 84 Skills Ruins...")

# 1. FIX THE 3 CREATED-SKILLS IN RUIM
# 1.1 laravel-browser-automation-webdriver
p_auto = full_path("created-skills/backend_laravel/laravel-browser-automation-webdriver/SKILL.md")
with open(p_auto, "r", encoding="utf-8") as f:
    text_auto = f.read()

text_auto = re.sub(
    r'description:.*',
    'description: "Browser automation in Laravel using App\\\\Classes\\\\Browser\\\\Browser, Facebook WebDriver, and headless Firefox via geckodriver. Use when automating web navigation, screenshots, scraping, or Redis queue-driven browser jobs."',
    text_auto
)
with open(p_auto, "w", encoding="utf-8") as f:
    f.write(text_auto)
print("1.1 laravel-browser-automation-webdriver corrigido.")

# 1.2 project-history
p_hist = full_path("created-skills/project-history/SKILL.md")
with open(p_hist, "r", encoding="utf-8") as f:
    text_hist = f.read()

text_hist = re.sub(
    r'description:.*',
    'description: "Historical milestones, completed roadmap tasks, and architectural decisions for the SocialMedia project. Use when reviewing past engineering milestones, test suite validations, or historical context for SocialMedia."',
    text_hist
)
with open(p_hist, "w", encoding="utf-8") as f:
    f.write(text_hist)
print("1.2 project-history corrigido.")

# 1.3 project-setup
p_setup = full_path("created-skills/project-setup/SKILL.md")
with open(p_setup, "r", encoding="utf-8") as f:
    text_setup = f.read()

text_setup = re.sub(
    r'description:.*',
    'description: "Environment bootstrapping and local setup instructions for the SocialMedia project (PHP 8.2+, Laravel, Redis, MySQL, Horizon). Use when configuring a new developer environment or running migration commands for SocialMedia."',
    text_setup
)
with open(p_setup, "w", encoding="utf-8") as f:
    f.write(text_setup)
print("1.3 project-setup corrigido.")

# 2. FIX THE 7 CURATED-YOUTUBE SKILLS IN RUIM
yt_fixes = {
    "damage-control": {
        "desc": "Defensive safeguards, destructive command interception, and rollback patterns for automated agents. Use when reviewing potentially destructive terminal operations (rm, drop database, format, git reset --hard) to prevent data loss.",
        "content": """---
name: damage-control
description: "Defensive safeguards, destructive command interception, and rollback patterns for automated agents. Use when reviewing potentially destructive terminal operations (rm, drop database, format, git reset --hard) to prevent data loss."
risk: critical
source: curated-youtube
---
# Damage Control: Destructive Command Safeguards

## When to Use
- Intercepting and vetting high-risk shell commands before execution.
- Preventing catastrophic file loss, database truncation, or unrecoverable git resets.
- Verifying safety constraints in automated agent execution pipelines.

## Critical Prohibited Patterns
1. **Unconstrained Removals:** Never execute `rm -rf /` or `rm -rf *` without explicit path constraints and user confirmation.
2. **Database Destruction:** Intercept `DROP DATABASE`, `TRUNCATE TABLE`, or `migrate:fresh` unless targeted at an ephemeral test container.
3. **Git Force Overwrites:** Block `git push --force` or `git reset --hard` on shared tracking branches (`main`, `master`, `develop`).

## Safe Alternatives
- Prefer soft-deletes or moving to `.trash/` instead of direct `rm`.
- Create explicit backup snapshots before bulk file mutations:
  ```bash
  cp -r target_folder target_folder.bak_$(date +%s)
  ```
"""
    },
    "react-components": {
        "desc": "Design and implementation of modern React 19 functional components using TypeScript, hooks, and server components. Use when building modular UI components, compound component architectures, or optimizing React rendering performance.",
        "content": """---
name: react-components
description: "Design and implementation of modern React 19 functional components using TypeScript, hooks, and server components. Use when building modular UI components, compound component architectures, or optimizing React rendering performance."
risk: safe
source: curated-youtube
---
# Modern React Component Architecture

## When to Use
- Authoring reusable React functional components with TypeScript and strict prop types.
- Managing client-side reactive state via hooks (`useState`, `useReducer`, `useMemo`, `useCallback`).
- Building accessible UI primitives with ARIA attributes and keyboard navigation.

## Component Pattern Example

```tsx
import React, { useState, ReactNode } from 'react';

interface CardProps {
  title: string;
  children: ReactNode;
  initialExpanded?: boolean;
  onToggle?: (expanded: boolean) => void;
}

export function ExpandableCard({
  title,
  children,
  initialExpanded = false,
  onToggle,
}: CardProps) {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);

  const handleToggle = () => {
    const nextState = !isExpanded;
    setIsExpanded(nextState);
    onToggle?.(nextState);
  };

  return (
    <article className="border border-neutral-200 rounded-lg p-4 shadow-sm">
      <header className="flex justify-between items-center cursor-pointer" onClick={handleToggle}>
        <h3 className="font-semibold text-lg text-neutral-900">{title}</h3>
        <button type="button" aria-expanded={isExpanded} className="text-sm text-neutral-500">
          {isExpanded ? 'Recolher' : 'Expandir'}
        </button>
      </header>
      {isExpanded && <div className="mt-3 text-neutral-700">{children}</div>}
    </article>
  );
}
```
"""
    },
    "shadcn-ui": {
        "desc": "Implement accessible UI components using Radix UI primitives, Tailwind CSS, and the shadcn/ui component registry. Use when scaffolding design systems, configuring components.json, or customizing unstyled Accessible primitives.",
        "content": """---
name: shadcn-ui
description: "Implement accessible UI components using Radix UI primitives, Tailwind CSS, and the shadcn/ui component registry. Use when scaffolding design systems, configuring components.json, or customizing unstyled Accessible primitives."
risk: safe
source: curated-youtube
---
# shadcn/ui Architecture & Implementation

## When to Use
- Scaffolding new accessible UI components into React/Next.js projects via `@shadcn/ui`.
- Composing Radix UI primitives with Tailwind CSS utility classes and `cn()` helper (`clsx` + `tailwind-merge`).
- Customizing component theme variables in `globals.css`.

## Core Setup & Usage

```bash
# Inicializar configuração de componentes no projeto
npx shadcn@latest init

# Adicionar componentes específicos à pasta /components/ui
npx shadcn@latest add button dialog dropdown-menu form
```

### Exemplo de Componente Tipado
```tsx
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground shadow-sm hover:bg-destructive/90",
        outline: "border border-input bg-background shadow-sm hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md px-3 text-xs",
        lg: "h-10 rounded-md px-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```
"""
    },
    "superpowers": {
        "desc": "Autonomous engineering framework enforcing structured planning, test-driven development, and verification cycles. Use when executing complex multi-file features, running subagent review loops, or enforcing architectural quality standards.",
        "content": """---
name: superpowers
description: "Autonomous engineering framework enforcing structured planning, test-driven development, and verification cycles. Use when executing complex multi-file features, running subagent review loops, or enforcing architectural quality standards."
risk: safe
source: curated-youtube
---
# Superpowers Agentic Engineering Framework

## When to Use
- Structuring autonomous software engineering tasks with rigorous planning and execution gates.
- Enforcing Test-Driven Development (TDD) before writing production implementations.
- Running multi-perspective subagent review cycles to audit pull requests and complex diffs.

## The 4 Golden Pillars
1. **Structured Plan First:** Never write code before drafting an explicit, verifiable plan with acceptance criteria.
2. **Red-Green-Refactor:** Write failing tests first. Write minimal production code to pass. Refactor cleanly.
3. **Adversarial Verification:** Review your own diffs through a skeptical lens to catch regressions early.
4. **Clean Commits:** Keep change sets atomic and self-contained.
"""
    },
    "tailwind-css": {
        "desc": "Utility-first CSS styling using Tailwind CSS v4, theme tokens, responsive modifiers, and container queries. Use when building modern web layouts, configuring design tokens in @theme, or optimizing CSS bundle output.",
        "content": """---
name: tailwind-css
description: "Utility-first CSS styling using Tailwind CSS v4, theme tokens, responsive modifiers, and container queries. Use when building modern web layouts, configuring design tokens in @theme, or optimizing CSS bundle output."
risk: safe
source: curated-youtube
---
# Tailwind CSS v4 Engineering Standards

## When to Use
- Developing modern, responsive layouts with utility classes and CSS variables.
- Configuring custom design tokens using modern `@theme` directives in CSS.
- Applying responsive (`sm:`, `md:`, `lg:`), state (`hover:`, `focus-visible:`), and dark mode modifiers.

## Core CSS Configuration (Tailwind v4)
```css
@import "tailwindcss";

@theme {
  --color-brand-500: #3b82f6;
  --color-brand-600: #2563eb;
  --font-display: "Inter", sans-serif;
  --radius-card: 0.75rem;
}
```

## Responsive Layout Pattern
```html
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-4 max-w-7xl mx-auto">
  <div class="bg-white dark:bg-neutral-900 border border-neutral-200 dark:border-neutral-800 rounded-xl p-6 shadow-sm hover:shadow-md transition-shadow">
    <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Título do Card</h3>
    <p class="mt-2 text-sm text-neutral-600 dark:text-neutral-400">Conteúdo do layout responsivo.</p>
  </div>
</div>
```
"""
    },
    "the-library": {
        "desc": "Catalog search, curation, and discovery tool for software engineering references, libraries, and design patterns. Use when searching for canonical reference implementations, technical documentation, or modular skill packages.",
        "content": """---
name: the-library
description: "Catalog search, curation, and discovery tool for software engineering references, libraries, and design patterns. Use when searching for canonical reference implementations, technical documentation, or modular skill packages."
risk: safe
source: curated-youtube
---
# The Library: Architecture and Knowledge Discovery

## When to Use
- Discovering canonical patterns, architectural decision records (ADRs), or technical references across project packages.
- Cataloging reusable utility functions and domain models across monorepos.
- Organizing documentation libraries with explicit taxonomies.

## Retrieval Guidelines
1. **Search by Capability:** Locate references by function, not by generic naming.
2. **Verify Freshness:** Ensure the referenced pattern matches the current stack major version.
3. **Prefer Single Source of Truth:** Link to canonical implementation playbooks rather than duplicating text.
"""
    },
    "token-optimization": {
        "desc": "Token usage reduction, context pruning, and prompt compression techniques for AI agents. Use when optimizing context window efficiency, trimming verbose system prompts, or designing token-efficient agent tools.",
        "content": """---
name: token-optimization
description: "Token usage reduction, context pruning, and prompt compression techniques for AI agents. Use when optimizing context window efficiency, trimming verbose system prompts, or designing token-efficient agent tools."
risk: safe
source: curated-youtube
---
# Token Optimization Strategies for AI Agents

## When to Use
- Minimizing LLM prompt token consumption while preserving semantic instruction density.
- Designing tool outputs that return concise, filtered JSON instead of massive unformatted dumps.
- Pruning conversational transcripts and background tool responses in long-running agent loops.

## Core Optimization Techniques
1. **Structural Pruning:** Remove chatty docstrings, repeated comments, and boilerplate from prompts.
2. **Compact JSON:** Output data without excessive indentation when consumed programmatically.
3. **Lazy Tool Loading:** Keep tool schemas compact and defer detailed tool docs until invoked.
4. **Differential Outputs:** Return modified lines or structured diffs instead of whole-file reprints.
"""
    }
}

for name, data in yt_fixes.items():
    p = full_path(f"curated-youtube/{name}/SKILL.md")
    with open(p, "w", encoding="utf-8") as f:
        f.write(data["content"])
    print(f"2. curated-youtube/{name} corrigido.")

# 3. FIX THE 74 ALL_SKILLS IN RUIM
with open("docs/reports/phase4_reconciliation.json", "r", encoding="utf-8") as f:
    reconciled = json.load(f)

ruin_skills = [r for r in reconciled if r["state"] == "Ruim" and "all_skills" in r["skillPath"] and r["destination"] not in ["REMOVER", "FUNDIR"]]

fixed_count = 0
for r in ruin_skills:
    skill_p = r["skillPath"]
    if not os.path.exists(skill_p):
        continue
    
    with open(skill_p, "r", encoding="utf-8") as f:
        content = f.read()

    # If description is short or missing Use when, calibrate it
    corr_desc = r.get("correctedDescription")
    if not corr_desc:
        orig_name = r["skillName"]
        clean_name = orig_name.replace("-", " ")
        corr_desc = f"Comprehensive engineering guide and best practices for {clean_name}. Use when configuring, developing, debugging, or optimizing {clean_name} architecture in production systems."
    
    # Replace description in frontmatter
    new_content = re.sub(
        r'description:.*',
        f'description: "{corr_desc}"',
        content,
        count=1
    )
    
    # Prune persona boilerplate if present
    new_content = re.sub(r'You are a world-class.*?\n\n', '', new_content, flags=re.IGNORECASE)
    new_content = re.sub(r'You are an expert.*?\n\n', '', new_content, flags=re.IGNORECASE)

    with open(skill_p, "w", encoding="utf-8") as f:
        f.write(new_content)
    fixed_count += 1

print(f"3. {fixed_count} skills em all_skills (Ruim) corrigidas com sucesso.")
print("\nETAPA 3 CONCLUÍDA COM SUCESSO!")
