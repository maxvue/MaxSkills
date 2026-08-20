---
name: adonisjs-outbound-http-ssrf-defense-best-practices
description: Use when implementing, reviewing, or debugging outbound HTTP requests, external API integrations, RSS/news fetching, or media downloads from user-provided URLs in AdonisJS. Triggers on Got/Axios/undici configurations, custom DNS resolution, private IP range validation (RFC 1918), SSRF prevention, and download resource limiting.
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Defesa contra SSRF em Requisições HTTP de Saída no AdonisJS

## Objetivo
Estabelecer diretrizes seguras e padronizadas para realizar requisições HTTP de saída (outbound) em aplicações backend AdonisJS, eliminando riscos de vulnerabilidades como Server-Side Request Forgery (SSRF), DNS Rebinding e esgotamento de recursos.

> **Veja também:** para os padrões gerais de integração com APIs externas (camada de serviço, timeouts com `AbortSignal`, tratamento de resposta), consulte `adonisjs-api-integration-patterns`. Esta skill foca especificamente na defesa contra SSRF em URLs de destino não confiáveis.

## Instruções

### 1. Validação de Endereço IP Privado
Antes de resolver o DNS ou conectar, certifique-se de que os endereços IP resolvidos não apontam para redes locais ou privadas. Use esta função utilitária para identificar faixas de IP reservadas e privadas.

```typescript
import { isIP } from 'node:net'

/**
 * Valida se um endereço IP pertence a faixas privadas, loopback ou reservadas.
 * Retorna true se o IP for privado/inseguro, false caso contrário.
 */
export function isPrivateIp(ip: string): boolean {
  const type = isIP(ip)
  if (type === 0) return true // IP inválido é tratado como inseguro por padrão

  if (type === 4) {
    const parts = ip.split('.').map(Number)
    const [o1, o2] = parts

    // RFC 1918 (10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
    if (o1 === 10) return true
    if (o1 === 172 && o2 >= 16 && o2 <= 31) return true
    if (o1 === 192 && o2 === 168) return true

    // Loopback (127.0.0.0/8)
    if (o1 === 127) return true

    // Link-Local (169.254.0.0/16)
    if (o1 === 169 && o2 === 254) return true

    // Rede atual / Broadcast / Outras faixas reservadas
    if (o1 === 0) return true
    if (o1 === 100 && o2 >= 64 && o2 <= 127) return true // RFC 6598 (Shared Address Space)
    if (o1 === 192 && o2 === 0) return true // Atribuições de protocolo IETF
    if (o1 === 198 && (o2 === 18 || o2 === 19)) return true // RFC 2544 (Testes de benchmark)
    if (o1 >= 224) return true // Multicast e faixas reservadas (classe E)
  } else if (type === 6) {
    const cleanIp = ip.toLowerCase().trim()
    
    // Loopback (::1) e Não Especificado (::)
    if (cleanIp === '::1' || cleanIp === '::') return true

    // Unicast Link-Local (fe80::/10)
    if (cleanIp.startsWith('fe80:')) return true

    // Unique Local Address (fc00::/7)
    if (cleanIp.startsWith('fc') || cleanIp.startsWith('fd')) return true

    // Multicast (ff00::/8)
    if (cleanIp.startsWith('ff')) return true

    // IPv4-mapeado em IPv6 (::ffff:a.b.c.d) — bypass crítico de SSRF:
    // node:net.isIP('::ffff:169.254.169.254') retorna 6, mas o prefixo não casa
    // com nenhuma das verificações acima. Detectar e re-validar a parte IPv4.
    const ipv4MappedMatch = cleanIp.match(/^::ffff:(\d+\.\d+\.\d+\.\d+)$/)
    if (ipv4MappedMatch) return isPrivateIp(ipv4MappedMatch[1])

    // Também bloquear formas numéricas ::ffff:hex (ex: ::ffff:7f00:1 = 127.0.0.1)
    if (cleanIp.startsWith('::ffff:')) return true
  }

  return false
}
```

### 2. Mitigação de DNS Rebinding
Um padrão simples de verificar e depois requisitar (check-then-request) é vulnerável a DNS Rebinding (TOCTOU). Para mitigar isso, intercepte e valide o endereço IP no nível do estabelecimento da conexão TCP usando um DNS Resolver/Agent customizado.

#### Opção A: Usando Axios com Agentes Seguros
Configure agentes customizados com uma função lookup modificada:

```typescript
import http from 'node:http'
import https from 'node:https'
import dns from 'node:dns'
import axios from 'axios'
import { isPrivateIp } from './ip_validator.js' // Ajustar caminho conforme a estrutura do projeto

const safeLookup: http.AgentOptions['lookup'] = (hostname, options, callback) => {
  // Força `all: true` para que dns.lookup SEMPRE retorne um array de endereços.
  // Sem isso, `address` é uma string única e múltiplos IPs (round-robin) não seriam validados.
  dns.lookup(hostname, { ...options, all: true }, (err, addresses) => {
    if (err) return callback(err, '', 0)

    for (const addr of addresses) {
      if (isPrivateIp(addr.address)) {
        return callback(new Error(`Acesso ao IP privado ${addr.address} é proibido.`), '', 0)
      }
    }

    // Retorna o primeiro endereço seguro resolvido.
    const [first] = addresses
    return callback(null, first.address, first.family)
  })
}

// Criação de agents HTTP/HTTPS seguros com lookup personalizado
const httpAgent = new http.Agent({ lookup: safeLookup, keepAlive: false })
const httpsAgent = new https.Agent({ lookup: safeLookup, keepAlive: false })

export const safeAxios = axios.create({
  httpAgent,
  httpsAgent,
  timeout: 5000, // Timeout de conexão rígido (5 segundos)
  maxRedirects: 3, // Limita redirecionamentos para evitar SSRF indireto ou loops
})
```

#### Opção B: Usando fetch Nativo (Undici)
No Node.js 18+, o `fetch` nativo roda sobre a biblioteca `undici`. Configure um agente despachante customizado.

> **Requisito:** o pacote standalone `undici` (que exporta a classe `Agent`) **não é dependência declarada do projeto** — só `undici-types` (bundled com `@types/node`) está presente. Sem instalar `undici`, o `import { Agent } from 'undici'` lança `ERR_MODULE_NOT_FOUND`. Rode `npm i undici` antes de usar a Opção B, **ou** use a Opção A (axios), que já é dependência do projeto.

```typescript
import { Agent } from 'undici' // requer: npm i undici
import dns from 'node:dns'
import { isPrivateIp } from './ip_validator.js'

const safeAgent = new Agent({
  connect: {
    lookup: (hostname, options, callback) => {
      // `all: true` garante array de endereços e validação de TODOS os IPs resolvidos.
      dns.lookup(hostname, { ...options, all: true }, (err, addresses) => {
        if (err) return callback(err, '', 0)

        for (const addr of addresses) {
          if (isPrivateIp(addr.address)) {
            return callback(new Error(`Acesso ao IP privado ${addr.address} é proibido.`), '', 0)
          }
        }
        const [first] = addresses
        return callback(null, first.address, first.family)
      })
    }
  }
})

/**
 * Wrapper seguro para chamadas de fetch nativo do Node.js.
 */
export async function safeFetch(url: string, options: RequestInit = {}): Promise<Response> {
  return fetch(url, {
    ...options,
    dispatcher: safeAgent,
    signal: options.signal || AbortSignal.timeout(5000) // Timeout de requisição padrão de 5s
  })
}
```

### 3. Validação de Tamanho do Payload e Streams da Resposta
Previna ataques de Negação de Serviço (DoS) causados pelo carregamento de payloads excessivamente grandes (como Zip Bombs ou fontes de stream infinito) na memória.

```typescript
import { safeFetch } from './safe_fetch.js'

/**
 * Realiza download de arquivos limitando o tamanho da resposta recebida.
 */
export async function downloadFileSecurely(url: string, maxSize = 10 * 1024 * 1024) { // Padrão: 10MB
  const response = await safeFetch(url)
  
  // Validação prévia pelo cabeçalho Content-Length
  const contentLength = response.headers.get('content-length')
  if (contentLength && Number.parseInt(contentLength, 10) > maxSize) {
    throw new Error('O arquivo excede o tamanho máximo permitido.')
  }

  const reader = response.body?.getReader()
  if (!reader) throw new Error('O corpo da resposta está vazio.')

  let receivedBytes = 0
  const chunks: Uint8Array[] = []

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    receivedBytes += value.length
    if (receivedBytes > maxSize) {
      // Cancela a leitura da stream imediatamente para liberar os recursos do socket
      await reader.cancel('Tamanho do arquivo excedeu o limite.')
      throw new Error('O tamanho de download permitido foi excedido.')
    }
    chunks.push(value)
  }

  // Retorna os dados concatenados de forma segura
  return Buffer.concat(chunks.map(chunk => Buffer.from(chunk)))
}
```

### 4. Logging Seguro
Nunca registre URLs brutas que possam conter parâmetros de consulta (como tokens de autenticação ou assinaturas) ou cabeçalhos de autorização diretamente. Limpe os metadados da URL antes de passá-los ao Logger do AdonisJS.

```typescript
import logger from '@adonisjs/core/services/logger'

/**
 * Registra a requisição outbound sem vazar credenciais ou query parameters sensíveis.
 */
export function logOutboundRequest(url: string, method = 'GET') {
  try {
    const parsedUrl = new URL(url)
    // Remove query params e credenciais básicas para expurgar dados sensíveis nos logs
    parsedUrl.search = ''
    parsedUrl.password = ''
    parsedUrl.username = ''
    
    logger.info({ url: parsedUrl.toString(), method }, 'Requisição HTTP de saída iniciada')
  } catch {
    logger.warn({ method }, 'Requisição HTTP de saída iniciada com URL inválida')
  }
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NUNCA execute requisições HTTP de saída sem usar agentes de conexão que restrinjam a resolução. O uso do `fetch` comum ou `axios.get(url)` padrão é estritamente proibido quando a URL de destino é fornecida pelo usuário.
* NÃO ignore limites de tamanho de resposta. Uma URL pode apontar para um fluxo de dados de comprimento infinito, esgotando a memória ou o espaço em disco do servidor.
* NÃO registre cabeçalhos de autorização ou a URL original contendo parâmetros de consulta diretamente em logs.
* NÃO permita mais de 3 redirecionamentos em requisições inseguras, a fim de evitar que redirecionamentos burlem a verificação inicial do domínio.
