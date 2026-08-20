---
name: adonisjs-docker-development-environment-best-practices
description: Use when creating, modifying, configuring, or debugging Docker containers, Dockerfiles, or docker-compose configurations for AdonisJS applications. Triggers on files like Dockerfile, docker-compose.yml, container setups, or requests to configure development environments with PostgreSQL, Redis, and Meilisearch.
author: Johnattas Conrady Gomes Santana
---
# Boas Práticas de Ambiente de Desenvolvimento Docker para AdonisJS

## Objetivo
Estabelecer um ambiente de desenvolvimento local estruturado e otimizado para aplicações AdonisJS v6 usando Docker e Docker Compose, integrando PostgreSQL, Redis e Meilisearch.

## Instruções

1. **Dockerizando a Aplicação (Dockerfile.dev):**
   - Use uma imagem Node.js LTS leve. Prefira `node:22-alpine` (Node 22 LTS): o Vite 8 exige Node 20.19+/22+, então `node:20-alpine` pode ser insuficiente para a versão alvo.
   - Copie os arquivos de dependência (`package.json`, `package-lock.json`) e execute `npm install` primeiro para aproveitar o cache de camadas.
   - NÃO instale apenas dependências de produção; compilação e monitoramento (hot-reload) exigem devDependencies (como `@adonisjs/assembler`).
   - Use o modelo dedicado para desenvolvimento local: [Dockerfile.dev](resources/Dockerfile.dev).

2. **Orquestrando Serviços (docker-compose.yml):**
   - Crie uma arquitetura multi-container contendo o App, PostgreSQL, Redis e Meilisearch.
   - Injete variáveis de ambiente no container do App para mapear os hosts de banco de dados e cache para os nomes de serviço dos containers correspondentes (`postgres`, `redis`, `meilisearch`).
   - Previna falhas na inicialização do app utilizando declarações de `healthcheck` nos serviços de banco de dados e Redis, garantindo que estejam prontos antes do container do App iniciar.
   - Evite conflitos no sistema host permitindo que os mapeamentos de porta sejam sobrescritos através de variáveis de ambiente no arquivo `.env` (ex: `DB_PORT`, `REDIS_PORT`).
   - Use o template padrão de docker-compose: [docker-compose.yml](resources/docker-compose.yml).

3. **Gerenciando Volumes e Hot-Reload:**
   - Monte o diretório de trabalho do host em `/app` no container para permitir o desenvolvimento ativo.
   - Impeça que a pasta `node_modules` do host sobrescreva a versão do container usando um volume anônimo `- /app/node_modules`. Isso evita conflitos de compilação de arquiteturas específicas (ex: módulos nativos compilados no Windows/macOS vs. containers Linux).
   - Garanta que a configuração de hot-reload (ex: `node ace serve --watch` ou `npm run dev`) execute via monitoramento do sistema de arquivos dentro do ambiente Docker.

4. **Configuração de Variáveis (Integração com .env):**
   - Mapeie os hostnames de acordo com a rede interna do container. Na mesma rede do Docker Compose, use `postgres`, `redis` e `meilisearch` em vez de `127.0.0.1` ou `localhost`.
   - Defina valores padrão (fallback) para ambientes locais para que os desenvolvedores possam rodar `docker compose up` imediatamente sem configuração manual.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- NÃO exponha senhas de banco de dados de containers para produção. Garanta que as configurações de docker-compose para desenvolvimento tenham avisos explícitos contra o uso em produção.
- NÃO execute etapas de compilação de produção (como compilar TypeScript via `node ace build`) no estágio de desenvolvimento, pois isso desacelera a inicialização inicial e quebra o hot-reloading ativo.
- Evite utilizar a pasta `node_modules` do host dentro do container. Sempre previna isso através do mapeamento anônimo `/app/node_modules` ou volume especializado.
- Sempre use tags específicas para as versões do banco de dados e serviços de cache (ex: `postgres:16-alpine`, `redis:7-alpine`) em vez de `latest` para evitar atualizações que causem quebras silenciosas.
