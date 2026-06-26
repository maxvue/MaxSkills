# Exemplo: Testando Saídas Estruturadas e Schemas Zod

Este exemplo demonstra como escrever um teste para verificar se um agente de IA retorna uma estrutura de dados JSON em conformidade com um schema Zod no AdonisJS v6, utilizando o `MockLanguageModelV3`.

## Arquivo de Teste Unitário

Crie o arquivo `tests/unit/ai_agent_structured.spec.ts`:

```typescript
import { test } from '@japa/runner'
import { MockLanguageModelV3 } from 'ai/test'
import { executeAgent } from '#ai/agent_ai_request'
import { z } from 'zod'

// Definir o schema esperado do agente de IA
const postCopySchema = z.object({
  title: z.string(),
  body: z.string(),
  hashtags: z.array(z.string()),
})

test.group('Agentes de IA | Teste Unitário de Saída Estruturada', () => {
  test('deve retornar conteúdo estruturado compatível com o schema Zod', async ({ assert }) => {
    const expectedOutput = {
      title: 'Eficiência da Energia Solar',
      body: 'Os painéis solares estão mais eficientes do que nunca. Mude para energia limpa hoje!',
      hashtags: ['energiasolar', 'sustentabilidade', 'energialimpa'],
    }

    // 1. Criar o modelo mockado retornando a string JSON esperada pelo schema
    const mockModel = new MockLanguageModelV3({
      doGenerate: async () => {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(expectedOutput),
            },
          ],
          finishReason: 'stop',
          usage: {
            promptTokens: 20,
            completionTokens: 35,
          },
          rawCall: { rawPrompt: null, rawSettings: {} },
        }
      },
    })

    // 2. Executar o agente passando o modelo mockado customModel
    const result = await executeAgent({
      agentName: 'structured-copywriter-test',
      systemPrompt: 'You output JSON matching the required schema.',
      prompt: 'Generate copy structure for solar energy.',
      tools: {},
      isDone: async () => true,
      customModel: mockModel, // Injetando o mock
    })

    // 3. Validar a saída utilizando o Zod
    assert.isFalse(result.errored)
    
    const parseResult = postCopySchema.safeParse(JSON.parse(result.lastText))
    
    assert.isTrue(parseResult.success)
    if (parseResult.success) {
      assert.equal(parseResult.data.title, 'Eficiência da Energia Solar')
      assert.include(parseResult.data.hashtags, 'sustentabilidade')
    }
  })
})
```
