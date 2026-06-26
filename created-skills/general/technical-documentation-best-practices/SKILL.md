---
name: technical-documentation-best-practices
description: Use when writing or improving technical documentation — READMEs, API endpoints, UI components, ADRs, changelogs, CONTRIBUTING guides, install/config guides, database schemas, or generating docs from existing code. Provides ready templates, formatting rules, and a quality checklist.
---

# Boas Práticas de Documentação Técnica

## Objetivo

Atue como Engenheiro de Documentação Técnica Sênior. Produza documentação que seja:

- **Clara** — Qualquer desenvolvedor entende na primeira leitura
- **Completa** — Cobre todos os cenários relevantes sem ser redundante
- **Estruturada** — Segue padrões e hierarquias lógicas
- **Prática** — Exemplos reais e funcionais, nunca pseudocódigo genérico
- **Manutenível** — Fácil de atualizar conforme o projeto evolui
- **Profissional** — Visual polido com badges, diagramas e formatação impecável

Você escreve para **humanos**, não para máquinas. Documentação é um produto — trate-a como tal. O idioma é português brasileiro (pt-BR) por padrão, inglês quando o usuário solicitar.

Use esta skill quando a tarefa for:

- Criar ou melhorar o `README.md` de um projeto/pacote
- Documentar APIs (endpoints, payloads, respostas, erros)
- Documentar componentes de UI (props, slots, eventos, exemplos)
- Escrever Changelogs e Release Notes
- Criar guias de instalação e configuração
- Documentar decisões arquiteturais (ADRs)
- Gerar JSDoc ou TSDoc para código
- Criar `CONTRIBUTING.md` e guias de contribuição
- Documentar schemas de banco de dados
- Escrever documentação de bibliotecas e SDKs
- Gerar documentação a partir de código existente
- Revisar e melhorar documentação existente

NÃO use esta skill quando a tarefa for exclusivamente escrever/corrigir código (sem documentação), apenas comentários inline simples, marketing/copywriting/conteúdo não-técnico, ou documentação de processos de negócio (não software).

## Instruções

### Princípios Fundamentais

**1. Audiência primeiro.** Antes de escrever, defina: Quem vai ler? (desenvolvedor júnior, sênior, usuário final, contribuidor) O que essa pessoa precisa fazer? (instalar, usar, contribuir, debugar) Qual o nível de conhecimento prévio esperado?

**2. Estrutura padronizada.** Cada tipo de documento tem uma estrutura própria. **Nunca invente estruturas novas** — siga os templates definidos aqui.

**3. Exemplos funcionais.** Todo exemplo de código DEVE funcionar se copiado e colado. Use dados realistas, nunca `foo`, `bar`, `baz`. Mostre o output/resultado esperado quando possível. Inclua exemplos de erro e como tratá-los.

**4. Linguagem.** Frases curtas e diretas. Voz ativa: "Instale o pacote" em vez de "O pacote deve ser instalado". Evite jargões desnecessários — se usar, explique na primeira ocorrência. Use listas e tabelas em vez de parágrafos longos.

**5. Versionamento.** Sempre inclua versão ou data na documentação. Mantenha a compatibilidade com versões anteriores documentada. Use badges para indicar versão, status e compatibilidade.

### Fluxo de Trabalho

**Fase 1 — Análise**

```
1. Examinar o código-fonte e a estrutura do projeto
2. Identificar a audiência-alvo
3. Listar os tópicos que precisam ser documentados
4. Verificar documentação existente (se houver)
5. Identificar lacunas e inconsistências
```

**Fase 2 — Planejamento**

```
1. Escolher o template adequado para cada tipo de documento
2. Definir a ordem dos tópicos (do mais importante ao menos)
3. Listar exemplos de código que precisam ser criados
4. Identificar diagramas necessários (arquitetura, fluxo, ER)
5. Apresentar plano ao usuário para aprovação
```

**Fase 3 — Escrita**

```
1. Escrever seguindo o template escolhido
2. Criar exemplos de código funcionais
3. Adicionar diagramas Mermaid quando apropriado
4. Incluir tabelas de referência (props, parâmetros, etc.)
5. Adicionar badges e shields relevantes
```

**Fase 4 — Revisão**

```
1. Executar o Checklist de Qualidade (seção abaixo)
2. Verificar links e referências cruzadas
3. Garantir consistência de terminologia
4. Validar exemplos de código
5. Revisar formatação Markdown
```

### Padrões de Resposta

**Ao criar documentação nova:** Análise (examinar o código/projeto relevante) → Plano (apresentar estrutura proposta) → Escrita (seguir o template escolhido) → Revisão (aplicar o checklist de qualidade).

**Ao melhorar documentação existente:** Diagnóstico (identificar problemas e lacunas) → Relatório (listar melhorias sugeridas com prioridade) → Execução (aplicar as melhorias aprovadas) → Validação (verificar com checklist).

**Ao documentar código existente:** Leitura (analisar o código em profundidade) → Extração (identificar interfaces públicas, tipos, parâmetros) → Contextualização (entender o propósito e uso) → Documentação (gerar docs seguindo o template relevante).

### Regras de Formatação Markdown

**Estrutura:** Use `#` para o título principal (apenas 1 por documento). Use `##` para seções principais. Use `###` para subseções. Nunca pule níveis (ex: `#` direto para `###`).

**Código:** Sempre especifique a linguagem nos blocos de código (```typescript, ```bash, ```json). Use inline code (`` ` ``) para nomes de variáveis, arquivos, comandos e paths. Exemplos devem ter dados realistas.

**Tabelas:** Use para parâmetros, props, configurações e comparações. Alinhe as colunas para legibilidade no código-fonte. Sempre inclua header e separador.

**Diagramas:** Use Mermaid para diagramas de arquitetura, fluxo e relacionamento. Mantenha diagramas simples — máximo 15 nós. Adicione labels descritivos nas conexões.

**Emojis** — use com moderação para melhorar a escaneabilidade:

| Emoji | Uso                    |
|-------|------------------------|
| ✨    | Funcionalidades        |
| 🚀    | Instalação/Deploy      |
| 📋    | Pré-requisitos         |
| 💡    | Uso/Exemplos           |
| 📖    | Documentação           |
| 🏗️    | Arquitetura            |
| 🧪    | Testes                 |
| 🤝    | Contribuição           |
| 📄    | Licença                |
| ⚠️    | Avisos                 |
| ❌    | Erros/Problemas        |
| ✅    | Sucesso/Correto        |

**Badges (Shields.io)** — adicione badges relevantes no topo do README:

```markdown
![Versão](https://img.shields.io/badge/versão-1.0.0-blue)
![Licença](https://img.shields.io/badge/licença-MIT-green)
![Node](https://img.shields.io/badge/Node-20+-green)
![AdonisJS](https://img.shields.io/badge/AdonisJS-6-blueviolet)
![Testes](https://img.shields.io/badge/testes-passando-brightgreen)
```

### Checklist de Qualidade

Antes de finalizar qualquer documentação, verifique:

**Conteúdo**

- [ ] Audiência-alvo claramente definida
- [ ] Todos os tópicos relevantes cobertos
- [ ] Exemplos de código são funcionais e testáveis
- [ ] Dados dos exemplos são realistas (não `foo`, `bar`)
- [ ] Cenários de erro documentados
- [ ] Pré-requisitos listados
- [ ] Versão/data incluída

**Estrutura**

- [ ] Template adequado seguido
- [ ] Hierarquia de headings correta (sem pular níveis)
- [ ] Sumário/índice para documentos longos (>5 seções)
- [ ] Links internos funcionam
- [ ] Tabelas usadas para dados tabulares

**Formatação**

- [ ] Blocos de código com linguagem especificada
- [ ] Inline code para termos técnicos
- [ ] Markdown renderiza corretamente
- [ ] Emojis usados com moderação
- [ ] Badges relevantes incluídos (para READMEs)

**Clareza**

- [ ] Frases curtas e diretas
- [ ] Voz ativa predominante
- [ ] Jargões explicados na primeira ocorrência
- [ ] Sem ambiguidades ou instruções vagas
- [ ] Cada seção pode ser lida independentemente

## Restrições

- Sempre analise o código antes de documentar — nunca invente funcionalidades
- Siga o template adequado — não crie estruturas ad-hoc
- Exemplos devem ser extraídos ou baseados no código real do projeto
- Mantenha consistência de estilo dentro do mesmo projeto
- Pergunte ao usuário quando houver ambiguidade sobre escopo ou audiência
- Documentação em português brasileiro (pt-BR) por padrão
- Não trate a saída como substituto para revisão de pares ou validação técnica
- Pare e peça esclarecimentos se informações essenciais estiverem faltando

**Anti-padrões a evitar:**

- ❌ Documentação gerada sem analisar o código-fonte
- ❌ Exemplos com dados genéricos (`foo`, `bar`, `test`)
- ❌ Blocos de código sem linguagem especificada
- ❌ Parágrafos longos onde tabelas seriam mais claras
- ❌ Copiar/colar sem adaptar ao contexto do projeto
- ❌ Documentação que repete o código sem agregar valor
- ❌ Omitir cenários de erro e edge cases
- ❌ Ignorar versionamento e datas
- ❌ Estrutura inconsistente entre documentos do mesmo projeto

## Exemplos

### Template: README.md de Projeto

```markdown
<p align="center">
  <img src="logo.png" alt="Nome do Projeto" width="200">
</p>

<h1 align="center">Nome do Projeto</h1>

<p align="center">
  Descrição breve e impactante do que o projeto faz — máximo 2 linhas.
</p>

<p align="center">
  <a href="#instalação">Instalação</a> •
  <a href="#uso-rápido">Uso Rápido</a> •
  <a href="#documentação">Documentação</a> •
  <a href="#contribuição">Contribuição</a> •
  <a href="#licença">Licença</a>
</p>

---

## ✨ Funcionalidades

- 🚀 Funcionalidade principal 1 — breve descrição
- 🔧 Funcionalidade principal 2 — breve descrição
- 📦 Funcionalidade principal 3 — breve descrição

## 📋 Pré-requisitos

- Node.js >= 18.0
- npm >= 9.0 ou yarn >= 1.22

## 🚀 Instalação

### npm
\```bash
npm install nome-do-pacote
\```

### yarn
\```bash
yarn add nome-do-pacote
\```

## 💡 Uso Rápido

\```typescript
import { MinhaClasse } from 'nome-do-pacote';

const instancia = new MinhaClasse({
  opcao: 'valor',
});

const resultado = instancia.executar();
console.log(resultado); // { sucesso: true, dados: [...] }
\```

## 📖 Documentação

### Configuração

| Opção       | Tipo      | Padrão   | Descrição                    |
|-------------|-----------|----------|------------------------------|
| `opcao1`    | `string`  | `''`     | Descrição da opção 1         |
| `opcao2`    | `number`  | `0`      | Descrição da opção 2         |
| `opcao3`    | `boolean` | `false`  | Descrição da opção 3         |

### Métodos

#### `executar(params?: Opcoes): Resultado`

Descrição do que o método faz.

**Parâmetros:**

| Nome     | Tipo     | Obrigatório | Descrição              |
|----------|----------|-------------|------------------------|
| `params` | `Opcoes` | Não         | Opções de configuração |

**Retorno:** `Resultado`

**Exemplo:**

\```typescript
const resultado = instancia.executar({ filtro: 'ativo' });
\```

## 🏗️ Arquitetura

\```mermaid
graph TD
    A[Entrada] --> B[Processamento]
    B --> C[Validação]
    C --> D[Saída]
\```

## 🧪 Testes

\```bash
# Executar todos os testes
npm test

# Executar com cobertura
npm run test:coverage

# Executar testes específicos
npm test -- --filter="nome-do-teste"
\```

## 🤝 Contribuição

Veja [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes.

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).
```

### Template: Documentação de API Endpoint

```markdown
## `POST /api/v1/recurso`

Descrição clara do que este endpoint faz.

### Autenticação

Requer sessão autenticada (guard `web`, cookie de sessão). O front consome este endpoint através de uma store `@maxvue/max-pinia` — o cookie de sessão é enviado automaticamente pelo navegador.

### Headers

| Header          | Valor                | Obrigatório |
|-----------------|----------------------|-------------|
| `Content-Type`  | `application/json`   | Sim         |
| `Accept`        | `application/json`   | Sim         |

### Parâmetros de Query

| Parâmetro  | Tipo     | Obrigatório | Descrição                |
|------------|----------|-------------|--------------------------|
| `pagina`   | `int`    | Não         | Número da página (padrão: 1) |
| `limite`   | `int`    | Não         | Itens por página (padrão: 15) |

> O consumo no front passa por uma store `@maxvue/max-pinia` (caminho string resolvido por `apiGetRoute`/`apiPostRoute` para `/api/...`), nunca por `axios.get`/`axios.post` manual. Alterações de dados são persistidas via auto-save (debounced) da store.

### Body (JSON)

\```json
{
  "nome": "Exemplo",
  "email": "usuario@exemplo.com",
  "ativo": true
}
\```

| Campo   | Tipo      | Obrigatório | Regras de Validação      |
|---------|-----------|-------------|--------------------------|
| `nome`  | `string`  | Sim         | min:3, max:255           |
| `email` | `string`  | Sim         | email válido, único      |
| `ativo` | `boolean` | Não         | padrão: true             |

### Respostas

#### ✅ 201 — Criado com Sucesso

\```json
{
  "data": {
    "id": 42,
    "nome": "Exemplo",
    "email": "usuario@exemplo.com",
    "ativo": true,
    "criado_em": "2026-05-24T00:00:00Z"
  }
}
\```

#### ❌ 422 — Erro de Validação

\```json
{
  "message": "Os dados fornecidos são inválidos.",
  "errors": {
    "email": ["O campo email já está em uso."]
  }
}
\```

#### ❌ 401 — Sessão Não Autenticada

\```json
{
  "message": "Sessão não autenticada."
}
\```
```

### Template: Documentação de Componente UI

```markdown
## `<NomeDoComponente />`

Descrição do que o componente faz e quando usá-lo.

### Uso Básico

\```vue
<template>
  <NomeDoComponente
    titulo="Meu Título"
    :itens="listaDeItens"
    @selecionar="aoSelecionar"
  />
</template>

<script setup lang="ts">
// Componentes Max e helpers (ref, etc.) chegam por auto-import
// (unplugin-vue-components / unplugin-auto-import). Não importe manualmente.
const listaDeItens = ref([
  { id: 1, nome: 'Item 1' },
  { id: 2, nome: 'Item 2' },
]);

function aoSelecionar(item: Item) {
  console.log('Selecionado:', item);
}
</script>
\```

### Props

| Prop        | Tipo        | Padrão    | Obrigatório | Descrição                 |
|-------------|-------------|-----------|-------------|---------------------------|
| `titulo`    | `string`    | `''`      | Sim         | Título exibido no topo    |
| `itens`     | `Item[]`    | `[]`      | Não         | Lista de itens            |
| `carregando`| `boolean`   | `false`   | Não         | Estado de carregamento    |
| `variante`  | `'primario' \| 'secundario'` | `'primario'` | Não | Estilo visual |

### Eventos

| Evento       | Payload     | Descrição                       |
|--------------|-------------|---------------------------------|
| `selecionar` | `Item`      | Emitido ao selecionar um item   |
| `fechar`     | `void`      | Emitido ao fechar o componente  |

### Slots

| Slot      | Props           | Descrição                          |
|-----------|-----------------|------------------------------------|
| `default` | `{ item: Item }`| Conteúdo personalizado de cada item|
| `vazio`   | —               | Exibido quando não há itens        |
| `rodape`  | —               | Conteúdo do rodapé                 |

### Exemplos Avançados

#### Com slot personalizado

\```vue
<NomeDoComponente :itens="itens">
  <template #default="{ item }">
    <div class="item-customizado">
      <strong>{{ item.nome }}</strong>
      <span>{{ item.descricao }}</span>
    </div>
  </template>
</NomeDoComponente>
\```

#### Com estado de carregamento

\```vue
<NomeDoComponente :itens="itens" :carregando="estaCarregando">
  <template #vazio>
    <p>Nenhum item encontrado.</p>
  </template>
</NomeDoComponente>
\```
```

### Template: ADR (Architecture Decision Record)

```markdown
# ADR-001: Título da Decisão

**Data:** 2026-05-24
**Status:** Aceita | Proposta | Deprecada | Substituída por ADR-XXX
**Decisores:** Nome 1, Nome 2

## Contexto

Descreva o contexto e a situação que levou à necessidade desta decisão.
Inclua requisitos técnicos e de negócio relevantes.

## Decisão

Descreva a decisão tomada de forma clara e direta.

**Escolhemos [OPÇÃO X] porque:**

1. Razão 1
2. Razão 2
3. Razão 3

## Alternativas Consideradas

### Opção A — Nome da Opção

- ✅ Vantagem 1
- ✅ Vantagem 2
- ❌ Desvantagem 1
- ❌ Desvantagem 2

### Opção B — Nome da Opção

- ✅ Vantagem 1
- ❌ Desvantagem 1
- ❌ Desvantagem 2

## Consequências

### Positivas

- Benefício 1
- Benefício 2

### Negativas

- Trade-off 1
- Trade-off 2

### Riscos

- Risco 1 — Mitigação: como mitigar
- Risco 2 — Mitigação: como mitigar
```

### Template: Changelog (Keep a Changelog)

```markdown
# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não Publicado]

### Adicionado
- Nova funcionalidade X para resolver o problema Y

### Alterado
- Refatorado o módulo Z para melhor performance

## [1.2.0] — 2026-05-24

### Adicionado
- Suporte a filtros avançados na listagem (#123)
- Exportação de dados em CSV (#124)
- Documentação completa da API

### Corrigido
- Erro de validação ao salvar formulário vazio (#125)
- Timeout em consultas com muitos registros (#126)

### Removido
- Suporte ao Node 18 (mínimo agora é Node 20)

## [1.1.0] — 2026-04-15

### Adicionado
- Autenticação via OAuth2

### Segurança
- Atualização de dependências com vulnerabilidades conhecidas
```

### Template: CONTRIBUTING.md

```markdown
# Guia de Contribuição

Obrigado pelo interesse em contribuir! Este guia explica como participar do projeto.

## 🚀 Como Começar

1. Faça um fork do repositório
2. Clone o fork localmente
3. Crie uma branch para sua feature/fix

\```bash
git checkout -b feature/minha-feature
\```

4. Faça suas alterações
5. Commit seguindo o padrão (veja abaixo)
6. Abra um Pull Request

## 📝 Padrão de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/pt-br/):

\```
tipo(escopo): descrição breve

corpo detalhado (opcional)

rodapé (opcional)
\```

**Tipos permitidos:**

| Tipo       | Descrição                              |
|------------|----------------------------------------|
| `feat`     | Nova funcionalidade                    |
| `fix`      | Correção de bug                        |
| `docs`     | Alteração em documentação              |
| `style`    | Formatação (sem mudança de lógica)     |
| `refactor` | Refatoração de código                  |
| `test`     | Adição ou correção de testes           |
| `chore`    | Manutenção geral (build, CI, deps)     |

## 🧪 Testes

Antes de enviar um PR, garanta que:

\```bash
# Todos os testes passam
npm test

# O linter não reporta erros
npm run lint

# O build completa sem erros
npm run build
\```

## 📋 Checklist do Pull Request

- [ ] Código segue os padrões do projeto
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada (se aplicável)
- [ ] Nenhum warning no linter
- [ ] Build passa sem erros
```
