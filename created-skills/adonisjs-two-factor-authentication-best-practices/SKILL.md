---
name: adonisjs-two-factor-authentication-best-practices
description: Use when implementing, configuring, reviewing, or securing Two-Factor Authentication (2FA) or Multi-Factor Authentication (MFA) in AdonisJS v6, using TOTP (Time-based One-time Password) libraries, generating QR codes, handling backup recovery codes, or implementing frontend challenge screens in Vue 3. Triggers on 2FA setup, token verification middleware, and backup code generation.
---

## Objetivo
Estabelecer padrões seguros, robustos e consistentes para a implementação de Autenticação de Dois Fatores (2FA) baseada em TOTP no backend AdonisJS v6 e no frontend Vue 3 dentro do ecossistema EngeApp.

## Instruções

### 1. Configuração do Schema do Banco de Dados e Model Lucid
* Adicione as seguintes colunas à tabela `users`:
  - `two_factor_secret`: string de texto criptografado (pode ser nulo).
  - `two_factor_recovery_codes`: JSON ou string de texto criptografado contendo códigos de recuperação (pode ser nulo).
  - `two_factor_enabled`: booleano (padrão `false`).
* No model Lucid `User` (`app/models/user.ts`):
  - Decore as propriedades utilizando `@column()`.
  - Para campos sensíveis como `twoFactorSecret` e `twoFactorRecoveryCodes`, configure-os para serializar como nulo usando `@column({ serializeAs: null })` para evitar exposição acidental em retornos de APIs.
  - Exponha métodos utilitários no model para verificar se o 2FA está ativo.

### 2. Lógica de TOTP no Backend (AdonisJS v6)
* Use a biblioteca `otplib` para geração de segredos TOTP e validação de tokens.
* Use `qrcode` para gerar uma URI de QR code segura no formato de data URL.
* **Armazenamento de Segredos:** Criptografe a chave secreta antes de salvá-la no banco usando o serviço de criptografia oficial do AdonisJS (`encryption`).
* **Códigos de Recuperação:**
  - Gere uma lista de códigos únicos de backup (ex: strings alfanuméricas de 8 a 10 caracteres).
  - Faça o hash dos códigos de recuperação (usando `@adonisjs/core/services/hash`) ou criptografe-os antes do armazenamento.
  - Implemente um método para verificar e marcar um código de recuperação como utilizado (uso único).
* **Rotas e Controllers:**
  - `POST /api/auth/2fa/setup`: Gera o segredo e a URI do QR code. Não habilita o 2FA até a validação.
  - `POST /api/auth/2fa/enable`: Valida o primeiro token TOTP para ativar formalmente o 2FA e retorna os códigos de recuperação de backup.
  - `POST /api/auth/2fa/disable`: Desativa o 2FA (exige confirmação da senha atual).
  - `POST /api/auth/2fa/verify`: Valida um token TOTP durante o fluxo de login.

### 3. Sessão e Middleware (AdonisJS v6)
* Implemente um middleware nomeado `TwoFactorAuthMiddleware` (ex: em `app/middleware/two_factor_auth_middleware.ts`):
  - Verifique se o usuário autenticado possui `twoFactorEnabled` habilitado.
  - Se sim, verifique se a sessão possui a flag de desafio respondido (ex: `session.get('auth_2fa_verified') === true`).
  - Se a flag não existir, aborte a requisição com o status `403 Forbidden` ou um payload indicando `{ status: '2fa_challenge_required' }`.
* Registre este middleware em `start/kernel.ts`.

### 4. Tela de Desafio e Navegação no Frontend Vue 3
* **Store `@maxvue/max-pinia` (`authStore.ts` / `useAuthStore`):**
  - Use uma store `@maxvue/max-pinia` (não um Pinia genérico) para o estado de autenticação.
  - Mantenha um estado indicando se o usuário está autenticado mas pendente de resolver o desafio de 2FA (ex: `is2faPending`).
  - Toda chamada ao backend (login, setup, enable, disable, verify) deve passar pela store, resolvendo o caminho string com `apiPostRoute('/api/auth/2fa/verify')` (etc.) do `@maxvue/max-use` — nunca `axios`/`fetch` manual nem rotas nomeadas estilo Ziggy.
  - Ao receber a resposta `2fa_challenge_required` do login ou middleware, defina `is2faPending` como `true`.
* **Vue Router:**
  - No guarda de navegação global (`router.beforeEach`), verifique se a rota requer autenticação.
  - Se `is2faPending` for `true`, redirecione o usuário para `/login/2fa` e restrinja o acesso a qualquer outra rota protegida.
* **Design do Componente SFC (Composition API):**
  - Use estritamente Composition API (`<script setup lang="ts">`). Estilize via UnoCSS attributify (presetMaxUno + presets de attributify) e tokens de tema — sem blocos `<style>`/`lang="scss"` e sem classes Tailwind cruas.
  - A tela de desafio 2FA (`/login/2fa`) é uma tela de autenticação — reutilize **`<MaxAuthCard>`** (o mesmo componente da tela de login, ver `vue-auth-session-state-best-practices`) para manter consistência visual com o fluxo de login Maxdmin. O input do código TOTP entra no slot do card; demais campos via `<MaxInputText>`/`<MaxButton>` do `MaxComponentsUi`.
  - Formate o template do componente mantendo todos os atributos/parâmetros na mesma linha (estilo inline), sem quebra de atributos em várias linhas.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
* NÃO armazene os segredos TOTP em texto plano. Sempre criptografe-os usando o serviço `encryption` do AdonisJS.
* NÃO exponha `two_factor_secret` ou `two_factor_recovery_codes` na serialização padrão do model.
* NÃO permita que rotas que exigem autenticação ignorem a verificação de 2FA se habilitado.
* NÃO utilize a Options API nos componentes Vue 3; use apenas Composition API com `<script setup>`.
* NÃO quebre linhas de atributos dentro de elementos do `<template>`. Todos os atributos/parâmetros devem permanecer na mesma linha.
