---
name: vue-livekit-client-integration-best-practices
description: Use when implementing, reviewing, or debugging LiveKit Client integrations, real-time video/audio streaming, screen sharing, room event listeners, and participant media track rendering in Vue 3 components within the Engeapp frontend.
---

# Boas Práticas de Integração do LiveKit Client no Vue

## Objetivo
Fornecer diretrizes sólidas e padrões estruturados para integrar, gerenciar e otimizar conexões de mídia em tempo real com o LiveKit Client no frontend Vue 3, garantindo ausência de memory leaks, gerenciamento de estado reativo fluído e tratamento adequado de permissões de hardware.

## Instruções

### 1. Conexão e Gerenciamento da Sala (Room)
* **Ciclo de Vida da Sala:** A instanciação do objeto `Room` deve usar `shallowRef` em vez de `ref` para evitar que o Vue rastreie recursivamente a estrutura interna pesada do LiveKit, o que causa problemas de desempenho.
* **Tokens e Configurações:** Solicite dinamicamente o token de conexão ao backend AdonisJS v6 **através de uma store `@maxvue/max-pinia`** (que internamente usa `apiGetRoute('/api/...')` do `@maxvue/max-use` para resolver o caminho string). Nunca faça `axios.get` manual para o token — o GET deve passar pela store. Inicialize a Room com opções robustas para reconexão automática e fluxos adaptativos (adaptive streams).
* **Composables:** Centralize a lógica de conexão, ouvintes da sala (listeners) e estado da conexão dentro de um composable (ex: `useLiveKit.ts`).

### 2. Prevenção de Vazamento de Memória (Memory Leaks - Ciclo de Vida da Track)
* **Rotina de Attach/Detach:** As faixas de mídia (`RemoteTrack` ou `LocalTrack`) devem ser associadas programaticamente a elementos HTML `<video>` ou `<audio>` quando subscritas, e **explicitamente desassociadas** ao cancelar a subscrição ou quando o componente for desmontado.
* **Hooks do Vue:** Sempre limpe os ouvintes de eventos e desassocie as tracks nos hooks `onUnmounted` ou `onBeforeUnmount`.

### 3. Rastreamento de Estado Reativo
* **Detecção de Falantes Ativos (Active Speakers):** Ouça o evento `RoomEvent.ActiveSpeakersChanged` para atualizar a lista de falantes atuais e estilizar a interface do usuário correspondentemente (ex: borda/indicador de falante ativo).
* **Estado dos Participantes:** Acompanhe a adição e remoção de participantes via `RoomEvent.ParticipantConnected` e `RoomEvent.ParticipantDisconnected` usando um array/objeto reativo.

### 4. Permissões de Hardware e Tratamento de Erros
* **Falha Graciosa:** Capture erros durante `room.connect()` ou ao publicar tracks locais. Informe o usuário com notificações amigáveis caso o acesso ao hardware (microfone/câmera) esteja bloqueado.
* **Solicitações de Permissão:** Solicite permissões antes de tentar conectar para garantir uma experiência de usuário mais suave.

## Exemplos

### Componente Renderizador de Track (`LiveKitTrack.vue`)
Este componente garante a associação e desassociação correta das faixas de mídia, eliminando vazamentos de memória.

```vue
<template>
  <div relative w-full h-full>
    <!-- Atributos do template devem ficar na mesma linha; estilização via UnoCSS attributify (presetMaxUno) -->
    <!-- <video>/<audio> nativos são aceitáveis aqui pois LiveKit attach() exige elementos de mídia DOM crus -->
    <video v-if="track.kind === 'video'" ref="videoEl" autoplay playsinline w-full h-full object-cover rounded-lg />
    <audio v-else ref="audioEl" hidden />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue';
import { Track } from 'livekit-client';

const props = defineProps<{
  track: Track;
}>();

const videoEl = ref<HTMLVideoElement | null>(null);
const audioEl = ref<HTMLAudioElement | null>(null);

// Associa a track ao elemento DOM correspondente
const attachTrack = () => {
  const element = props.track.kind === 'video' ? videoEl.value : audioEl.value;
  if (element) {
    props.track.attach(element);
  }
};

// Desassocia a track para evitar vazamento de memória
const detachTrack = () => {
  const element = props.track.kind === 'video' ? videoEl.value : audioEl.value;
  if (element) {
    props.track.detach(element);
  }
};

onMounted(() => {
  attachTrack();
});

onUnmounted(() => {
  detachTrack();
});

// Caso a instância da track mude dinamicamente, atualiza a vinculação
watch(() => props.track, (newTrack, oldTrack) => {
  if (oldTrack) {
    const oldElement = oldTrack.kind === 'video' ? videoEl.value : audioEl.value;
    if (oldElement) oldTrack.detach(oldElement);
  }
  attachTrack();
});
</script>
```

### Composable para Gerenciamento de Sala (`useLiveKit.ts`)
Demonstra como lidar com conexão, atualizações de estado e limpeza de ouvintes.

```typescript
import { ref, shallowRef, onUnmounted } from 'vue';
import { Room, RoomEvent, Participant } from 'livekit-client';

export function useLiveKit() {
  // shallowRef evita que o Vue monitore recursivamente o objeto complexo Room
  const room = shallowRef<Room | null>(null);
  const isConnected = ref<boolean>(false);
  const participants = ref<Participant[]>([]);
  const activeSpeakers = ref<Participant[]>([]);

  const connect = async (url: string, token: string) => {
    if (room.value) {
      await disconnect();
    }

    const newRoom = new Room({
      adaptiveStream: true,
      dynacast: true,
    });

    newRoom.on(RoomEvent.Connected, () => {
      isConnected.value = true;
      participants.value = Array.from(newRoom.remoteParticipants.values());
    });

    newRoom.on(RoomEvent.Disconnected, () => {
      isConnected.value = false;
      participants.value = [];
      activeSpeakers.value = [];
    });

    newRoom.on(RoomEvent.ParticipantConnected, (participant) => {
      participants.value = [...participants.value, participant];
    });

    newRoom.on(RoomEvent.ParticipantDisconnected, (participant) => {
      participants.value = participants.value.filter((p) => p.sid !== participant.sid);
    });

    newRoom.on(RoomEvent.ActiveSpeakersChanged, (speakers) => {
      activeSpeakers.value = speakers;
    });

    try {
      await newRoom.connect(url, token);
      room.value = newRoom;
    } catch (error) {
      console.error('Falha ao conectar na sala LiveKit:', error);
      throw error;
    }
  };

  const disconnect = async () => {
    if (room.value) {
      room.value.removeAllListeners();
      await room.value.disconnect();
      room.value = null;
      isConnected.value = false;
      participants.value = [];
      activeSpeakers.value = [];
    }
  };

  onUnmounted(async () => {
    await disconnect();
  });

  return {
    room,
    isConnected,
    participants,
    activeSpeakers,
    connect,
    disconnect,
  };
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* **Sem Reatividade Profunda no Objeto Room:** Nunca envolva a instância de `Room` em um `ref()` ou `reactive()` padrão. É **obrigatório** usar `shallowRef(room)` para evitar degradação substancial de desempenho.
* **Limpeza de Track Obrigatória:** Cada associação de track (`track.attach()`) deve ter uma desassociação correspondente (`track.detach()`) no `onUnmounted` ou antes de trocar as tracks. Não fazer isso causará vazamentos de memória no navegador e manterá os indicadores de câmera/microfone ativos.
* **Arquitetura de Componentes:** O estilo SFC é obrigatório. Use Composition API (`<script setup lang="ts">`) e estilização via UnoCSS attributify (`presetMaxUno`) com tokens de tema — não use SCSS nem classes CSS nomeadas. Os elementos `<video>`/`<audio>` nativos são aceitáveis por exigência do `attach()` do LiveKit.
* **Atributos Inline:** Dentro do template Vue, mantenha todos os atributos/parâmetros dos componentes na mesma linha. Não quebre os atributos em várias linhas.
* **Idioma dos Comentários:** Comentários de código e docstrings nos blocos de exemplo devem ser escritos em **Português do Brasil (pt-BR)**.
