# MaxGrid — cobertura responsiva diferente da regra do preset

- Data: 16/10/2026.
- Localização: `projects/MaxComponentsUi/src/presetMaxUno.ts:84–117`, `src/components/MaxGrid.vue:22` e `src/components/base/gridSlotRows.ts:17–23,76–118` no repositório referenciado por `projects/MaxComponentsUi`.
- Evidência: o preset aceita uma posição start/end com mobile/tablet/desktop nas duas ordens. O organizador de linhas aceita start/end sem dispositivo e somente end-mobile/mobile-end condicionais; o MaxGrid lhe fornece apenas isMobile.
- Impacto: um token como `s7-start-desktop` gera dimensões e break-before sob media query, mas não cria uma nova linha explícita do MaxGrid. Declarações de fragmentação não substituem o organizador em flexbox comum.
- Encaminhamento: o plano desta sessão documenta a cobertura real. Eventual expansão do componente e seus testes exige tarefa e autorização separadas no repositório da biblioteca. Não houve edição nem execução de testes nesse repositório.
- Não foi encontrado componente/helper ausente que precise ser criado para a atualização documental solicitada. MaxPinia e MaxUse não precisam de alterações para este escopo.
