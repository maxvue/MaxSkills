# PROPOSTA DE SKILL: vue-i18n-localization-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when implementing, configuring, customizing, or debugging internationalization (i18n) and localization features in Vue 3 applications, managing translation keys, using vue-i18n, formatting dates and currencies locally, or switching locales dynamically. Triggers on vue-i18n setup, $t usage, translation JSON files, and dynamic locale switching components.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O ecossistema Engeapp (especialmente o SocialMediaApp e demais módulos do ecossistema Max) necessita de suporte multi-idioma de alta performance para expansão de mercado (Português, Inglês e Espanhol). É crucial estabelecer um padrão para carregamento assíncrono de locales para otimização de bundle (lazy loading), organização escalável das chaves de tradução em JSON e formatação consistente de moedas, números e datas conforme o locale ativo.
* **Recursos:** Carregamento dinâmico e assíncrono de arquivos JSON de tradução (lazy loading), padronização de nomenclatura de chaves estruturadas por namespace, suporte a pluralização e interpolação de chaves, fallback de idiomas seguro, tipagem estrita de chaves de tradução com TypeScript e formatação localizada de moedas, números e datas usando a API nativa Intl.
* **Objetivo:** Estabelecer diretrizes consistentes e padrões arquiteturais para a implementação, gerenciamento e manutenção de internacionalização (i18n) e localização em aplicações Vue 3 no ecossistema Engeapp.
* **Casos de uso:** Tradução de interfaces de usuário (dashboards, landing pages, formulários, simuladores), troca dinâmica de idioma no perfil ou cabeçalho do usuário, formatação de valores monetários baseada no país do tenant/usuário, persistência de preferências de idioma do usuário em localStorage/cookies e tratamento de traduções ausentes (fallback).
* **Workflows:**
  - `/bug-fix-front-end`
* **Skills próprias utilizadas:**
  - `vue-typescript-best-practices` — Utilizará as regras de tipagem do TypeScript para garantir a segurança no uso de chaves de tradução e funções auxiliares do `vue-i18n`.
  - `vue-maxvue-frontend-best-practices` — Garantirá que a inicialização do plugin do `vue-i18n` e os padrões de componentes de troca de idioma se alinhem com as diretrizes do framework frontend interno `maxvue`.
* **Skills auxiliares:** modern-web-guidance
* **Skills beneficiadas:**
  - `vue-max-components-ui-development-best-practices` — Permitirá que a biblioteca de componentes estilizados receba traduções e chaves localizadas de forma padronizada.
* **Benefícios:** Facilidade de expansão do produto para novos mercados com baixo custo de desenvolvimento, chaves de tradução limpas e organizadas por domínio, melhor performance da aplicação com code-splitting das traduções e redução drástica de erros de strings não traduzidas ou falhas de formatação local.
