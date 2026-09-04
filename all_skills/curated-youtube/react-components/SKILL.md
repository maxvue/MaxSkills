---
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
