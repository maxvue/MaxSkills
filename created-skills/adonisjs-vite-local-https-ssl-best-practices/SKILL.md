---
name: adonisjs-vite-local-https-ssl-best-practices
description: Use when configuring, reviewing, or debugging local HTTPS development environments, setting up Vite 8 HMR (Hot Module Replacement) over SSL, managing SSL/TLS keys and certificates, or routing local subdomains and custom hosts (e.g., dev.maxdmin.local) in AdonisJS and Vite 8.
---

# Melhores Práticas para HTTPS/SSL Local no AdonisJS e Vite

## Objetivo
Estabelecer um ambiente de desenvolvimento local seguro e sem fricção utilizando HTTPS/SSL para AdonisJS v6 e Vite, garantindo que o Hot Module Replacement (HMR) funcione perfeitamente sobre WebSockets seguros (`wss://`) e domínios locais customizados (ex: `dev.maxdmin.local`).

## Instruções

### 1. Geração de Certificados SSL Locais com mkcert
Utilize a ferramenta `mkcert` para criar certificados localmente confiáveis:
1. Instale o `mkcert` e execute `mkcert -install` para adicionar a CA local ao repositório de chaves confiáveis do seu sistema.
2. Gere os certificados para seus domínios locais (ex: `localhost` e domínios personalizados):
   ```bash
   mkcert -key-file certificates/key.pem -cert-file certificates/cert.pem localhost dev.maxdmin.local "*.maxdmin.local"
   ```
3. Adicione o diretório gerado (`certificates/`) ao arquivo `.gitignore`.

### 2. Mapeamento de Domínio Personalizado
Mapeie seu domínio personalizado para o localhost no arquivo de hosts do sistema (ex: `/etc/hosts` no Linux/macOS ou `C:\Windows\System32\drivers\etc\hosts` no Windows):
```hosts
127.0.0.1   dev.maxdmin.local
127.0.0.1   tenant1.dev.maxdmin.local
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
    host: 'dev.maxdmin.local', // Ou 'localhost'
    port: 5173,
    https: isHttps ? {
      key: fs.readFileSync(path.resolve(__dirname, 'certificates/key.pem')),
      cert: fs.readFileSync(path.resolve(__dirname, 'certificates/cert.pem')),
    } : false,
    hmr: {
      host: 'dev.maxdmin.local',
      protocol: isHttps ? 'wss' : 'ws',
    },
    cors: true,
    allowedHosts: [
      'dev.maxdmin.local',
      '.dev.maxdmin.local' // Permite subdomínios de inquilinos (tenants)
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
   HOST=dev.maxdmin.local
   NODE_ENV=development
   
   # Configuração SSL
   SSL_KEY_PATH=./certificates/key.pem
   SSL_CERT_PATH=./certificates/cert.pem
   ```
2. Atualize o arquivo `bin/server.ts` para iniciar o servidor com HTTPS caso os certificados existam:
   ```typescript
   import fs from 'node:fs'
   import path from 'node:path'
   import env from '#start/env'

   const keyPath = env.get('SSL_KEY_PATH')
   const certPath = env.get('SSL_CERT_PATH')

   const options = keyPath && certPath && fs.existsSync(keyPath)
     ? {
         key: fs.readFileSync(path.resolve(keyPath)),
         cert: fs.readFileSync(path.resolve(certPath)),
       }
     : undefined

   // Inicialize o servidor HTTP do AdonisJS com as opções de SSL
   // (No AdonisJS v6, isso é feito interceptando a criação do servidor Node
   // via Ignitor/hook no bin/server.ts — ver nota abaixo)
   ```
   *Nota (abordagem recomendada): A forma mais simples e robusta de TLS local é **terminar o HTTPS num proxy reverso** (Caddy ou nginx) à frente do AdonisJS, deixando o Adonis rodar em HTTP puro na porta interna. O Caddy usa a mesma CA do `mkcert` automaticamente. Só termine TLS dentro do próprio processo Node (passando `key`/`cert` ao `http.createServer` via hook no `bin/server.ts`) se realmente precisar. Não existe uma propriedade `config/app.ts -> http.serverOptions` para injetar certificados em Adonis v6; configurações em `config/app.ts -> http` referem-se a parsing/cookies/trustProxy, não às opções de TLS do servidor Node.*

### 5. Tratamento de Requisições Internas Servidor-a-Servidor (Rejeição de TLS)
Se o backend AdonisJS realiza requisições de backend-para-backend para si mesmo ou para outros serviços seguros locais e falha com `DEPTH_ZERO_SELF_SIGNED_CERT`, permita TLS não autorizado *estritamente* no ambiente de desenvolvimento:
```typescript
if (process.env.NODE_ENV === 'development') {
  process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'
}
```

## Restrições
- **NUNCA** envie chaves privadas (`*.key`, `key.pem`) ou certificados (`*.crt`, `cert.pem`) para o repositório de controle de versão.
- **NUNCA** utilize `process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0'` em código de produção. Certifique-se de envolver essa instrução em uma validação estrita de ambiente de desenvolvimento.
- Não utilize caminhos absolutos fixos (hardcoded) para os certificados SSL; leia-os das variáveis de ambiente ou de caminhos relativos à raiz do projeto com verificações de existência (`fs.existsSync`).
- Não misture conteúdo HTTP e HTTPS (Mixed Content); se o servidor principal rodar sob `https://`, o HMR do Vite DEVE utilizar `wss://` e o servidor do Vite DEVE rodar sob `https://`.
