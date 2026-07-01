---
name: vue-ai-agent-playground-best-practices
description: Use when designing, building, styling, or debugging Vue 3 frontend components, pages, or Pinia stores for the AI agent interactive playground. Triggers on custom prompts configuration UI, chat interfaces with streaming responses, setting LLM parameters (temperature, max tokens), toggling tools, and displaying model parameters selectors.
---

# Boas Práticas para o Playground de Agentes de IA no Vue

## Objetivo
Estabelecer padrões de codificação e padrões estruturais para criar playgrounds interativos de agentes de IA usando Vue 3, TypeScript e o design system MaxComponentsUi. Garante interfaces de chat reativas com streaming de dados, layouts de painel dividido (split-panel) fluidos, logging correto de execução de ferramentas e vinculação precisa de parâmetros.

## Instruções

### 1. Layout de Painel Dividido (`splitpanes`)
- Divida o playground em uma barra lateral de parâmetros (30% a 40% de largura) e um console de chat principal (60% to 70% de largura) usando a biblioteca `splitpanes`.
- Restrinja os limites de redimensionamento usando os atributos `min-size` e `max-size` para evitar quebras visuais em telas menores.
- Use classes do UnoCSS (como flexbox, grid e bordas) para manter os painéis alinhados e responsivos.

### 2. Painel de Controle de Parâmetros (Barra Lateral)
- **Seletor de Agente:** Use `MaxInputSelect` vinculado ao agente selecionado da store. Carregue a lista de agentes e a configuração do playground (parâmetros padrão, ferramentas disponíveis) por meio de uma store `@maxvue/max-pinia` cacheada — NUNCA via `axios.get` manual. O GET é resolvido pelo `apiGetRoute('/api/...')` dentro da store, e qualquer alteração de parâmetro é persistida automaticamente pelo auto-save (debounced) do MaxPinia.
- **Input de Prompt do Sistema:** Use `MaxInputTextArea` para o campo multilinha de instruções do sistema (linhas personalizadas via prop `rows`).
- **Parâmetros do Modelo (Sliders):** Como o `MaxComponentsUi` não possui um componente slider nativo:
  - Renderize um `<input type="range" min="0" max="1" step="0.1" />` formatado com propriedades de thumb do UnoCSS. Este é o único caso justificado de input nativo, por ausência de componente Max equivalente.
  - Agrupe-o com um `MaxInputText` somente leitura ou um indicador numérico para feedback visual preciso.
- **Tokens Máximos (Max Tokens):** Vincule a um `MaxInputText` (`type="number"`) restringindo o valor mínimo a `1` e o máximo a `8192` (ou limite atual do modelo).
- **Input de Mensagem:** Use `MaxInputText` para o campo de envio de mensagem; evite `<input type="text">` nativo.
- **Toggle de Ferramentas:** Use `MaxInputCheckbox` (ou o toggle equivalente do MaxComponentsUi) envelopado dentro de grids de layout responsivos (`MaxGrid` ou `MaxGridCols`). Não use `<input type="checkbox">` nativo.

### 3. Console de Chat em Streaming
- **Estado de Stream Reativo:** Gerencie o histórico do chat como um array reativo de objetos de mensagem contendo `id`, `role` ('user' ou 'assistant'), `content` (texto em streaming) e `tools` (array de ferramentas chamadas).
- **Comportamento de Rolagem Automática (Auto-scroll):** Dispare ações de rolagem para o final (scroll-to-bottom) dentro de um observador `watch` ou quando ocorrerem atualizações. Implemente usando `nextTick`:
  ```typescript
  const chatContainer = ref<HTMLElement | null>(null)
  const scrollToBottom = () => {
    nextTick(() => {
      if (chatContainer.value) {
        chatContainer.value.scrollTop = chatContainer.value.scrollHeight
      }
    })
  }
  ```
- **Integração real de streaming (Vercel AI SDK + Transmit):** O streaming NÃO deve ser simulado com `setInterval` em produção — isso serve apenas para protótipos. Use uma das duas abordagens reais:
  - **Resposta de chat do agente:** consuma o stream do backend (AdonisJS rodando o Vercel AI SDK) com o helper de cliente do Vercel AI SDK (`useChat`/`readUIMessageStream`), acumulando os chunks de texto de forma reativa em `message.content`.
  - **Eventos colaterais em tempo real** (progresso de ferramentas, broadcast multi-usuário): assine via `@adonisjs/transmit-client`:
    ```typescript
    import { Transmit } from '@adonisjs/transmit-client'

    const transmit = new Transmit({ baseUrl: window.location.origin })
    const subscription = transmit.subscription(`playground/${runId}`)
    await subscription.create()
    subscription.onMessage((chunk) => {
      const msg = messages.value.find(m => m.id === chunk.messageId)
      if (msg) { msg.content += chunk.delta; scrollToBottom() }
    })
    ```
  Não use Pusher, Soketi, Reverb ou Laravel Echo.

### 4. Logs de Execução de Ferramentas Colapsáveis
- Renderize as ferramentas invocadas durante a execução do agente em elementos colapsáveis (ex: tags HTML `<details>` ou cards reativos com toggles).
- Agrupe as execuções de ferramentas sob a mensagem do assistente que as disparou.
- Formate as entradas (inputs) e saídas (outputs) das ferramentas com blocos de código para facilitar a leitura. Use ícones (ex: Check/Error do Iconify) para indicar sucesso ou falha.

### 5. Alinhamento Arquitetural
- Estruture cada componente na ordem exata: `<template>`, `<script setup lang="ts">`, `<style scoped lang="scss">`.
- Certifique-se de que todos os atributos sejam mantidos inline dentro dos templates (sem quebras de linha para atributos).
- Escreva todos os comentários do código em Português do Brasil (pt-BR).

## Restrições
- **PROIBIDO Options API:** Não use `data()`, `methods` ou `computed` nos objetos de opções padrão. Use apenas a Composition API.
- **PROIBIDO estilização pura:** Não utilize CSS puro ou estilos inline para barras de rolagem personalizadas ou cards visuais. Em vez disso, use UnoCSS ou estilos SCSS com escopo (`scoped`).
- **PROIBIDO atributos multilinha:** Não formate tags de componentes com quebras de linha nos atributos. Mantenha os atributos na mesma linha da tag de abertura.
- **PROIBIDA Mutação Direta:** Não altere diretamente o estado das stores a partir de componentes; dispare ações (actions) ou mutações definidas nas stores do Pinia.

## Exemplos

### Componente Completo de View do Playground

```vue
<template>
  <div class="agent-playground h-screen flex flex-col bg-slate-900 text-slate-100">
    <div class="header p-4 border-b border-slate-800 flex justify-between items-center">
      <MaxTitle1 h1="Playground de Agentes de IA" h2="Configure prompts e teste interações em tempo real" />
    </div>

    <!-- Layout dividido usando splitpanes -->
    <splitpanes class="default-theme flex-1 overflow-hidden">
      <!-- Painel Esquerdo: Parametrização -->
      <pane size="35" min-size="25" max-size="50" class="pane-sidebar flex flex-col bg-slate-950 p-4 border-r border-slate-800 overflow-y-auto">
        <MaxTitle2 h1="Parâmetros de Execução" />
        
        <MaxGrid class="gap-4 mt-4">
          <!-- Seletor de Agente -->
          <div class="s100">
            <MaxInputSelect v-model="selectedAgentId" label="Selecionar Agente de IA" :options="agentOptions" icon="mdi:robot" />
          </div>

          <!-- Prompt do Sistema -->
          <div class="s100">
            <MaxInputTextArea v-model="systemPrompt" rows="4" label="Instruções do Sistema" placeholder="Ex: Você é um especialista em projetos de energia solar fotovoltaica..." />
          </div>

          <!-- Slider de Temperatura -->
          <div class="s100 flex flex-col gap-1">
            <div class="flex justify-between text-xs text-slate-400 font-semibold uppercase">
              <span>Temperatura</span>
              <span class="text-orange-400">{{ temperature }}</span>
            </div>
            <input v-model.number="temperature" type="range" min="0" max="1" step="0.1" class="w-full accent-orange-500 cursor-pointer h-1.5 bg-slate-800 rounded-lg appearance-none" />
          </div>

          <!-- Input de Max Tokens -->
          <div class="s50">
            <MaxInputText v-model.number="maxTokens" type="number" label="Max Tokens" icon="mdi:counter" />
          </div>

          <!-- Toggle de Ferramentas -->
          <div class="s50 flex items-center justify-start pt-6">
            <MaxInputCheckbox v-model="enableTools" label="Habilitar Tools" />
          </div>
        </MaxGrid>
      </pane>

      <!-- Painel Direito: Chat e Resposta -->
      <pane size="65" class="flex flex-col bg-slate-900 overflow-hidden">
        <!-- Histórico do Chat -->
        <div ref="chatContainer" class="flex-1 p-6 overflow-y-auto flex flex-col gap-4">
          <div v-for="message in messages" :key="message.id" class="message-wrapper flex flex-col" :class="[message.role === 'user' ? 'items-end' : 'items-start']">
            <div class="max-w-85% rounded-lg p-3 text-sm" :class="[message.role === 'user' ? 'bg-orange-600 text-white' : 'bg-slate-800 text-slate-100 border border-slate-700']">
              <!-- Remetente -->
              <div class="text-xs font-semibold uppercase mb-1 opacity-70">
                {{ message.role === 'user' ? 'Desenvolvedor' : 'Agente de IA' }}
              </div>
              <!-- Conteúdo da Mensagem -->
              <div class="whitespace-pre-wrap leading-relaxed">{{ message.content }}</div>
            </div>

            <!-- Logs colapsáveis de ferramentas executadas (apenas para o assistente) -->
            <div v-if="message.role === 'assistant' && message.tools && message.tools.length" class="w-85% mt-2">
              <details class="bg-slate-950 border border-slate-800 rounded text-xs overflow-hidden">
                <summary class="p-2 cursor-pointer select-none font-semibold text-slate-400 flex items-center gap-2 hover:bg-slate-900">
                  <span class="i-mdi-cogs text-orange-400 w-4 h-4" />
                  <span>Ferramentas Executadas ({{ message.tools.length }})</span>
                </summary>
                <div class="p-2 border-t border-slate-900 flex flex-col gap-2 bg-slate-950/50">
                  <div v-for="tool in message.tools" :key="tool.name" class="tool-log border-l-2 border-orange-500 pl-2 py-1">
                    <div class="flex justify-between items-center mb-1">
                      <span class="font-mono text-orange-400 font-bold">{{ tool.name }}</span>
                      <span class="px-1.5 py-0.5 rounded text-10px uppercase font-semibold" :class="[tool.status === 'success' ? 'bg-emerald-950 text-emerald-400' : 'bg-rose-950 text-rose-400']">
                        {{ tool.status }}
                      </span>
                    </div>
                    <pre class="bg-slate-900 p-2 rounded text-10px text-slate-300 overflow-x-auto font-mono">Input: {{ tool.input }}&#10;Output: {{ tool.output }}</pre>
                  </div>
                </div>
              </details>
            </div>
          </div>
        </div>

        <!-- Entrada de Mensagem -->
        <div class="p-4 border-t border-slate-800 bg-slate-950 flex gap-2">
          <MaxInputText v-model="inputText" class="flex-1" placeholder="Digite uma mensagem para o agente..." @keydown.enter.prevent="sendMessage" />
          <MaxButton @click="sendMessage" label="Enviar" icon="mdi:send" severity="primary" />
        </div>
      </pane>
    </splitpanes>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue';
import { splitpanes, pane } from 'splitpanes';
import 'splitpanes/dist/splitpanes.css';
import { usePlaygroundStore } from '@/stores/playground'; // store @maxvue/max-pinia

// Chaves de definição de tipos e estados
interface ToolCall {
  name: string;
  status: 'success' | 'failed';
  input: string;
  output: string;
}

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  tools?: ToolCall[];
}

// Estados reativos do formulário e parâmetros
const selectedAgentId = ref<string>('');
const systemPrompt = ref<string>('');
const temperature = ref<number>(0.7);
const maxTokens = ref<number>(2048);
const enableTools = ref<boolean>(true);
const inputText = ref<string>('');

// Store de configuração do playground (@maxvue/max-pinia): GET cacheado dos agentes
// e auto-save dos parâmetros. Substitui qualquer axios.get/post manual.
const playgroundStore = usePlaygroundStore();
const agentOptions = computed(() => playgroundStore.agentOptions);

// Mensagens do chat
const messages = ref<ChatMessage[]>([]);
const chatContainer = ref<HTMLElement | null>(null);

// Função para rolar o container de chat até o final
const scrollToBottom = () => {
  nextTick(() => {
    if (chatContainer.value) {
      chatContainer.value.scrollTop = chatContainer.value.scrollHeight;
    }
  });
};

// Ação de envio de mensagem
const sendMessage = () => {
  if (!inputText.value.trim()) return;

  const userMsgId = `user-${Date.now()}`;
  messages.value.push({
    id: userMsgId,
    role: 'user',
    content: inputText.value.trim()
  });

  inputText.value = '';
  scrollToBottom();

  // Em produção, dispare a chamada ao backend (AdonisJS + Vercel AI SDK) e
  // consuma o stream real via useChat/readUIMessageStream ou via assinatura
  // @adonisjs/transmit-client. O bloco abaixo é APENAS um stub de protótipo.
  simulateStreamResponse();
};

// STUB DE PROTÓTIPO — não use setInterval em produção.
// Substitua pelo consumo real do stream do Vercel AI SDK / Transmit.
const simulateStreamResponse = () => {
  const assistantMsgId = `assistant-${Date.now()}`;
  const streamMessage: ChatMessage = {
    id: assistantMsgId,
    role: 'assistant',
    content: '',
    tools: [
      {
        name: 'fetch_usina_context',
        status: 'success',
        input: '{"usinaId": "usina-123"}',
        output: '{"nome": "Usina Solar Maxdmin", "potenciaKwp": 120}'
      }
    ]
  };

  messages.value.push(streamMessage);
  scrollToBottom();

  const fullText = 'Olá! Recebi sua mensagem de teste e o agente de IA está respondendo com os parâmetros configurados para análise fotovoltaica.';
  let index = 0;
  
  const interval = setInterval(() => {
    if (index < fullText.length) {
      const msg = messages.value.find(m => m.id === assistantMsgId);
      if (msg) {
        msg.content += fullText[index];
        scrollToBottom();
      }
      index++;
    } else {
      clearInterval(interval);
    }
  }, 30);
};
</script>

<style scoped lang="scss">
.agent-playground {
  /* Estilização customizada da barra de rolagem usando SCSS e variáveis do sistema */
  ::-webkit-scrollbar {
    width: 6px;
  }
  ::-webkit-scrollbar-track {
    background: transparent;
  }
  ::-webkit-scrollbar-thumb {
    background: var(--slate-800, #1e293b);
    border-radius: 4px;
    &:hover {
      background: var(--orange-500, #f97316);
    }
  }
}
</style>
```
