# Achados fora da atualização de dimensionamento

Data: 16/10/2026. Evidências obtidas por leitura; nenhum dos pontos abaixo foi corrigido.

## Documentação antiga sobre PrimeVue

- Localizações: `all_skills/created-skills/frontEnd/vue-unocss-styling-best-practices/SKILL.md:51` e `vue-inputs-masks-validation-best-practices/SKILL.md:44`.
- Evidência: a primeira afirma que componentes Max são construídos sobre PrimeVue; a segunda afirma que MaxInputNumber encapsula primevue/inputnumber. As diretrizes atuais de `projects/MaxComponentsUi/AGENTS.md`, fornecidas à sessão, declaram independência concluída e preservação deliberada de classes legadas `.p-*`.
- Impacto: agentes podem supor uma dependência antiga ou propor alterações internas incompatíveis. A presença de classes `.p-*` não prova uso atual de PrimeVue.
- Próxima ação: auditar e corrigir essas orientações em tarefa própria, verificando o fonte de cada componente. Esta sessão não realizou auditoria completa dessa migração.

## Rótulo antigo em teste upstream

- Localização: `projects/MaxComponentsUi/tests/preset/presetMaxUno.test.ts:157–161`.
- Evidência: o nome do teste diz que s-X captura porcentagem para flex; o teste apenas captura dígitos. No mesmo arquivo, os testes dos handlers reais em 433–529 usam os multiplicadores atuais em pixels.
- Impacto: o rótulo pode induzir leitura errada; não há evidência, por esse nome, de falha na implementação ou no resultado da suíte.
- Próxima ação: ajustar o nome em manutenção própria da biblioteca, sem alterar asserções por causa desta atualização das skills.

## Pasta de worktrees não coberta pelo ignore local

- Localização: `.gitignore:1` na worktree MaxSkills.
- Evidência: a regra local cobre `/.worktrees`; `git check-ignore -v .worktrees .max-code-worktrees` retornou correspondência apenas para `.worktrees`.
- Impacto: a regra local não demonstra proteção para o nome usado pelo MaxCode. Não foi investigada a configuração de outras sessões nem alterado o ignore.
- Próxima ação: avaliar cobertura do diretório no contexto da raiz principal e do MaxCode, mediante autorização própria. Não criar outra worktree nem mudar configurações nesta tarefa.
