# Exemplo: Mockando a Geração de Texto do Gemini no AdonisJS v6

Este exemplo demonstra como escrever um teste unitário para um agente de IA no AdonisJS v6 utilizando o Japa e a classe `MockLanguageModelV3` do Vercel AI SDK.

## Arquivo de Teste Unitário

Crie o arquivo `tests/unit/ai_agent_mock.spec.ts`:

```typescript
import { test } from '@japa/runner'
import { MockLanguageModelV3 } from 'ai/test'
import { executeAgent } from '#ai/agent_ai_request'

test.group('Agentes de IA | Teste Unitário do Copywriter', () => {
  test('deve gerar uma copy de marketing com sucesso usando Gemini mockado', async ({ assert }) => {
    // 1. Criar o modelo de linguagem simulado (mock)
    const mockModel = new MockLanguageModelV3({
      defaultObjectGenerationMode: 'json',
      doGenerate: async (options) => {
        // Garantir que o prompt do sistema e o prompt do usuário foram enviados corretamente
        assert.include(options.system || '', 'You are a professional copywriter')
        assert.include(options.prompt[0].text || '', 'Write a post about Solar Energy')

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
            promptTokens: 15,
            completionTokens: 12,
          },
          rawCall: { rawPrompt: null, rawSettings: {} },
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
