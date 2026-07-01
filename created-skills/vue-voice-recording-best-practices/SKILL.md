---
name: vue-voice-recording-best-practices
description: Use when implementing, reviewing, or debugging voice recording features, audio file handling, MediaRecorder API usage, and microphone permission requests in Vue 3 components within the Engeapp frontend.
---

# Boas Práticas para Gravação de Voz no Vue 3

## Objetivo
Fornecer diretrizes sólidas, padrões e restrições de segurança para a implementação de recursos de gravação de áudio e voz reativos, performáticos e livres de vazamentos de memória no Vue 3, utilizando a API MediaRecorder e a Web Audio API (`AudioContext`), com `useUserMedia` do MaxUse (`@maxvue/max-use`, que reexporta o VueUse) como caminho recomendado para o acesso ao microfone.

## Instruções

### 1. Estrutura SFC e Convenções
- **Composition API**: É estritamente obrigatório utilizar `<script setup lang="ts">` com TypeScript.
- **Ordem das Seções SFC**: Siga sempre a seguinte sequência:
  1. `<template>`
  2. `<script lang="ts">` / `<script setup lang="ts">`
  3. `<style lang="scss">` / `<style scoped lang="scss">`
- **Formatação de Templates**: Mantenha as tags de componentes Vue e seus atributos em uma única linha no template. Evite quebras de linha para os atributos.
- **Comentários de Código**: Todos os comentários no código-fonte devem ser escritos em português brasileiro (`pt-BR`).

### 2. Microfone e Permissões
- Solicite acesso ao microfone do usuário usando `useUserMedia` do MaxUse (`@maxvue/max-use`, que reexporta o VueUse) ou `navigator.mediaDevices.getUserMedia` nativo.
- Trate recusas de permissão ou indisponibilidade de hardware de forma amigável usando blocos try-catch e notificações de estado reativas.

### 3. Gerenciamento do Ciclo de Vida do MediaRecorder
- **Inicialização**: Instancie o `MediaRecorder` dentro de um watch no stream do microfone ou imediatamente após a resolução dele.
- **Coleta de Dados**: Escute o evento `ondataavailable` e acumule os pedaços (chunks) de áudio em um array reativo de objetos `Blob`.
- **Finalização**: No callback `onstop`, compile o array em um único `Blob` final (normalmente no formato `audio/webm` ou outro suportado pelo navegador) e mapeie-o para uma URL temporária via `URL.createObjectURL(audioBlob)`. Limpe o array de pedaços após isso.

### 3.1. Envio do Áudio ao Backend (MaxPinia)
- Ao persistir o áudio gravado, **NÃO** dispare `axios.post`/`fetch` manuais. Encaminhe o upload através de uma store `@maxvue/max-pinia`, deixando que a camada de cache + salvamento automático cuide da requisição.
- Os caminhos de rota são strings `/api/...` resolvidas por `apiPostRoute` do `@maxvue/max-use` (não há `route()`/Ziggy).
- Para o `Blob`, monte um `FormData` e atribua-o ao campo da store; o auto-save (debounced) envia ao backend Adonis v6 sem submit manual.

### 4. Prevenção de Vazamento de Memória e Liberação de Hardware (CRÍTICO)
- **Limpeza do AudioContext**: Se estiver usando a Web Audio API (`AudioContext`, `AnalyserNode`) para visualizações gráficas:
  - Os objetos `AudioContext` criados devem ser obrigatoriamente fechados quando a gravação terminar ou na desmontagem do componente:
    ```typescript
    if (audioContext.value && audioContext.value.state !== 'closed') {
      await audioContext.value.close();
      audioContext.value = null;
    }
    ```
- **Liberação de Faixas (Tracks)**: Pare explicitamente todas as faixas (tracks) do stream de mídia para apagar o indicador visual de gravação do navegador:
  ```typescript
  stream.value?.getTracks().forEach((track) => track.stop());
  ```
- **Revogação de URLs de Objeto**: Revogue sempre URLs antigas criadas para pré-visualização de áudio usando `URL.revokeObjectURL(audioUrl)` antes de iniciar uma nova gravação e no ciclo de vida `onUnmounted`:
  ```typescript
  onUnmounted(() => {
    if (audioUrl.value) {
      URL.revokeObjectURL(audioUrl.value);
    }
  });
  ```

### 5. Visualização de Áudio (Opcional)
- Conecte um `MediaStreamAudioSourceNode` a um `AnalyserNode` para ler dados em tempo real.
- Renderize ondas sonoras ou barras gráficas reativas utilizando Canvas leves ou elementos SVG/Div de forma otimizada.
- Garanta que o loop de animação (ex: `requestAnimationFrame` ou intervalos) seja imediatamente interrompido quando a gravação parar ou o componente for desmontado.

## Restrições
- **NÃO use Options API**: Não utilize a Options API (`data`, `methods`, etc.) sob nenhuma circunstância.
- **NÃO deixe AudioContext aberto**: Nunca deixe instâncias de `AudioContext` ativas após o término da gravação, pois os navegadores limitam severamente a quantidade de contextos ativos.
- **NÃO bloqueie o microfone**: Não mantenha tracks do stream ativas após encerrar a gravação. Sempre libere o hardware.
- **NÃO acumule Blobs órfãos**: Chame sempre `URL.revokeObjectURL` para liberar referências da memória do navegador.
