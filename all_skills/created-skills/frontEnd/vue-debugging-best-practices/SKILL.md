---
name: vue-debugging-best-practices
description: "Use when diagnosing or fixing Vue 3 reactivity bugs, computed refs, refs not updating, watcher timing, stale data, null template refs, lifecycle hook issues, and async component warnings. Covers best practices, debugging strategies, and objectives."
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Depuração no Vue 3

## Objetivo
Diagnosticar e corrigir problemas de runtime, avisos e falhas assíncronas no Vue 3. Use como um roteador: associe o sintoma observado ao guia de referência específico que explica a causa e a correção. Para convenções de desenvolvimento e pegadinhas mais amplas, consulte também `vue`.

## Instruções
Identifique a categoria do sintoma abaixo e abra o guia de referência correspondente para a causa detalhada e a correção.

### Reatividade
- Rastrear re-renderizações e atualizações de estado inesperadas → Veja [reactivity-debugging-hooks](reference/reactivity-debugging-hooks.md)
- Valores de ref não atualizam por falta de acesso a .value → Veja [ref-value-access](reference/ref-value-access.md)
- Estado para de atualizar após desestruturar objetos reativos → Veja [reactive-destructuring](reference/reactive-destructuring.md)
- Refs dentro de arrays, Maps ou Sets não fazem unwrapping → Veja [refs-in-collections-need-value](reference/refs-in-collections-need-value.md)
- Refs aninhados renderizam como [object Object] nos templates → Veja [template-ref-unwrapping-top-level](reference/template-ref-unwrapping-top-level.md)
- Comparações de identidade de proxy reativo sempre retornam false → Veja [reactivity-proxy-identity-hazard](reference/reactivity-proxy-identity-hazard.md)
- Instâncias de terceiros quebram ao serem proxificadas → Veja [reactivity-markraw-for-non-reactive](reference/reactivity-markraw-for-non-reactive.md)
- Watchers disparando apenas uma vez por tick inesperadamente → Veja [reactivity-same-tick-batching](reference/reactivity-same-tick-batching.md)

### Computed
- Getter de computed dispara mutações ou requisições inesperadamente → Veja [computed-no-side-effects](reference/computed-no-side-effects.md)
- Mutar valores de computed faz as mudanças desaparecerem → Veja [computed-return-value-readonly](reference/computed-return-value-readonly.md)
- Valor de computed nunca atualiza após lógica condicional → Veja [computed-conditional-dependencies](reference/computed-conditional-dependencies.md)
- Ordenar ou inverter arrays quebra o estado original (também em métodos usados em v-for) → Veja [computed-array-mutation](reference/computed-array-mutation.md)
- Passar parâmetros para propriedades computed falha → Veja [computed-no-parameters](reference/computed-no-parameters.md)

### Watchers
- Operações assíncronas sobrescrevendo com dados obsoletos → Veja [watch-async-cleanup](reference/watch-async-cleanup.md)
- Criar watchers dentro de callbacks assíncronos → Veja [watch-async-creation-memory-leak](reference/watch-async-creation-memory-leak.md)
- Watcher nunca dispara para propriedades de objeto reativo → Veja [watch-reactive-property-getter](reference/watch-reactive-property-getter.md)
- watchEffect assíncrono perde dependências após await → Veja [watcheffect-async-dependency-tracking](reference/watcheffect-async-dependency-tracking.md)
- Leituras do DOM ficam obsoletas dentro de callbacks de watcher → Veja [watch-flush-timing](reference/watch-flush-timing.md)
- Watchers profundos reportam valores antigo/novo idênticos → Veja [watch-deep-same-object-reference](reference/watch-deep-same-object-reference.md)
- watchEffect roda antes de os template refs atualizarem → Veja [watcheffect-flush-post-for-refs](reference/watcheffect-flush-post-for-refs.md)

### Componentes
- Componente filho lança erro "component not found" → Veja [local-components-not-in-descendants](reference/local-components-not-in-descendants.md)
- Listener de clique não dispara em componente customizado → Veja [click-events-on-components](reference/click-events-on-components.md)
- Pai não consegue acessar dados de ref do filho em script setup → Veja [component-ref-requires-defineexpose](reference/component-ref-requires-defineexpose.md)
- Componente errado renderiza por colisões de nomes → Veja [component-naming-conflicts](reference/component-naming-conflicts.md)
- Estilos do pai não se aplicam a componente multi-raiz → Veja [multi-root-component-class-attrs](reference/multi-root-component-class-attrs.md)

### Props e Emits
- Variáveis referenciadas em defineProps causam erros → Veja [prop-defineprops-scope-limitation](reference/prop-defineprops-scope-limitation.md)
- Componente emite evento não declarado gerando avisos → Veja [declare-emits-for-documentation](reference/declare-emits-for-documentation.md)
- defineEmits usado dentro de função ou condicional → Veja [defineEmits-must-be-top-level](reference/defineEmits-must-be-top-level.md)
- defineEmits com argumentos de tipo e de runtime juntos → Veja [defineEmits-no-runtime-and-type-mixed](reference/defineEmits-no-runtime-and-type-mixed.md)
- Listeners de evento nativo não respondem a cliques → Veja [native-event-collision-with-emits](reference/native-event-collision-with-emits.md)
- Evento de componente dispara duas vezes ao clicar → Veja [undeclared-emits-double-firing](reference/undeclared-emits-double-firing.md)

### Templates
- Erros de compilação de template com instruções → Veja [template-expressions-restrictions](reference/template-expressions-restrictions.md)
- Erros de runtime "Cannot read property of undefined" → Veja [v-if-null-check-order](reference/v-if-null-check-order.md)
- Argumentos dinâmicos de diretiva não funcionam corretamente → Veja [dynamic-argument-constraints](reference/dynamic-argument-constraints.md)
- Elementos v-else renderizando sempre incondicionalmente → Veja [v-else-must-follow-v-if](reference/v-else-must-follow-v-if.md)
- Misturar v-if com v-for causa bugs de precedência e quebra na migração → Veja [no-v-if-with-v-for](reference/no-v-if-with-v-for.md)
- Chamadas de função no template que mutam estado causam bugs imprevisíveis de re-render → Veja [template-functions-no-side-effects](reference/template-functions-no-side-effects.md)
- Componentes filhos em loops mostrando dados undefined → Veja [v-for-component-props](reference/v-for-component-props.md)
- Itens de lista desaparecendo ou trocando de estado inesperadamente → Veja [v-for-key-attribute](reference/v-for-key-attribute.md)
- Erros de off-by-one ao iterar sobre intervalos → Veja [v-for-range-starts-at-one](reference/v-for-range-starts-at-one.md)
- v-show ou v-else não funcionando em elementos template → Veja [v-show-template-limitation](reference/v-show-template-limitation.md)

### Template Refs
- Ref vira null quando o elemento é ocultado condicionalmente → Veja [ts-template-ref-null-handling](reference/ts-template-ref-null-handling.md)
- Índices do array de refs não batem com o array de dados em loops → Veja [template-ref-v-for-order](reference/template-ref-v-for-order.md)
- Renomear template refs quebra silenciosamente no código → Veja [use-template-ref-vue35](reference/use-template-ref-vue35.md)

### Formulários e v-model
- Valores iniciais do formulário não aparecem ao usar v-model → Veja [v-model-ignores-html-attributes](reference/v-model-ignores-html-attributes.md)
- Mudanças no conteúdo do textarea não atualizam o ref → Veja [textarea-no-interpolation](reference/textarea-no-interpolation.md)
- Usuários de iOS não conseguem selecionar a primeira opção do dropdown → Veja [select-initial-value-ios-bug](reference/select-initial-value-ios-bug.md)
- Componentes pai e filho têm valores diferentes → Veja [define-model-default-value-sync](reference/define-model-default-value-sync.md)
- Mudanças em propriedade de objeto não sincronizam com o pai → Veja [definemodel-object-mutation-no-emit](reference/definemodel-object-mutation-no-emit.md)
- Busca/validação em tempo real quebrada para entrada chinesa/japonesa → Veja [v-model-ime-composition](reference/v-model-ime-composition.md)
- Input numérico retorna string vazia em vez de zero → Veja [v-model-number-modifier-behavior](reference/v-model-number-modifier-behavior.md)
- Estado de checkbox precisa ser transformado antes de enviar via apiPostRoute → Veja [checkbox-true-false-value-form-submission](reference/checkbox-true-false-value-form-submission.md)

### Eventos e Modificadores
- Encadear múltiplos modificadores de evento produz resultados inesperados → Veja [event-modifier-order-matters](reference/event-modifier-order-matters.md)
- Atalhos de teclado não disparam com teclas modificadoras do sistema → Veja [keyup-modifier-timing](reference/keyup-modifier-timing.md)
- Atalhos de teclado disparam com combinações de modificadores indesejadas → Veja [exact-modifier-for-precise-shortcuts](reference/exact-modifier-for-precise-shortcuts.md)
- Combinar modificadores passive e prevent quebra o comportamento do evento → Veja [no-passive-with-prevent](reference/no-passive-with-prevent.md)

### Ciclo de Vida
- Vazamentos de memória por listeners de evento não removidos → Veja [cleanup-side-effects](reference/cleanup-side-effects.md)
- Acesso ao DOM falha antes de o componente montar → Veja [lifecycle-dom-access-timing](reference/lifecycle-dom-access-timing.md)
- Leituras do DOM retornam valores obsoletos após mudanças de estado → Veja [dom-update-timing-nexttick](reference/dom-update-timing-nexttick.md)
- Hooks de ciclo de vida registrados assincronamente nunca rodam → Veja [lifecycle-hooks-synchronous-registration](reference/lifecycle-hooks-synchronous-registration.md)

### Slots
- Acessar dados do componente filho no conteúdo do slot retorna undefined → Veja [slot-render-scope-parent-only](reference/slot-render-scope-parent-only.md)
- Misturar slots nomeados e com escopo causa erros de compilação → Veja [slot-named-scoped-explicit-default](reference/slot-named-scoped-explicit-default.md)
- Usar v-slot em elementos HTML nativos causa erros de compilação → Veja [slot-v-slot-on-components-or-templates-only](reference/slot-v-slot-on-components-or-templates-only.md)
- Posicionamento inesperado de conteúdo pelo comportamento implícito do slot default → Veja [slot-implicit-default-content](reference/slot-implicit-default-content.md)
- Props de slot com escopo sem a propriedade name esperada → Veja [slot-name-reserved-prop](reference/slot-name-reserved-prop.md)
- Componentes wrapper quebrando a funcionalidade de slot do filho → Veja [slot-forwarding-to-child-components](reference/slot-forwarding-to-child-components.md)

### Provide/Inject
- Chamar provide após operações assíncronas falha silenciosamente → Veja [provide-inject-synchronous-setup](reference/provide-inject-synchronous-setup.md)
- Rastrear de onde vêm os valores providos → Veja [provide-inject-debugging-challenges](reference/provide-inject-debugging-challenges.md)
- Valores injetados não atualizam quando o provedor muda → Veja [provide-inject-reactivity-not-automatic](reference/provide-inject-reactivity-not-automatic.md)
- Múltiplos componentes compartilham o mesmo objeto default → Veja [provide-inject-default-value-factory](reference/provide-inject-default-value-factory.md)

### Attrs
- Handlers de evento internos e de fallthrough executam ambos → Veja [attrs-event-listener-merging](reference/attrs-event-listener-merging.md)
- Atributos explícitos sobrescritos por valores de fallthrough → Veja [fallthrough-attrs-overwrite-vue3](reference/fallthrough-attrs-overwrite-vue3.md)
- Atributos aplicando-se ao elemento errado em wrappers → Veja [inheritattrs-false-for-wrapper-components](reference/inheritattrs-false-for-wrapper-components.md)

### Composables
- Composable chamado fora do contexto de setup ou assincronamente → Veja [composable-call-location-restrictions](reference/composable-call-location-restrictions.md)
- Dependência reativa do composable não atualiza quando a entrada muda → Veja [composable-tovalue-inside-watcheffect](reference/composable-tovalue-inside-watcheffect.md)
- Composable muta estado externo inesperadamente → Veja [composable-avoid-hidden-side-effects](reference/composable-avoid-hidden-side-effects.md)
- Desestruturar retornos de composable quebra a reatividade inesperadamente → Veja [composable-naming-return-pattern](reference/composable-naming-return-pattern.md)

### Composition API
- Hooks de ciclo de vida falham silenciosamente após operações assíncronas → Veja [composition-api-script-setup-async-context](reference/composition-api-script-setup-async-context.md)
- Refs do componente pai não conseguem acessar propriedades expostas → Veja [define-expose-before-await](reference/define-expose-before-await.md)
- Padrões de programação funcional quebram a reatividade esperada do Vue → Veja [composition-api-not-functional-programming](reference/composition-api-not-functional-programming.md)
- Modelo mental de React Hooks causa uso incorreto da Composition API → Veja [composition-api-vs-react-hooks-differences](reference/composition-api-vs-react-hooks-differences.md)

### Animação
- Animações não disparam quando nós do DOM são reutilizados → Veja [animation-key-for-rerender](reference/animation-key-for-rerender.md)
- Atualizações de lista do TransitionGroup ficam lentas sob carga → Veja [animation-transitiongroup-performance](reference/animation-transitiongroup-performance.md)

### TypeScript
- Defaults mutáveis de prop vazam estado entre instâncias do componente → Veja [ts-withdefaults-mutable-factory-function](reference/ts-withdefaults-mutable-factory-function.md)
- Tipagem genérica de reactive() causa divergências no unwrapping de refs → Veja [ts-reactive-no-generic-argument](reference/ts-reactive-no-generic-argument.md)
- Template refs lançam erros de acesso a null antes do mount ou após unmount do v-if → Veja [ts-template-ref-null-handling](reference/ts-template-ref-null-handling.md)
- Props booleanas opcionais se comportam como false em vez de undefined → Veja [ts-defineprops-boolean-default-false](reference/ts-defineprops-boolean-default-false.md)
- Tipos importados em defineProps falham com referências de tipo não resolvíveis ou complexas → Veja [ts-defineprops-imported-types-limitations](reference/ts-defineprops-imported-types-limitations.md)
- Handlers de evento do DOM sem tipo falham com TypeScript estrito → Veja [ts-event-handler-explicit-typing](reference/ts-event-handler-explicit-typing.md)
- Refs de componente dinâmico disparam avisos de componente reativo → Veja [ts-shallowref-for-dynamic-components](reference/ts-shallowref-for-dynamic-components.md)
- Expressões de template com tipo união falham na checagem sem narrowing → Veja [ts-template-type-casting](reference/ts-template-type-casting.md)

### Componentes Assíncronos
- Componentes de rota mal configurados com lazy loading de defineAsyncComponent → Veja [async-component-vue-router](reference/async-component-vue-router.md)
- Falhas de rede ou timeouts ao carregar componentes → Veja [async-component-error-handling](reference/async-component-error-handling.md)
- Template refs undefined após reativação do componente → Veja [async-component-keepalive-ref-issue](reference/async-component-keepalive-ref-issue.md)

### Render Functions
- Saída da render function fica estática após mudanças de estado → Veja [rendering-render-function-return-from-setup](reference/rendering-render-function-return-from-setup.md)
- Instâncias de vnode reutilizadas renderizam incorretamente → Veja [render-function-vnodes-must-be-unique](reference/render-function-vnodes-must-be-unique.md)
- Nomes de componente em string renderizam como elementos HTML → Veja [rendering-resolve-component-for-string-names](reference/rendering-resolve-component-for-string-names.md)
- Acessar internos de vnode quebra em atualizações do Vue → Veja [render-function-avoid-internal-vnode-properties](reference/render-function-avoid-internal-vnode-properties.md)
- Padrões de render function do Vue 2 quebram no Vue 3 → Veja [rendering-render-function-h-import-vue3](reference/rendering-render-function-h-import-vue3.md)
- Conteúdo de slot não renderiza a partir de h() → Veja [rendering-render-function-slots-as-functions](reference/rendering-render-function-slots-as-functions.md)

### KeepAlive
- Componentes filhos montam duas vezes com rotas aninhadas do Vue Router → Veja [keepalive-router-nested-double-mount](reference/keepalive-router-nested-double-mount.md)
- Memória cresce ao combinar KeepAlive com animações de Transition → Veja [keepalive-transition-memory-leak](reference/keepalive-transition-memory-leak.md)

### Transições
- Hooks de transição JavaScript travam sem o callback done → Veja [transition-js-hooks-done-callback](reference/transition-js-hooks-done-callback.md)
- Animações de movimento falham em elementos de lista inline → Veja [transition-group-flip-inline-elements](reference/transition-group-flip-inline-elements.md)
- Itens de lista saltam em vez de animar suavemente → Veja [transition-group-move-animation-position-absolute](reference/transition-group-move-animation-position-absolute.md)
- Mudanças de wrapper do TransitionGroup do Vue 2 para o Vue 3 quebram o layout → Veja [transition-group-no-default-wrapper-vue3](reference/transition-group-no-default-wrapper-vue3.md)
- Transições aninhadas são cortadas antes de terminar → Veja [transition-nested-duration](reference/transition-nested-duration.md)
- Estilos com escopo param de funcionar em wrappers de transição reutilizáveis → Veja [transition-reusable-scoped-style](reference/transition-reusable-scoped-style.md)
- Transições do RouterView animam inesperadamente na primeira renderização → Veja [transition-router-view-appear](reference/transition-router-view-appear.md)
- Misturar transições e animações CSS causa problemas de timing → Veja [transition-type-when-mixed](reference/transition-type-when-mixed.md)
- Hooks de cleanup perdidos durante trocas rápidas de transição → Veja [transition-unmount-hook-timing](reference/transition-unmount-hook-timing.md)

### Teleport
- Elemento alvo do Teleport não encontrado no DOM → Veja [teleport-target-must-exist](reference/teleport-target-must-exist.md)
- Estilos com escopo não se aplicam ao conteúdo teleportado → Veja [teleport-scoped-styles-limitation](reference/teleport-scoped-styles-limitation.md)

### Suspense
- Necessidade de tratar erros assíncronos de componentes em Suspense → Veja [suspense-no-builtin-error-handling](reference/suspense-no-builtin-error-handling.md)
- UI de loading/erro de componente assíncrono ignorada sob Suspense → Veja [async-component-suspense-control](reference/async-component-suspense-control.md)

### Performance
- Filhos de lista re-renderizam desnecessariamente porque o pai passa props instáveis → Veja [perf-props-stability-update-optimization](reference/perf-props-stability-update-optimization.md)
- Objetos computed re-disparam efeitos apesar de valores equivalentes → Veja [perf-computed-object-stability](reference/perf-computed-object-stability.md)

### SFC (Single File Components)
- Tentar usar exports nomeados a partir de blocos script do componente → Veja [sfc-named-exports-forbidden](reference/sfc-named-exports-forbidden.md)
- Variáveis não atualizam no template após mudanças → Veja [sfc-script-setup-reactivity](reference/sfc-script-setup-reactivity.md)
- Estilos com escopo não se aplicam a elementos de componente filho → Veja [sfc-scoped-css-child-component-styling](reference/sfc-scoped-css-child-component-styling.md)
- Estilos com escopo não se aplicam a conteúdo dinâmico v-html → Veja [sfc-scoped-css-dynamic-content](reference/sfc-scoped-css-dynamic-content.md)
- Estilos com escopo não se aplicam ao conteúdo de slot → Veja [sfc-scoped-css-slot-content](reference/sfc-scoped-css-slot-content.md)
- Utilitários UnoCSS ausentes quando construídos dinamicamente → Veja [unocss-dynamic-class-generation](reference/unocss-dynamic-class-generation.md)
- Componentes recursivos não renderizam por conflitos de nome → Veja [self-referencing-component-name](reference/self-referencing-component-name.md)

### Plugins
- Depurar por que propriedades globais causam conflitos de nome → Veja [plugin-global-properties-sparingly](reference/plugin-global-properties-sparingly.md)
- Plugin não funcionando ou inject retornando undefined → Veja [plugin-install-before-mount](reference/plugin-install-before-mount.md)
- Propriedades globais de plugin indisponíveis em componentes baseados em setup → Veja [plugin-prefer-provide-inject-over-global-properties](reference/plugin-prefer-provide-inject-over-global-properties.md)
- Erros na augmentação de tipos de plugin quebram a tipagem de ComponentCustomProperties → Veja [plugin-typescript-type-augmentation](reference/plugin-typescript-type-augmentation.md)

### Configuração do App
- Métodos de configuração do app não funcionando após a chamada de mount → Veja [configure-app-before-mount](reference/configure-app-before-mount.md)
- Encadear config do app a partir de mount() falha porque mount retorna a instância do componente → Veja [mount-return-value](reference/mount-return-value.md)

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- Trate cada guia de referência como a fonte de verdade para o seu sintoma específico; não adivinhe uma correção quando existe um guia correspondente.
- Associe pelo sintoma de runtime observado (erro, aviso, valor obsoleto, divergência), não apenas pelo nome da API.
- Para convenções de desenvolvimento e pegadinhas não relacionadas a depuração, recorra a `vue` em vez de duplicar a orientação aqui.
