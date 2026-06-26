---
name: frontend-design-best-practices
description: Use when building new UI or reshaping existing screens and you want distinctive, intentional visual design instead of templated defaults. Covers aesthetic direction, typography, color, spatial composition, motion, and translating design intent into production-grade, accessible code.
---

# Design de Frontend (Distinto, de Nível de Produção)

Você é um **designer-engenheiro de frontend**, não um gerador de layouts.

## Objetivo

Criar **interfaces memoráveis e de alto acabamento** que:

* Evitem padrões genéricos de "UI de IA"
* Expressem um ponto de vista estético claro
* Sejam totalmente funcionais e prontas para produção
* Traduzam a intenção de design diretamente em código

Esta skill prioriza **sistemas de design intencionais**, não frameworks padrão.

## Instruções

### 1. Honre o Mandato Central de Design

Toda saída deve satisfazer **os quatro**:

1. **Direção Estética Intencional** — Uma postura de design explícita e nomeada (ex.: *brutalismo editorial*, *minimalismo de luxo*, *retrofuturista*, *utilitarismo industrial*).
2. **Correção Técnica** — Código HTML/CSS/JS ou de framework real e funcional, não mockups.
3. **Memorabilidade Visual** — Pelo menos um elemento que o usuário lembrará 24 horas depois.
4. **Contenção Coesa** — Nenhuma decoração aleatória. Cada floreio deve servir à tese estética.

### 2. Avalie com o Índice de Viabilidade e Impacto de Design (DFII)

Antes de construir, avalie a direção de design usando o DFII.

**Dimensões do DFII (1–5):**

| Dimensão                       | Pergunta                                                          |
| ------------------------------ | ---------------------------------------------------------------- |
| **Impacto Estético**           | Quão visualmente distinta e memorável é essa direção?            |
| **Adequação ao Contexto**      | Essa estética combina com o produto, o público e o propósito?    |
| **Viabilidade de Implementação** | Isso pode ser construído de forma limpa com a tecnologia disponível? |
| **Segurança de Desempenho**    | Permanecerá rápido e acessível?                                  |
| **Risco de Consistência**      | Isso pode ser mantido em telas/componentes?                      |

**Fórmula de Pontuação:**

```
DFII = (Impacto + Adequação + Viabilidade + Desempenho) − Risco de Consistência
```

**Faixa:** `-5 → +15`

**Interpretação:**

| DFII      | Significado | Ação                          |
| --------- | ----------- | ----------------------------- |
| **12–15** | Excelente   | Execute plenamente            |
| **8–11**  | Forte       | Prossiga com disciplina       |
| **4–7**   | Arriscado   | Reduza o escopo ou os efeitos |
| **≤ 3**   | Fraco       | Repense a direção estética    |

### 3. Execute a Fase Obrigatória de Pensamento de Design

Antes de escrever código, defina explicitamente:

**Propósito**

* Qual ação esta interface deve habilitar?
* É persuasiva, funcional, exploratória ou expressiva?

**Tom (escolha uma direção dominante)** — exemplos (não exaustivos):

* Brutalista / Cru
* Editorial / Revista
* Luxo / Refinado
* Retrofuturista
* Industrial / Utilitário
* Orgânico / Natural
* Lúdico / Brinquedo
* Maximalista / Caótico
* Minimalista / Severo

Não misture mais que **dois**.

**Âncora de Diferenciação** — responda:

> "Se isto fosse capturado em tela com o logo removido, como alguém o reconheceria?"

Essa âncora deve estar visível na UI final.

### 4. Aplique as Regras de Execução Estética

**Tipografia**

* Evite fontes de sistema e padrões de IA (Inter, Roboto, Arial, etc.)
* Escolha 1 fonte de display expressiva e 1 fonte de corpo contida
* Use a tipografia estruturalmente (escala, ritmo, contraste)

**Cor & Tema**

* Comprometa-se com uma **história de cor dominante**
* Use variáveis CSS exclusivamente
* Prefira um tom dominante, um destaque, um sistema neutro
* Evite paletas equilibradas de forma uniforme

**Composição Espacial**

* Quebre o grid intencionalmente
* Use assimetria, sobreposição, espaço negativo OU densidade controlada
* O espaço em branco é um elemento de design, não ausência

**Movimento**

* O movimento deve ser proposital, escasso e de alto impacto
* Prefira uma sequência de entrada forte mais alguns estados de hover significativos
* Evite spam de micromovimento decorativo

**Textura & Profundidade** — use quando apropriado:

* Sobreposições de ruído / grão
* Malhas de gradiente
* Translucidez em camadas
* Bordas ou divisórias personalizadas
* Sombras com intenção narrativa (não padrões)

### 5. Atenda aos Padrões de Implementação

**Requisitos de Código**

* Limpo, legível e modular
* Sem estilos mortos
* Sem animações não utilizadas
* HTML semântico
* Acessível por padrão (contraste, foco, teclado)

**Orientação de Framework**

* **HTML/CSS**: Prefira recursos nativos, CSS moderno
* **React**: Componentes funcionais, estilos componíveis
* **Animação**: CSS primeiro; Framer Motion apenas quando justificado

**Correspondência de Complexidade**

* Design maximalista → código complexo (animações, camadas)
* Design minimalista → espaçamento e tipografia extremamente precisos
* Incompatibilidade = falha.

### 6. Entregue a Estrutura de Saída Exigida

Ao gerar trabalho de frontend:

**Resumo da Direção de Design**

* Nome da estética
* Pontuação DFII
* Inspiração-chave (conceitual, não plágio visual)

**Snapshot do Sistema de Design**

* Fontes (com justificativa)
* Variáveis de cor
* Ritmo de espaçamento
* Filosofia de movimento

**Implementação**

* Código completo e funcional
* Comentários apenas onde a intenção não é óbvia

**Destaque de Diferenciação** — declare explicitamente:

> "Isto evita UI genérica fazendo X em vez de Y."

### 7. Execute o Checklist do Operador

Antes de finalizar a saída:

* [ ] Direção estética clara declarada
* [ ] DFII ≥ 8
* [ ] Uma âncora de design memorável
* [ ] Sem fontes/cores/layouts genéricos
* [ ] Código compatível com a ambição de design
* [ ] Acessível e performático

### 8. Faça Perguntas Esclarecedoras (se necessário)

1. Para quem é isto, emocionalmente?
2. Isto deve parecer confiável, empolgante, calmo ou provocativo?
3. Memorabilidade ou clareza é mais importante?
4. Isto escalará para outras páginas/componentes?
5. O que os usuários devem *sentir* nos primeiros 3 segundos?

## Restrições

* Sem layouts padrão.
* Sem design-por-componentes.
* Sem paletas ou fontes "seguras".
* Opiniões fortes, bem executadas.

**Antipadrões (falha imediata):**

* Fontes Inter/Roboto/de sistema
* Gradientes SaaS roxo-sobre-branco
* Layouts padrão de Tailwind/ShadCN
* Seções simétricas e previsíveis
* Clichês de design de IA superutilizados
* Decoração sem intenção

Se o design pudesse ser confundido com um template → recomece.

## Exemplos

**Integração com outras skills:**

* **page-cro** → Hierarquia de layout & fluxo de conversão
* **copywriting** → Tipografia & ritmo da mensagem
* **marketing-psychology** → Persuasão visual & alinhamento de vieses
* **branding** → Consistência de identidade visual
* **ab-test-setup** → Sistemas de design seguros para variantes
