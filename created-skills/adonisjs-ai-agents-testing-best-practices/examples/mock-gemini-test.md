# Exemplo: Mockando a Geração de Texto do Gemini no AdonisJS v6

Este exemplo demonstra como escrever um teste unitário para um agente de IA no AdonisJS v6 utilizando o Japa e a classe `MockLanguageModelV4` do Vercel AI SDK.

## Arquivo de Teste Unitário

Crie o arquivo `tests/unit/ai_agent_mock.spec.ts`:

```typescript
import { test } from '@japa/runner'
import { MockLanguageModelV4 } from 'ai/test'
import { executeAgent } from '#ai/agent_ai_request'

test.group('Agentes de IA | Teste Unitário do Copywriter', () => {
  test('deve gerar uma copy de marketing com sucesso usando Gemini mockado', async ({ assert }) => {
    // 1. Criar o modelo de linguagem simulado (mock)
    const mockModel = new MockLanguageModelV4({
      doGenerate: async (options) => {
        // Garantir que o prompt do sistema e o prompt do usuário foram enviados corretamente
        // O system prompt é uma mensagem com role 'system' dentro de options.prompt
        const systemMessage = options.prompt.find((message) => message.role === 'system')
        assert.include((systemMessage?.content as string) || '', 'You are a professional copywriter')

        // O prompt do usuário é uma mensagem com role 'user' cujo texto vive nas partes de conteúdo
        const userMessage = options.prompt.find((message) => message.role === 'user')
        const userText = Array.isArray(userMessage?.content)
          ? userMessage!.content.map((part) => ('text' in part ? part.text : '')).join('')
          : ''
        assert.include(userText, 'Write a post about Solar Energy')

        // Retornar uma resposta determinística
        return {
          content: [
            {
              type: 'text',
              text: 'Descubra o poder da Energia Solar! Economize dinheiro e salve o planeta.',
            },
          ],
          finishReason: 'stop',
          usage: {
            inputTokens: { total: 15 },
            outputTokens: { total: 12 },
          },
          warnings: [],
        }
      },
    })

    // 2. Executar o agente passando o customModel
    const result = await executeAgent({
      agentName: 'instagram-copywriter-test',
      systemPrompt: 'You are a professional copywriter.',
      prompt: 'Write a post about Solar Energy.',
      tools: {},
      isDone: async () => true,
      customModel: mockModel, // Injetando o mock do modelo
    })

    // 3. Executar as asserções de teste
    assert.isFalse(result.errored)
    assert.equal(result.agent, 'instagram-copywriter-test')
    assert.equal(result.lastText, 'Descubra o poder da Energia Solar! Economize dinheiro e salve o planeta.')
    assert.equal(result.totalTokens, 27) // 15 input + 12 output
  })
})
```
