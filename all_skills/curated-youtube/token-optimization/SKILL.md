---
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
