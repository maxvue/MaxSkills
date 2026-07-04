---
name: adonisjs-vite-local-https-ssl-best-practices
description: Use when configuring, reviewing, or debugging local HTTPS development environments, setting up Vite 8 HMR (Hot Module Replacement) over SSL, managing SSL/TLS keys and certificates, or routing local subdomains and custom hosts (e.g., dev.maxdmin.com.br) in AdonisJS and Vite 8.
---

# Melhores Práticas para HTTPS/SSL Local no AdonisJS e Vite

## Objetivo
Estabelecer um ambiente de desenvolvimento local seguro e sem fricção utilizando HTTPS/SSL para AdonisJS v6 e Vite, garantindo que o Hot Module Replacement (HMR) funcione perfeitamente sobre WebSockets seguros (`wss://`) e domínios locais customizados (ex: `dev.maxdmin.com.br`).

## Instruções

### 1. Geração de Certificados SSL Locais com mkcert
Utilize a ferramenta `mkcert` para criar certificados localmente confiáveis:
1. Instale o `mkcert` e execute `mkcert -install` para adicionar a CA local ao repositório de chaves confiáveis do seu sistema.
2. Gere os certificados para seus domínios locais (ex: `localhost` e domínios personalizados):
   ```bash
   mkcert -key-file certificates/key.pem -cert-file certificates/cert.pem localhost dev.maxdmin.com.br "*.maxdmin.com.br"
   ```
3. Adicione o diretório gerado (`certificates/`) ao arquivo `.gitignore`.

### 2. Mapeamento de Domínio Personalizado
Mapeie seu domínio personalizado para o localhost no arquivo de hosts do sistema (ex: `/etc/hosts` no Linux/macOS ou `C:\Windows\System32\drivers\etc\hosts` no Windows):
```hosts
127.0.0.1   dev.maxdmin.com.br
127.0.0.1   tenant1.dev.maxdmin.com.br
```

### 3. Configuração do Vite (`vite.config.ts`)
Configure o Vite para ler os certificados SSL locais e habilitar o HMR seguro:
```typescript
import { defineConfig } from 'vite'
import adonisjs from '@adonisjs/vite/client'
import fs from 'node:fs'
import path from 'node:path'

const isHttps = fs.existsSync(path.resolve(__dirname, 'certificates/key.pem'))

export default defineConfig({
  server: {
    host: 'dev.maxdmin.com.br', // Ou 'localhost'
    port: 5173,
    https: isHttps ? {
      key: fs.readFileSync(path.resolve(__dirname, 'certificates/key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname, 'certificates/cert.pem')),
    } : false,
    hmr: {
      host: 'dev.maxdmin.com.br',
      protocol: isHttps ? 'wss' : 'ws',
    },
    cors: true,
    allowedHosts: [
      'dev.maxdmin.com.br',
      '.dev.maxdmin.com.br' // Permite subdomínios de inquilinos (tenants)
    ]
  },
  plugins: [
    adonisjs({
      // Mantenha o mesmo entrypoint usado pela configuração principal do Vite do projeto
      // (SPA Vue + Vue Router): 'resources/app.ts'
      entrypoints: ['resources/app.ts'],
      // 'reload' recebe globs de arquivos do backend (Edge/rotas) que devem
      // disparar full-reload. Numa SPA Vue pura isso normalmente não é necessário.
      reload: [],
    }),
  ],
})
```

### 4. Configuração do Servidor HTTPS no AdonisJS
Para rodar também o servidor AdonisJS sob HTTPS:
1. Certifique-se de que o seu arquivo `.env` contenha os caminhos das chaves:
   ```env
   PORT=3333
   HOST=dev.maxdmin.com.br
   NODE_ENV=development
   
   # Configuração SSL
   SSL_KEY_PATH=./certificates/key.pem
   SSL_CERT_PATH=./certificates/cert.pem
   ```
2. Atualize o arquivo `bin/server.ts` para iniciar o servidor com HTTPS caso os certificados existam. O Ignitor do AdonisJS v6 expõe um mecanismo de primeira classe: `.httpServer().start(serverCallback)` aceita um callback que recebe o `handler` e retorna o servidor Node — basta devolver um `https.createServer(options, handler)`:
   ```typescript
   import 'reflect-metadata'
   import { Ignitor, prettyPrintError } from '@adonisjs/core'
   import fs from 'node:fs'
   import https from 'node:https'
   import path from 'node:path'

   const APP_ROOT = new URL('../', import.meta.url)
   const IMPORTER = (filePath: string) => {
     if (filePath.startsWith('./') || filePath.startsWith('../')) {
       return import(new URL(filePath, APP_ROOT).href)
     }
     return import(filePath)
   }

   const keyPath = process.env.SSL_KEY_PATH
   const certPath = process.env.SSL_CERT_PATH

   const options = keyPath && certPath && fs.existsSync(path.resolve(keyPath))
     ? {
         key: fs.readFileSync(path.resolve(keyPath)),
         cert: fs.readFileSync(path.resolve(certPath)),
       }
     : undefined

   new Ignitor(APP_ROOT, { importer: IMPORTER })
     .tap((app) => {
       app.booting(async () => {
         await import('#start/env')
       })
       app.listen('SIGTERM', () => app.terminate())
       app.listenIf(app.managedByPm2, 'SIGINT', () => app.terminate())
     })
     .httpServer()
     // Com certificados, embrulhe o handler do Adonis num servidor HTTPS;
     // sem eles, passe `undefined` e o Adonis cria o servidor HTTP padrão.
     .start(options ? (handler) => https.createServer(options, handler) : undefined)
     .catch((error) => {
       process.exitCode = 1
       prettyPrintError(error)
     })
   ```
   *Nota: TLS in-process **não** precisa de hook frágil — o callback do `.httpServer().start()` é o mecanismo documentado. Alternativamente (produção-like), você pode **terminar o HTTPS num proxy reverso** (Caddy ou nginx) à frente do AdonisJS rodando em HTTP puro; o Caddy reutiliza a CA do `mkcert` automaticamente. Não existe uma propriedade `config/app.ts -> http.serverOptions` para injetar certificados; `config/app.ts -> http` refere-se a parsing/cookies/trustProxy, não às opções de TLS do servidor Node.*

### 5. Tratamento de Requisições Internas Servidor-a-Servidor (Rejeição de TLS)
Se o backend AdonisJS realiza requisições de backend-para-backend para si mesmo ou para outros serviços seguros locais e falha com `DEPTH_ZERO_SELF_SIGNED_CERT`, permita TLS não autorizado *estritamente* no ambiente de desenvolvimento:
```typescript
if (process.env.NODE_ENV === 'development') {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'
}
```

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NUNCA** envie chaves privadas (`*.key`, `key.pem`) ou certificados (`*.crt`, `cert.pem`) para o repositório de controle de versão.
- **NUNCA** utilize `process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'` em código de produção. Certifique-se de envolver essa instrução em uma validação estrita de ambiente de desenvolvimento.
- Não utilize caminhos absolutos fixos (hardcoded) para os certificados SSL; leia-os das variáveis de ambiente ou de caminhos relativos à raiz do projeto com verificações de existência (`fs.existsSync`).
- Não misture conteúdo HTTP e HTTPS (Mixed Content); se o servidor principal rodar sob `https://`, o HMR do Vite DEVE utilizar `wss://` e o servidor do Vite DEVE rodar sob `https://`.
