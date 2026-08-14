# Instruções para Atualização do list-skills.yaml

Este documento descreve o procedimento completo para atualizar a lista de skills no arquivo `list-skills.yaml`, garantindo que ele reflita sempre o estado atual do repositório.

---

## Passos para a Atualização

### 1. Verificar Propostas Existentes
Analise o diretório `proposals-skills/` para identificar todas as propostas de skills (novas ou melhorias) que foram elaboradas. Leia o resumo de cada uma.

### 2. Verificar Skills Concluídas
Analise o diretório `created-skills/` para identificar quais das propostas já foram executadas e implementadas como skills definitivas.

### 3. Preencher os Dados no YAML
Cada item da lista deverá conter os seguintes campos:

| Campo | Descrição | Valores Permitidos |
|-------|-----------|-------------------|
| `nome` | Nome identificador da skill (kebab-case) | Ex: `laravel-jobs-queues-horizon-best-practices` |
| `action` | Tipo de ação | `CRIAR` (skill nova) ou `ATUALIZAR` (melhoria de skill existente) |
| `status` | Estado atual da proposta | Ver tabela de status abaixo |
| `resumo` | Texto breve descrevendo o propósito | Baseado no documento de proposta |
| `workflows` | Lista de workflows que usarão a skill | Lista YAML ou `[]` se nenhum |

**Tabela de Status:**

| Status | Significado | Regra |
|--------|------------|-------|
| `AGUARDANDO EXECUÇÃO` | Proposta pronta para elaboração | Aguardando agente para execução |
| `EXECUTANDO` | Proposta em processo ativo de desenvolvimento | Definido no início da execução |
| `CONCLUIDA` | Proposta executada e validada | Somente se existir na pasta `created-skills/` |
| `MESCLADA` | Conteúdo absorvido por outra skill | Terminal — nunca reexecutar; manter como rastro histórico |
| `DESCONTINUADA` | Proposta abandonada (fora do stack canônico) | Terminal — nunca reexecutar; manter como rastro histórico |

### 4. Ordenação dos Itens (OBRIGATÓRIA)
Sempre ordene os itens de cima para baixo na seguinte prioridade:
1. `AGUARDANDO EXECUÇÃO` (topo absoluto)
3. `EXECUTANDO`
4. `CONCLUIDA` (final do arquivo)
5. `MESCLADA` (Itens absorvidos por outra skill)
6. `DESCONTINUADA` (Itens abandonados — final absoluto do arquivo)

### 5. Tratamento de Situações Especiais
- **Proposta rejeitada pelo usuário:** Remova o item do `list-skills.yaml` e exclua o arquivo de proposta correspondente da pasta `proposals-skills/`.
- **Entradas duplicadas:** Se dois itens possuem o mesmo nome ou propósito muito semelhante, mantenha apenas o mais recente e informe ao usuário.
- **Skill removida:** Se uma skill existente na `created-skills/` foi excluída, remova também o item correspondente do YAML.
- **Inconsistência de dados:** Se um item está marcado como `CONCLUIDA` mas não existe na pasta `created-skills/`, corrija o status para `AGUARDANDO EXECUÇÃO`.
- **Skill absorvida por outra:** Se o conteúdo de uma proposta foi incorporado a outra skill, marque o item como `MESCLADA` (não remova) e registre a skill absorvente no resumo.
- **Tecnologia descontinuada:** Se a proposta deixou de fazer sentido (stack abandonado ou decisão do usuário), marque o item como `DESCONTINUADA` (não remova).
- **Status terminais:** Itens `MESCLADA` e `DESCONTINUADA` NÃO são elegíveis para execução na Fase 1 do `index.md` e NÃO devem ser rebaixados pela regra de inconsistência de dados, mesmo sem pasta correspondente em disco.

---

**Exemplo de Estrutura Completa:**

```yaml
skills:
  - nome: nome-da-skill-pendente
    action: CRIAR
    status: AGUARDANDO EXECUÇÃO
    resumo: Resumo descritivo da nova skill e seus objetivos.
    workflows:
      - nome-do-workflow-que-vai-fazer-uso-desta-skill

  - nome: nome-da-skill-finalizada
    action: ATUALIZAR
    status: CONCLUIDA
    resumo: Resumo descritivo da atualização que foi realizada.
    workflows: []
```