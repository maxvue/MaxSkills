# ESTRUTURA DO ARQUIVO list-skills.yaml
1. Cada item da lista deverá conter os seguintes dados:
   - `nome`: O nome identificador da skill (ex: `laravel-jobs-queues-horizon-best-practices`).
   - `action`: 
     - Usar `CRIAR` para itens onde a proposta é a criação de uma skill totalmente nova.
     - Usar `ATUALIZAR` para itens onde a proposta é a melhoria ou atualização de uma skill existente.
   - `status`: 
     - Usar `AGUARDANDO EXECUÇÃO` para propostas prontas para desenvolvimento e aguardando um agente.
     - Usar `EXECUTANDO` para propostas que estão em processo ativo de desenvolvimento.
     - Usar `CONCLUIDA` para propostas que já foram executadas e validadas (já constam na pasta `created-skills`).
   - `resumo`: Um texto breve descrevendo o propósito da skill, baseado no documento de proposta.
   - `workflows`: Lista de workflows que farão uso desta skill.

---

**Exemplo de Estrutura:**

```yaml
skills:
  - nome: nome-da-skill-pendente
    action: CRIAR
    status: AGUARDANDO EXECUÇÃO
    resumo: Resumo descritivo da nova skill e seus objetivos.
    workflows:
      - nome-do-workflow-que-vai-fazer-uso-desta-skill
      - nome-de-outro-workflow-que-vai-fazer-uso-desta-skill

  - nome: nome-da-skill-finalizada
    action: ATUALIZAR
    status: CONCLUIDA
    resumo: Resumo descritivo da atualização que foi realizada.
    workflows:
      - nome-do-workflow-que-vai-fazer-uso-desta-skill
```
