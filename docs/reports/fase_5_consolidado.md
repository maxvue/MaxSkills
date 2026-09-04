# Relatório Consolidado de Auditoria de Skills (Fases 1 a 5)

Auditoria completa e diagnóstico determinístico realizado sobre todas as skills do repositório.

## 📊 Distribuição Quantitativa

### Por Estado de Saúde:
- **Crítica:** 0 skills (0.0%)
- **Ruim:** 0 skills (0.0%)
- **Regular:** 2 skills (0.2%)
- **Boa:** 530 skills (60.2%)
- **Excelente:** 349 skills (39.6%)

### Por Destino Conciliado:
- **REMOVER:** 0 skills (0.0%)
- **FUNDIR:** 0 skills (0.0%)
- **PODAR:** 10 skills (1.1%)
- **CORRIGIR:** 525 skills (59.6%)
- **MANTER:** 346 skills (39.3%)

---

## 🔍 Análise de Redundâncias Inter-Skills (Fase 2)

- **Clusters `vue-pinia-state-management-best-practices` & `vue-max-use-usecachedapi-state-cache-best-practices`:** Veredito **LAPIDAR**. Ambas tocam cache e Pinia. Delimitar: vue-pinia para stores e usecachedapi para requisições com cache.
- **Clusters `laravel-gemini-php-sdk-best-practices` & `laravel-gemini-file-api-media-integration-best-practices`:** Veredito **DEMARCAR**. A primeira cuida do client SDK geral; a segunda foca exclusivamente no upload/processamento de mídia na File API.
- **Clusters `laravel-socialite-oauth-integration-best-practices` & `laravel-social-media-oauth-token-lifecycle-management-best-practices`:** Veredito **DEMARCAR**. Socialite foca na autenticação de usuários; Social Media Lifecycle foca no refresh contínuo e expiração de tokens de páginas.

---

## 📋 Tabela Consolidada de Diagnóstico (881 Skills)

| # | Skill | Estado | Nº de Problemas | Destino | Descrição dos Problemas / Veredito |
|---|---|---|---|---|---|
| 1 | `vue-axios-api-integration-best-practices` | Regular | 1 | CORRIGIR | Uso de rota crua '/api/login' no frontend — deve adotar nomes Ziggy com @maxvue/max-use. |
| 2 | `vue-unocss-styling-best-practices` | Regular | 1 | CORRIGIR | Exemplo ensina classes utilitárias inline no template — adotar classes semânticas e estilizar em <style lang="scss">. |
| 3 | `007` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 4 | `ab-test-setup` | Boa | 1 | CORRIGIR | Description curta (112 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 5 | `aegisops-ai` | Boa | 1 | CORRIGIR | Description curta (143 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 6 | `agent-creator` | Boa | 1 | CORRIGIR | Description curta (106 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 7 | `agent-evaluation-reporting` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 8 | `agent-framework-azure-ai-py` | Boa | 1 | CORRIGIR | Description curta (91 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 9 | `agent-harness-fault-injection` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 10 | `agent-manager-skill` | Boa | 1 | CORRIGIR | Description curta (109 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 11 | `agent-memory-mcp` | Boa | 1 | CORRIGIR | Description curta (131 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 12 | `agent-orchestration-improve-agent` | Boa | 1 | CORRIGIR | Description curta (117 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 13 | `agent-orchestrator` | Boa | 1 | CORRIGIR | Description curta (167 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 14 | `agent-qa-authoring` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 15 | `agent-qa-debug-fix` | Boa | 1 | CORRIGIR | Description curta (146 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 16 | `agent-qa-result-triage` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 17 | `agent-self-scheduling` | Boa | 1 | CORRIGIR | Description curta (106 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 18 | `agent-squad` | Boa | 1 | CORRIGIR | Description curta (70 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 19 | `agentfolio` | Boa | 1 | CORRIGIR | Description curta (113 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 20 | `agentmail` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 21 | `ai-agent-development` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 22 | `ai-agents-architect` | Boa | 1 | CORRIGIR | Description curta (140 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 23 | `ai-engineer` | Boa | 1 | CORRIGIR | Description curta (180 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 24 | `ai-ml` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 25 | `ai-studio-image` | Boa | 1 | CORRIGIR | Description curta (155 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 26 | `analytics-product` | Boa | 1 | CORRIGIR | Description curta (127 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 27 | `animejs-animation` | Boa | 1 | CORRIGIR | Description curta (98 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 28 | `anti-reversing-techniques` | Boa | 1 | CORRIGIR | Description curta (122 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 29 | `antigravity-agent-manager` | Boa | 1 | CORRIGIR | Description curta (113 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 30 | `antigravity-design-expert` | Boa | 1 | CORRIGIR | Description curta (144 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 31 | `antigravity-workflows` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 32 | `anywrite` | Boa | 1 | CORRIGIR | Description curta (148 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 33 | `api-endpoint-builder` | Boa | 1 | CORRIGIR | Description curta (163 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 34 | `api-patterns` | Boa | 1 | CORRIGIR | Description curta (119 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 35 | `api-security-best-practices` | Boa | 1 | CORRIGIR | Description curta (160 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 36 | `apify-audience-analysis` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 37 | `apify-competitor-intelligence` | Boa | 1 | CORRIGIR | Description curta (151 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 38 | `apify-ecommerce` | Boa | 1 | CORRIGIR | Description curta (130 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 39 | `app-store-changelog` | Boa | 1 | CORRIGIR | Description curta (81 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 40 | `app-store-optimization` | Boa | 1 | CORRIGIR | Description curta (151 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 41 | `appdeploy` | Boa | 1 | CORRIGIR | Description curta (175 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 42 | `apple-container` | Boa | 1 | CORRIGIR | Description curta (167 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 43 | `application-performance-performance-optimization` | Boa | 1 | CORRIGIR | Description curta (168 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 44 | `architect-review` | Boa | 1 | CORRIGIR | Description curta (61 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 45 | `architecture-decision-records` | Boa | 1 | CORRIGIR | Description curta (178 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 46 | `aria` | Boa | 1 | CORRIGIR | Description curta (79 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 47 | `astro` | Boa | 1 | CORRIGIR | Description curta (139 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 48 | `async-python-patterns` | Boa | 1 | CORRIGIR | Description curta (189 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 49 | `atlas-cloud-media` | Boa | 1 | CORRIGIR | Description curta (136 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 50 | `attack-tree-construction` | Boa | 1 | CORRIGIR | Description curta (169 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 51 | `audio-transcriber` | Boa | 1 | CORRIGIR | Description curta (116 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 52 | `auth-implementation-patterns` | Boa | 1 | CORRIGIR | Description curta (123 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 53 | `autonomous-agent-patterns` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 54 | `avalonia-layout-zafiro` | Boa | 1 | CORRIGIR | Description curta (140 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 55 | `avalonia-zafiro-development` | Boa | 1 | CORRIGIR | Description curta (105 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 56 | `aws-secrets-rotation` | Boa | 1 | CORRIGIR | Description curta (64 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 57 | `aws-skills` | Boa | 1 | CORRIGIR | Description curta (78 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 58 | `azd-deployment` | Boa | 1 | CORRIGIR | Description curta (145 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 59 | `azure-ai-contentunderstanding-py` | Boa | 1 | CORRIGIR | Description curta (126 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 60 | `azure-ai-textanalytics-py` | Boa | 1 | CORRIGIR | Description curta (174 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 61 | `azure-ai-transcription-py` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 62 | `azure-ai-translation-document-py` | Boa | 1 | CORRIGIR | Description curta (181 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 63 | `azure-ai-vision-imageanalysis-java` | Boa | 1 | CORRIGIR | Description curta (175 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 64 | `azure-ai-voicelive-ts` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 65 | `azure-cosmos-java` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 66 | `azure-cosmos-ts` | Boa | 1 | CORRIGIR | Description curta (174 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 67 | `azure-keyvault-keys-ts` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 68 | `azure-mgmt-apicenter-py` | Boa | 1 | CORRIGIR | Description curta (126 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 69 | `azure-monitor-ingestion-py` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 70 | `azure-postgres-ts` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 71 | `azure-speech-to-text-rest-py` | Boa | 1 | CORRIGIR | Description curta (145 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 72 | `azure-storage-blob-ts` | Boa | 1 | CORRIGIR | Description curta (163 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 73 | `backend-security-coder` | Boa | 1 | CORRIGIR | Description curta (188 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 74 | `backtesting-frameworks` | Boa | 1 | CORRIGIR | Description curta (130 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 75 | `base` | Boa | 1 | CORRIGIR | Description curta (79 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 76 | `baseline-ui` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 77 | `bats-testing-patterns` | Boa | 1 | CORRIGIR | Description curta (199 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 78 | `bazel-build-optimization` | Boa | 1 | CORRIGIR | Description curta (165 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 79 | `bdistill-behavioral-xray` | Boa | 1 | CORRIGIR | Description curta (145 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 80 | `bdistill-knowledge-extraction` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 81 | `behavioral-modes` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 82 | `bilig-workpaper` | Boa | 1 | CORRIGIR | Description curta (114 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 83 | `brain-to-docs` | Boa | 1 | CORRIGIR | Description curta (90 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 84 | `brendangregg-use-tsa` | Boa | 1 | CORRIGIR | Description curta (153 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 85 | `brevo-automation` | Boa | 1 | CORRIGIR | Description curta (110 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 86 | `browser-testing-with-devtools` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 87 | `bugs-are-annoying` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 88 | `bun-development` | Boa | 1 | CORRIGIR | Description curta (127 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 89 | `business-analyst` | Boa | 1 | CORRIGIR | Description curta (192 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 90 | `buywhere-product-catalog` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 91 | `c4-architecture-c4-architecture` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 92 | `c4-component` | Boa | 1 | CORRIGIR | Description curta (188 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 93 | `c4-container` | Boa | 1 | CORRIGIR | Description curta (51 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 94 | `c4-context` | Boa | 1 | CORRIGIR | Description curta (172 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 95 | `canvas-design` | Boa | 1 | CORRIGIR | Description curta (162 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 96 | `carrier-relationship-management` | Boa | 1 | CORRIGIR | Description curta (177 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 97 | `cc-skill-backend-patterns` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 98 | `cc-skill-clickhouse-io` | Boa | 1 | CORRIGIR | Description curta (139 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 99 | `cc-skill-coding-standards` | Boa | 1 | CORRIGIR | Description curta (116 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 100 | `cc-skill-frontend-patterns` | Boa | 1 | CORRIGIR | Description curta (116 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 101 | `cdk-patterns` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 102 | `clarvia-aeo-check` | Boa | 1 | CORRIGIR | Description curta (170 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 103 | `claude-monitor` | Boa | 1 | CORRIGIR | Description curta (156 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 104 | `clerk-auth` | Boa | 1 | CORRIGIR | Description curta (97 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 105 | `cloud-architect` | Boa | 1 | CORRIGIR | Description curta (187 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 106 | `cloud-penetration-testing` | Boa | 1 | CORRIGIR | Description curta (150 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 107 | `cloudflare-security-audit` | Boa | 1 | CORRIGIR | Description curta (145 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 108 | `code-review-checklist` | Boa | 1 | CORRIGIR | Description curta (127 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 109 | `code-showcase-core-components` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 110 | `code-showcase-testing-patterns` | Boa | 1 | CORRIGIR | Description curta (176 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 111 | `codebase-audit-pre-push` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 112 | `codebase-to-wordpress-converter` | Boa | 1 | CORRIGIR | Description curta (127 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 113 | `comfyui-gateway` | Boa | 1 | CORRIGIR | Description curta (146 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 114 | `computer-vision-expert` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 115 | `conductor-implement` | Boa | 1 | CORRIGIR | Description curta (71 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 116 | `conductor-revert` | Boa | 1 | CORRIGIR | Description curta (59 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 117 | `content-creator` | Boa | 1 | CORRIGIR | Description curta (100 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 118 | `content-marketer` | Boa | 1 | CORRIGIR | Description curta (162 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 119 | `context-agent` | Boa | 1 | CORRIGIR | Description curta (144 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 120 | `context-compression` | Boa | 1 | CORRIGIR | Description curta (180 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 121 | `context-driven-development` | Boa | 1 | CORRIGIR | Description curta (181 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 122 | `context-engineering` | Boa | 1 | CORRIGIR | Description curta (198 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 123 | `context-kit` | Boa | 1 | CORRIGIR | Description curta (119 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 124 | `context-window-management` | Boa | 1 | CORRIGIR | Description curta (112 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 125 | `conversation-memory` | Boa | 1 | CORRIGIR | Description curta (104 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 126 | `convex` | Boa | 1 | CORRIGIR | Description curta (141 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 127 | `copy-editing` | Boa | 1 | CORRIGIR | Description curta (195 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 128 | `copywriting` | Boa | 1 | PODAR | Description curta (140 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 129 | `copywriting-psychologist` | Boa | 1 | CORRIGIR | Description curta (57 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 130 | `cpp-pro` | Boa | 1 | CORRIGIR | Description curta (153 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 131 | `cqrs-implementation` | Boa | 1 | CORRIGIR | Description curta (186 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 132 | `cross-platform-contract-propagation-audit` | Boa | 1 | CORRIGIR | Description curta (143 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 133 | `crypto-bd-agent` | Boa | 1 | CORRIGIR | Description curta (146 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 134 | `customer-support` | Boa | 1 | CORRIGIR | Description curta (151 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 135 | `customs-trade-compliance` | Boa | 1 | CORRIGIR | Description curta (172 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 136 | `cyber-audit` | Boa | 1 | CORRIGIR | Description curta (96 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 137 | `daily` | Boa | 1 | CORRIGIR | Description curta (50 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 138 | `daily-gift` | Boa | 1 | CORRIGIR | Description curta (177 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 139 | `daily-news-report` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 140 | `damage-control` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 141 | `data-engineering-data-pipeline` | Boa | 1 | CORRIGIR | Description curta (154 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 142 | `data-scientist` | Boa | 1 | CORRIGIR | Description curta (168 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 143 | `database-migrations-migration-observability` | Boa | 1 | CORRIGIR | Description curta (59 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 144 | `database-migrations-sql-migrations` | Boa | 1 | CORRIGIR | Description curta (136 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 145 | `database-optimizer` | Boa | 1 | CORRIGIR | Description curta (116 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 146 | `dbt-transformation-patterns` | Boa | 1 | CORRIGIR | Description curta (144 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 147 | `debugger` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 148 | `debugging-toolkit` | Boa | 1 | CORRIGIR | Description curta (93 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 149 | `deep-research` | Boa | 1 | CORRIGIR | Description curta (109 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 150 | `deepapi` | Boa | 1 | CORRIGIR | Description curta (105 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 151 | `delegating-to-agents` | Boa | 1 | CORRIGIR | Description curta (98 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 152 | `deployment-pipeline-design` | Boa | 1 | CORRIGIR | Description curta (100 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 153 | `design-philosophy` | Boa | 1 | CORRIGIR | Description curta (191 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 154 | `design-taste-frontend` | Boa | 1 | CORRIGIR | Description curta (130 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 155 | `devops-deploy` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 156 | `diagnosing-bugs` | Boa | 1 | PODAR | Description curta (156 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 157 | `differential-review` | Boa | 1 | CORRIGIR | Description curta (57 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 158 | `discord-bot-architect` | Boa | 1 | CORRIGIR | Description curta (199 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 159 | `distribute-skill-to-all-agents` | Boa | 1 | CORRIGIR | Description curta (96 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 160 | `docs-architect` | Boa | 1 | CORRIGIR | Description curta (188 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 161 | `docs-guard` | Boa | 1 | PODAR | Description curta (153 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 162 | `domain-driven-design` | Boa | 1 | CORRIGIR | Description curta (126 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 163 | `drizzle-migration-conflict` | Boa | 1 | CORRIGIR | Description curta (141 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 164 | `drizzle-orm-expert` | Boa | 1 | CORRIGIR | Description curta (180 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 165 | `ecl-harness-engineer` | Boa | 1 | CORRIGIR | Description curta (145 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 166 | `effective-agent-skills` | Boa | 1 | CORRIGIR | Description curta (100 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 167 | `electron-development` | Boa | 1 | CORRIGIR | Description curta (178 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 168 | `email-sequence` | Boa | 1 | CORRIGIR | Description curta (168 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 169 | `email-systems` | Boa | 1 | CORRIGIR | Description curta (181 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 170 | `emil-design-eng` | Boa | 1 | CORRIGIR | Description curta (133 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 171 | `employment-contract-templates` | Boa | 1 | CORRIGIR | Description curta (127 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 172 | `enhance-prompt` | Boa | 1 | CORRIGIR | Description curta (193 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 173 | `expo-api-routes` | Boa | 1 | CORRIGIR | Description curta (66 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 174 | `fal-audio` | Boa | 1 | CORRIGIR | Description curta (59 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 175 | `fal-upscale` | Boa | 1 | CORRIGIR | Description curta (55 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 176 | `fastapi-templates` | Boa | 1 | CORRIGIR | Description curta (196 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 177 | `feature-tracking` | Boa | 1 | CORRIGIR | Description curta (161 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 178 | `find-bugs` | Boa | 1 | CORRIGIR | Description curta (184 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 179 | `firmware-analyst` | Boa | 1 | CORRIGIR | Description curta (105 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 180 | `food-database-query` | Boa | 1 | CORRIGIR | Description curta (19 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 181 | `fp-async` | Boa | 1 | CORRIGIR | Description curta (109 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 182 | `fp-backend` | Boa | 1 | CORRIGIR | Description curta (135 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 183 | `fp-data-transforms` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 184 | `fp-errors` | Boa | 1 | CORRIGIR | Description curta (113 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 185 | `fp-pragmatic` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 186 | `fp-react` | Boa | 1 | CORRIGIR | Description curta (122 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 187 | `fp-refactor` | Boa | 1 | CORRIGIR | Description curta (91 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 188 | `fp-taskeither-ref` | Boa | 1 | CORRIGIR | Description curta (127 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 189 | `fp-types-ref` | Boa | 1 | CORRIGIR | Description curta (134 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 190 | `frontend-dev-guidelines` | Boa | 1 | CORRIGIR | Description curta (188 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 191 | `frontend-developer` | Boa | 1 | CORRIGIR | Description curta (158 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 192 | `frontend-lighthouse` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 193 | `frontend-slides` | Boa | 1 | CORRIGIR | Description curta (98 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 194 | `frontend-ui-dark-ts` | Boa | 1 | CORRIGIR | Description curta (192 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 195 | `gdb-cli` | Boa | 1 | CORRIGIR | Description curta (144 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 196 | `gemini-deep-research` | Boa | 1 | CORRIGIR | Description curta (179 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 197 | `generate-nanobanana` | Boa | 1 | CORRIGIR | Description curta (189 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 198 | `get-shit-done` | Boa | 1 | CORRIGIR | Description curta (123 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 199 | `gha-security-review` | Boa | 1 | CORRIGIR | Description curta (171 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 200 | `git-advanced-workflows` | Boa | 1 | CORRIGIR | Description curta (130 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 201 | `git-hooks-automation` | Boa | 1 | CORRIGIR | Description curta (190 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 202 | `git-pr-review` | Boa | 1 | CORRIGIR | Description curta (93 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 203 | `git-workflow-and-versioning` | Boa | 1 | CORRIGIR | Description curta (188 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 204 | `git-worktree` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 205 | `github` | Boa | 1 | CORRIGIR | Description curta (81 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 206 | `github-workflow-automation` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 207 | `global-chat-agent-discovery` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 208 | `go-rod-master` | Boa | 1 | CORRIGIR | Description curta (145 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 209 | `goal-loop` | Boa | 1 | CORRIGIR | Description curta (102 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 210 | `golang-pro` | Boa | 1 | CORRIGIR | Description curta (121 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 211 | `google-calendar-automation` | Boa | 1 | CORRIGIR | Description curta (101 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 212 | `gpt-taste` | Boa | 1 | CORRIGIR | Description curta (126 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 213 | `graphql-architect` | Boa | 1 | CORRIGIR | Description curta (171 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 214 | `grilling` | Boa | 1 | CORRIGIR | Description curta (155 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 215 | `grok-build` | Boa | 1 | CORRIGIR | Description curta (184 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 216 | `growth-engine` | Boa | 1 | CORRIGIR | Description curta (147 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 217 | `handoff` | Boa | 1 | CORRIGIR | Description curta (86 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 218 | `hasdata` | Boa | 1 | CORRIGIR | Description curta (69 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 219 | `hierarchical-agent-memory` | Boa | 1 | CORRIGIR | Description curta (177 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 220 | `hig-components-status` | Boa | 1 | PODAR | Description curta (120 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 221 | `hig-patterns` | Boa | 1 | CORRIGIR | Description curta (61 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 222 | `hono` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 223 | `hybrid-cloud-networking` | Boa | 1 | CORRIGIR | Description curta (135 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 224 | `iconsax-library` | Boa | 1 | CORRIGIR | Description curta (84 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 225 | `idea-autopsy` | Boa | 1 | CORRIGIR | Description curta (177 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 226 | `imagen` | Boa | 1 | CORRIGIR | Description curta (148 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 227 | `improve-codebase-architecture` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 228 | `indexing-issue-auditor` | Boa | 1 | CORRIGIR | Description curta (148 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 229 | `industrial-brutalist-ui` | Boa | 1 | CORRIGIR | Description curta (130 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 230 | `ingest-youtube` | Boa | 1 | CORRIGIR | Description curta (154 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 231 | `instagram` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 232 | `javascript-mastery` | Boa | 1 | CORRIGIR | Description curta (139 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 233 | `javascript-pro` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 234 | `javascript-testing-patterns` | Boa | 1 | CORRIGIR | Description curta (152 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 235 | `junta-leiloeiros` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 236 | `k6-load-testing` | Boa | 1 | CORRIGIR | Description curta (153 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 237 | `k8s-security-policies` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 238 | `kaizen` | Boa | 1 | CORRIGIR | Description curta (173 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 239 | `keyword-extractor` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 240 | `kotler-macro-analyzer` | Boa | 1 | CORRIGIR | Description curta (98 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 241 | `kpi-dashboard-design` | Boa | 1 | CORRIGIR | Description curta (120 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 242 | `kubestellar-console` | Boa | 1 | CORRIGIR | Description curta (106 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 243 | `lambdatest-agent-skills` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 244 | `langchain-architecture` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 245 | `legacy-modernizer` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 246 | `leiloeiro-risco` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 247 | `linkedin-cli` | Boa | 1 | CORRIGIR | Description curta (148 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 248 | `linkedin-content-generator` | Boa | 1 | CORRIGIR | Description curta (178 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 249 | `linkedin-post-writer` | Boa | 1 | CORRIGIR | Description curta (193 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 250 | `linkedin-profile-optimizer` | Boa | 1 | CORRIGIR | Description curta (160 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 251 | `linkerd-patterns` | Boa | 1 | CORRIGIR | Description curta (107 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 252 | `linux-troubleshooting` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 253 | `llm-app-patterns` | Boa | 1 | CORRIGIR | Description curta (140 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 254 | `llm-application-dev-langchain-agent` | Boa | 1 | CORRIGIR | Description curta (123 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 255 | `llm-council` | Boa | 1 | CORRIGIR | Description curta (101 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 256 | `llm-evaluation` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 257 | `llm-ops` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 258 | `llm-structured-output` | Boa | 1 | CORRIGIR | Description curta (161 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 259 | `local-legal-seo-audit` | Boa | 1 | CORRIGIR | Description curta (196 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 260 | `local-llm-expert` | Boa | 1 | CORRIGIR | Description curta (196 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 261 | `logic-lens` | Boa | 1 | CORRIGIR | Description curta (180 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 262 | `loki-mode` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 263 | `lore` | Boa | 1 | CORRIGIR | Description curta (199 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 264 | `luna` | Boa | 1 | CORRIGIR | Description curta (66 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 265 | `m365-agents-ts` | Boa | 1 | CORRIGIR | Description curta (48 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 266 | `magic-animator` | Boa | 1 | CORRIGIR | Description curta (91 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 267 | `magic-ui-generator` | Boa | 1 | CORRIGIR | Description curta (113 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 268 | `mailtrap-managing-contacts` | Boa | 1 | CORRIGIR | Description curta (123 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 269 | `mailtrap-sending-emails` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 270 | `makepad-skills` | Boa | 1 | CORRIGIR | Description curta (102 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 271 | `manage-skills` | Boa | 1 | CORRIGIR | Description curta (186 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 272 | `manifest` | Boa | 1 | CORRIGIR | Description curta (156 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 273 | `markdown-rendering` | Boa | 1 | CORRIGIR | Description curta (78 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 274 | `marketing-ideas` | Boa | 1 | PODAR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 275 | `marketing-psychology` | Boa | 1 | CORRIGIR | Description curta (141 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 276 | `markstream-custom-components` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 277 | `markstream-install` | Boa | 1 | CORRIGIR | Description curta (133 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 278 | `markstream-migration` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 279 | `markstream-nuxt` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 280 | `markstream-react` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 281 | `markstream-vue` | Boa | 1 | CORRIGIR | Description curta (156 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 282 | `mason` | Boa | 1 | CORRIGIR | Description curta (77 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 283 | `mcp-tool-developer` | Boa | 1 | CORRIGIR | Description curta (163 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 284 | `mdpr-skill` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 285 | `mermaid-diagrammer` | Boa | 1 | CORRIGIR | Description curta (122 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 286 | `mesh-memory` | Boa | 1 | CORRIGIR | Description curta (184 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 287 | `minimalist-ui` | Boa | 1 | CORRIGIR | Description curta (133 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 288 | `modellix` | Boa | 1 | CORRIGIR | Description curta (131 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 289 | `modern-javascript-patterns` | Boa | 1 | CORRIGIR | Description curta (174 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 290 | `monte-carlo-monitoring-advisor` | Boa | 1 | CORRIGIR | Description curta (163 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 291 | `monte-carlo-prevent` | Boa | 1 | CORRIGIR | Description curta (115 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 292 | `monte-carlo-validation-notebook` | Boa | 1 | CORRIGIR | Description curta (91 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 293 | `moodle-external-api-development` | Boa | 1 | CORRIGIR | Description curta (151 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 294 | `moyu` | Boa | 1 | CORRIGIR | Description curta (147 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 295 | `multi-agent-task-orchestrator` | Boa | 1 | CORRIGIR | Description curta (109 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 296 | `multi-platform-apps-multi-platform` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 297 | `n8n-agents` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 298 | `n8n-binary-and-data` | Boa | 1 | CORRIGIR | Description curta (122 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 299 | `n8n-code-tool` | Boa | 1 | CORRIGIR | Description curta (133 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 300 | `nerdzao-elite-gemini-high` | Boa | 1 | CORRIGIR | Description curta (158 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 301 | `network-engineer` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 302 | `nextjs-seo-indexing` | Boa | 1 | CORRIGIR | Description curta (195 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 303 | `nextjs-supabase-auth` | Boa | 1 | CORRIGIR | Description curta (59 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 304 | `nodejs-best-practices` | Boa | 1 | CORRIGIR | Description curta (147 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 305 | `obsidian-cli` | Boa | 1 | CORRIGIR | Description curta (146 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 306 | `odoo-automated-tests` | Boa | 1 | CORRIGIR | Description curta (144 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 307 | `odoo-backup-strategy` | Boa | 1 | CORRIGIR | Description curta (151 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 308 | `odoo-ecommerce-configurator` | Boa | 1 | CORRIGIR | Description curta (138 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 309 | `odoo-migration-helper` | Boa | 1 | CORRIGIR | Description curta (148 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 310 | `odoo-orm-expert` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 311 | `odoo-performance-tuner` | Boa | 1 | CORRIGIR | Description curta (154 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 312 | `odoo-qweb-templates` | Boa | 1 | CORRIGIR | Description curta (136 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 313 | `odoo-rpc-api` | Boa | 1 | CORRIGIR | Description curta (170 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 314 | `odoo-security-rules` | Boa | 1 | CORRIGIR | Description curta (120 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 315 | `odoo-shopify-integration` | Boa | 1 | CORRIGIR | Description curta (142 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 316 | `odoo-xml-views-builder` | Boa | 1 | CORRIGIR | Description curta (151 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 317 | `ontoly-software-graph` | Boa | 1 | CORRIGIR | Description curta (155 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 318 | `optim-agent` | Boa | 1 | CORRIGIR | Description curta (165 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 319 | `orchestrate-batch-refactor` | Boa | 1 | CORRIGIR | Description curta (90 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 320 | `osterwalder-canvas-architect` | Boa | 1 | CORRIGIR | Description curta (108 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 321 | `outreachagent` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 322 | `page-cro` | Boa | 1 | CORRIGIR | Description curta (65 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 323 | `pagespeed-enhancer` | Boa | 1 | CORRIGIR | Description curta (176 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 324 | `pakistan-payments-stack` | Boa | 1 | CORRIGIR | Description curta (190 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 325 | `papers-skill` | Boa | 1 | CORRIGIR | Description curta (177 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 326 | `pci-compliance` | Boa | 1 | CORRIGIR | Description curta (135 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 327 | `people-data` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 328 | `performance-optimizer` | Boa | 1 | CORRIGIR | Description curta (123 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 329 | `performance-profiling` | Boa | 1 | CORRIGIR | Description curta (85 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 330 | `photopea-embedded-editor` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 331 | `php-pro` | Boa | 1 | CORRIGIR | Description curta (153 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 332 | `pi-custom-model` | Boa | 1 | CORRIGIR | Description curta (84 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 333 | `pilot-protocol` | Boa | 1 | CORRIGIR | Description curta (118 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 334 | `pipecat-friday-agent` | Boa | 1 | CORRIGIR | Description curta (113 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 335 | `piv-loop` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 336 | `plaid-fintech` | Boa | 1 | CORRIGIR | Description curta (198 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 337 | `planning-with-files` | Boa | 1 | CORRIGIR | Description curta (80 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 338 | `playwright-java` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 339 | `podcast-generation` | Boa | 1 | CORRIGIR | Description curta (83 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 340 | `polis-protocol` | Boa | 1 | CORRIGIR | Description curta (156 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 341 | `postgres-readonly-queries` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 342 | `postgresql` | Boa | 1 | CORRIGIR | Description curta (138 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 343 | `pr-merge-champion` | Boa | 1 | CORRIGIR | Description curta (136 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 344 | `prisma-expert` | Boa | 1 | CORRIGIR | Description curta (183 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 345 | `product-decision-agent` | Boa | 1 | CORRIGIR | Description curta (114 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 346 | `product-inventor` | Boa | 1 | CORRIGIR | Description curta (185 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 347 | `product-manager` | Boa | 1 | CORRIGIR | Description curta (135 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 348 | `progressive-estimation` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 349 | `project-development` | Boa | 1 | CORRIGIR | Description curta (179 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 350 | `prompt-engineering-patterns` | Boa | 1 | CORRIGIR | Description curta (108 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 351 | `protect-mcp-governance` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 352 | `protocol-reverse-engineering` | Boa | 1 | CORRIGIR | Description curta (140 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 353 | `prototype` | Boa | 1 | CORRIGIR | Description curta (183 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 354 | `puppeteer-skill` | Boa | 1 | CORRIGIR | Description curta (167 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 355 | `pydantic-ai` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 356 | `pydantic-models-py` | Boa | 1 | CORRIGIR | Description curta (81 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 357 | `pypict-skill` | Boa | 1 | CORRIGIR | Description curta (24 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 358 | `pytest-and-jest-automation` | Boa | 1 | CORRIGIR | Description curta (135 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 359 | `python-pro` | Boa | 1 | CORRIGIR | Description curta (199 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 360 | `python-testing-patterns` | Boa | 1 | CORRIGIR | Description curta (198 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 361 | `quinn` | Boa | 1 | CORRIGIR | Description curta (75 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 362 | `quit-sponsor` | Boa | 1 | CORRIGIR | Description curta (189 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 363 | `radix-ui-design-system` | Boa | 1 | CORRIGIR | Description curta (178 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 364 | `rag-implementation` | Boa | 1 | CORRIGIR | Description curta (162 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 365 | `rayden-code` | Boa | 1 | CORRIGIR | Description curta (102 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 366 | `react-component-performance` | Boa | 1 | CORRIGIR | Description curta (70 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 367 | `react-components` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 368 | `react-flow-architect` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 369 | `react-flow-node-ts` | Boa | 1 | CORRIGIR | Description curta (116 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 370 | `react-native-architecture` | Boa | 1 | CORRIGIR | Description curta (153 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 371 | `react-patterns` | Boa | 1 | CORRIGIR | Description curta (97 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 372 | `readme` | Boa | 1 | CORRIGIR | Description curta (194 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 373 | `recallmax` | Boa | 1 | CORRIGIR | Description curta (171 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 374 | `receiving-code-review` | Boa | 1 | CORRIGIR | Description curta (69 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 375 | `recursive-context-pruning-token-budgeting` | Boa | 1 | CORRIGIR | Description curta (138 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 376 | `redesign-existing-projects` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 377 | `reference-builder` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 378 | `remote-gpu-trainer` | Boa | 1 | CORRIGIR | Description curta (197 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 379 | `remotion-best-practices` | Boa | 1 | CORRIGIR | Description curta (53 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 380 | `repo-maintainer` | Boa | 1 | CORRIGIR | Description curta (196 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 381 | `resolving-merge-conflicts` | Boa | 1 | CORRIGIR | Description curta (70 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 382 | `review-animations` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 383 | `riffkit` | Boa | 1 | CORRIGIR | Description curta (192 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 384 | `robius-app-architecture` | Boa | 1 | CORRIGIR | Description curta (192 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 385 | `routerbase-model-gateway` | Boa | 1 | CORRIGIR | Description curta (129 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 386 | `ruby-pro` | Boa | 1 | CORRIGIR | Description curta (164 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 387 | `saas-multi-tenant` | Boa | 1 | CORRIGIR | Description curta (192 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 388 | `saas-mvp-launcher` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 389 | `sankhya-dashboard-html-jsp-custom-best-pratices` | Boa | 1 | CORRIGIR | Description curta (148 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 390 | `sast-configuration` | Boa | 1 | CORRIGIR | Description curta (169 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 391 | `schema-markup` | Boa | 1 | PODAR | Description curta (114 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 392 | `screenshots` | Boa | 1 | CORRIGIR | Description curta (171 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 393 | `security-audit` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 394 | `security-auditor` | Boa | 1 | CORRIGIR | Description curta (106 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 395 | `security-bluebook-builder` | Boa | 1 | CORRIGIR | Description curta (198 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 396 | `security-checklist` | Boa | 1 | CORRIGIR | Description curta (51 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 397 | `security-requirement-extraction` | Boa | 1 | CORRIGIR | Description curta (193 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 398 | `security-scanning-security-hardening` | Boa | 1 | CORRIGIR | Description curta (115 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 399 | `seek-and-analyze-video` | Boa | 1 | CORRIGIR | Description curta (108 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 400 | `semgrep-rule-creator` | Boa | 1 | CORRIGIR | Description curta (179 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 401 | `sendblue-cli` | Boa | 1 | CORRIGIR | Description curta (173 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 402 | `sendblue-notify` | Boa | 1 | CORRIGIR | Description curta (183 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 403 | `sendgrid-automation` | Boa | 1 | CORRIGIR | Description curta (197 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 404 | `seo-cannibalization-detector` | Boa | 1 | CORRIGIR | Description curta (183 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 405 | `seo-content-planner` | Boa | 1 | CORRIGIR | Description curta (168 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 406 | `seo-content-refresher` | Boa | 1 | CORRIGIR | Description curta (185 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 407 | `seo-dataforseo` | Boa | 1 | PODAR | Description curta (190 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 408 | `seo-drift` | Boa | 1 | CORRIGIR | Description curta (131 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 409 | `seo-forensic-incident-response` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 410 | `seo-fundamentals` | Boa | 1 | CORRIGIR | Description curta (144 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 411 | `seo-image-gen` | Boa | 1 | CORRIGIR | Description curta (189 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 412 | `seo-meta-optimizer` | Boa | 1 | CORRIGIR | Description curta (188 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 413 | `seo-schema` | Boa | 1 | CORRIGIR | Description curta (172 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 414 | `seo-structure-architect` | Boa | 1 | CORRIGIR | Description curta (174 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 415 | `shadcn-ui` | Boa | 1 | CORRIGIR | Description curta (134 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 416 | `shopify-development` | Boa | 1 | CORRIGIR | Description curta (100 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 417 | `similarity-search-patterns` | Boa | 1 | CORRIGIR | Description curta (171 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 418 | `skill-audit` | Boa | 1 | CORRIGIR | Description curta (110 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 419 | `skill-optimizer` | Boa | 1 | CORRIGIR | Description curta (175 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 420 | `skill-scanner` | Boa | 1 | CORRIGIR | Description curta (160 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 421 | `skill-seekers` | Boa | 1 | CORRIGIR | Description curta (110 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 422 | `skill-writer` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 423 | `smart-git-automation` | Boa | 1 | CORRIGIR | Description curta (78 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 424 | `social-metadata-hardening` | Boa | 1 | CORRIGIR | Description curta (187 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 425 | `social-post-writer-seo` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 426 | `software-architecture` | Boa | 1 | CORRIGIR | Description curta (190 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 427 | `spark-optimization` | Boa | 1 | CORRIGIR | Description curta (192 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 428 | `spline-3d-integration` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 429 | `sql-injection-testing` | Boa | 1 | CORRIGIR | Description curta (199 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 430 | `sql-optimization-patterns` | Boa | 1 | CORRIGIR | Description curta (137 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 431 | `sql-pro` | Boa | 1 | CORRIGIR | Description curta (177 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 432 | `sqlmap-database-pentesting` | Boa | 1 | CORRIGIR | Description curta (101 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 433 | `sred-project-organizer` | Boa | 1 | CORRIGIR | Description curta (111 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 434 | `sshepherd` | Boa | 1 | CORRIGIR | Description curta (184 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 435 | `startup-metrics-framework` | Boa | 1 | CORRIGIR | Description curta (150 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 436 | `stitch-design-taste` | Boa | 1 | CORRIGIR | Description curta (132 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 437 | `stride-analysis-patterns` | Boa | 1 | CORRIGIR | Description curta (169 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 438 | `supabase-postgres-best-practices` | Boa | 1 | CORRIGIR | Description curta (183 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 439 | `super-code` | Boa | 1 | CORRIGIR | Description curta (138 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 440 | `superpowers` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 441 | `supply-chain-risk-auditor` | Boa | 1 | CORRIGIR | Description curta (182 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 442 | `sveltekit` | Boa | 1 | CORRIGIR | Description curta (127 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 443 | `tailwind-css` | Boa | 1 | CORRIGIR | Description curta (129 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 444 | `tailwind-design-system` | Boa | 1 | CORRIGIR | Description curta (141 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 445 | `tailwind-patterns` | Boa | 1 | CORRIGIR | Description curta (115 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 446 | `taisly-social-media-posting` | Boa | 1 | CORRIGIR | Description curta (140 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 447 | `talivia-agent-kit` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 448 | `tavily-web` | Boa | 1 | CORRIGIR | Description curta (198 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 449 | `tdd` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 450 | `tdd-orchestrator` | Boa | 1 | CORRIGIR | Description curta (158 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 451 | `tdd-workflows-tdd-green` | Boa | 1 | CORRIGIR | Description curta (84 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 452 | `tdd-workflows-tdd-red` | Boa | 1 | CORRIGIR | Description curta (88 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 453 | `tdd-workflows-tdd-refactor` | Boa | 1 | CORRIGIR | Description curta (48 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 454 | `technical-change-tracker` | Boa | 1 | CORRIGIR | Description curta (117 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 455 | `telegram-bot-messaging` | Boa | 1 | CORRIGIR | Description curta (189 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 456 | `test-automator` | Boa | 1 | CORRIGIR | Description curta (183 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 457 | `test-driven-development` | Boa | 1 | CORRIGIR | Description curta (79 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 458 | `test-guard` | Boa | 1 | CORRIGIR | Description curta (115 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 459 | `the-library` | Boa | 1 | CORRIGIR | Description curta (123 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 460 | `threat-mitigation-mapping` | Boa | 1 | CORRIGIR | Description curta (181 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 461 | `threejs-lighting` | Boa | 1 | CORRIGIR | Description curta (160 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 462 | `threejs-materials` | Boa | 1 | CORRIGIR | Description curta (187 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 463 | `time-ledger` | Boa | 1 | CORRIGIR | Description curta (168 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 464 | `token-optimization` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 465 | `trading-ledger` | Boa | 1 | CORRIGIR | Description curta (191 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 466 | `tree-ring-memory` | Boa | 1 | CORRIGIR | Description curta (151 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 467 | `trpc-fullstack` | Boa | 1 | CORRIGIR | Description curta (131 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 468 | `typescript` | Boa | 1 | CORRIGIR | Description curta (55 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 469 | `typescript-expert` | Boa | 1 | CORRIGIR | Description curta (168 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 470 | `typescript-pro` | Boa | 1 | CORRIGIR | Description curta (145 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 471 | `ui-a11y` | Boa | 1 | CORRIGIR | Description curta (63 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 472 | `ui-lint` | Boa | 1 | CORRIGIR | Description curta (73 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 473 | `ui-page` | Boa | 1 | CORRIGIR | Description curta (69 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 474 | `ui-pattern` | Boa | 1 | CORRIGIR | Description curta (107 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 475 | `ui-score` | Boa | 1 | CORRIGIR | Description curta (185 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 476 | `ui-skills` | Boa | 1 | CORRIGIR | Description curta (74 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 477 | `ui-skills-root` | Boa | 1 | CORRIGIR | Description curta (101 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 478 | `ui-tokens` | Boa | 1 | CORRIGIR | Description curta (65 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 479 | `ui-update` | Boa | 1 | CORRIGIR | Description curta (85 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 480 | `ui-ux-designer` | Boa | 1 | CORRIGIR | Description curta (130 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 481 | `ui-ux-pro-max` | Boa | 1 | CORRIGIR | Description curta (179 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 482 | `ui-visual-validator` | Boa | 1 | CORRIGIR | Description curta (119 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 483 | `uncle-bob-craft` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 484 | `unit-testing-test-generate` | Boa | 1 | CORRIGIR | Description curta (106 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 485 | `unship` | Boa | 1 | CORRIGIR | Description curta (106 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 486 | `user-thoughts` | Boa | 1 | CORRIGIR | Description curta (196 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 487 | `ux-audit` | Boa | 1 | CORRIGIR | Description curta (90 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 488 | `ux-copy` | Boa | 1 | CORRIGIR | Description curta (120 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 489 | `ux-feedback` | Boa | 1 | CORRIGIR | Description curta (92 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 490 | `ux-flow` | Boa | 1 | CORRIGIR | Description curta (71 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 491 | `uxui-principles` | Boa | 1 | CORRIGIR | Description curta (133 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 492 | `varlock-claude-skill` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 493 | `vector-index-tuning` | Boa | 1 | CORRIGIR | Description curta (175 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 494 | `vercel-ai-sdk-expert` | Boa | 1 | CORRIGIR | Description curta (173 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 495 | `vercel-optimize` | Boa | 1 | CORRIGIR | Description curta (136 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 496 | `vercel-react-view-transitions` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 497 | `vibers-code-review` | Boa | 1 | CORRIGIR | Description curta (140 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 498 | `video-content-extractor` | Boa | 1 | CORRIGIR | Description curta (175 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 499 | `video-router` | Boa | 1 | CORRIGIR | Description curta (157 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 500 | `voice-ai-engine-development` | Boa | 1 | CORRIGIR | Description curta (183 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 501 | `vscode-extension-guide-en` | Boa | 1 | CORRIGIR | Description curta (83 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 502 | `vue-components` | Boa | 1 | CORRIGIR | Description curta (95 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 503 | `vulnerability-scanner` | Boa | 1 | CORRIGIR | Description curta (123 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 504 | `warehouse` | Boa | 1 | CORRIGIR | Description curta (114 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 505 | `weaviate` | Boa | 1 | CORRIGIR | Description curta (128 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 506 | `web-artifacts-builder` | Boa | 1 | CORRIGIR | Description curta (67 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 507 | `web-project-brainstorming` | Boa | 1 | CORRIGIR | Description curta (184 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 508 | `web-scraper` | Boa | 1 | CORRIGIR | Description curta (154 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 509 | `web-security-testing` | Boa | 1 | CORRIGIR | Description curta (149 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 510 | `webapp-testing` | Boa | 1 | CORRIGIR | Description curta (71 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 511 | `wechat-official-account-strategist` | Boa | 1 | CORRIGIR | Description curta (144 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 512 | `wiki-architect` | Boa | 1 | CORRIGIR | Description curta (112 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 513 | `wiki-builder` | Boa | 1 | CORRIGIR | Description curta (119 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 514 | `wiki-changelog` | Boa | 1 | CORRIGIR | Description curta (193 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 515 | `wiki-page-writer` | Boa | 1 | CORRIGIR | Description curta (125 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 516 | `wireshark-analysis` | Boa | 1 | CORRIGIR | Description curta (186 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 517 | `wordpress-centric-high-seo-optimized-blogwriting-skill` | Boa | 1 | CORRIGIR | Description curta (174 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 518 | `wordpress-penetration-testing` | Boa | 1 | CORRIGIR | Description curta (92 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 519 | `wordpress-woocommerce-development` | Boa | 1 | CORRIGIR | Description curta (199 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 520 | `workflow-orchestration-patterns` | Boa | 1 | CORRIGIR | Description curta (179 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 521 | `workflow-patterns` | Boa | 1 | CORRIGIR | Description curta (181 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 522 | `wp-guard` | Boa | 1 | CORRIGIR | Description curta (135 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 523 | `wp-site-health-auditor` | Boa | 1 | CORRIGIR | Description curta (184 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 524 | `writer` | Boa | 1 | CORRIGIR | Description curta (104 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 525 | `writing-skills` | Boa | 1 | CORRIGIR | Description curta (55 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 526 | `x-twitter-scraper` | Boa | 1 | CORRIGIR | Description curta (174 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 527 | `xiaohongshu-content-strategist` | Boa | 1 | CORRIGIR | Description curta (161 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 528 | `youtube-full` | Boa | 1 | CORRIGIR | Description curta (159 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 529 | `youtube-notetaker` | Boa | 1 | CORRIGIR | Description curta (119 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 530 | `youtube-seo-optimizer` | Boa | 1 | CORRIGIR | Description curta (185 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 531 | `youtube-summarizer` | Boa | 1 | CORRIGIR | Description curta (124 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 532 | `youtube-transcript` | Boa | 1 | CORRIGIR | Description curta (95 caracteres) — expandir para faixa 200 a 400 caracteres mantendo termos acionáveis. |
| 533 | `2slides-ppt-generator` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 534 | `ab-testing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 535 | `ad-creative` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 536 | `adhx` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 537 | `agent-evaluation` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 538 | `agent-memory-systems` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 539 | `agent-tool-builder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 540 | `agentic-actions-auditor` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 541 | `agentphone` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 542 | `ai-native-cli` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 543 | `ai-seo` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 544 | `akf-trust-metadata` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 545 | `analytics` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 546 | `andrej-karpathy` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 547 | `api-analyzer` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 548 | `api-and-interface-design` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 549 | `api-and-interface-design` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 550 | `api-fuzzing-bug-bounty` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 551 | `api-integration` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 552 | `api-onboarding` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 553 | `api-sdk-generator` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 554 | `apify-actorization` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 555 | `applicationinsights-web-ts` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 556 | `atlas-contract` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 557 | `audit-agent-run-evidence` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 558 | `aws-agentic-ai` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 559 | `aws-cost-operations` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 560 | `aws-mcp-setup` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 561 | `aws-serverless-eda` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 562 | `awt-e2e-testing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 563 | `backend-dev-guidelines` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 564 | `bdi-mental-states` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 565 | `biopython` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 566 | `blueprint` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 567 | `brand-guidelines` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 568 | `brave-man` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 569 | `broken-authentication` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 570 | `brooks-audit` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 571 | `brooks-harness` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 572 | `brooks-sweep` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 573 | `brooks-test` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 574 | `browser-automation` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 575 | `burp-suite-testing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 576 | `burpsuite-project-parser` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 577 | `c4-code` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 578 | `cc-skill-security-review` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 579 | `ci-cd-and-automation` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 580 | `cicd-automation-workflow-automate` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 581 | `ckw-design` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 582 | `claimable-postgres` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 583 | `co-marketing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 584 | `code-documentation-code-explain` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 585 | `code-documentation-doc-generate` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 586 | `code-refactoring-refactor-clean` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 587 | `code-review-and-quality` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 588 | `code-simplifier` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 589 | `codebase-cleanup-deps-audit` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 590 | `cohesivity` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 591 | `commit` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 592 | `competitor-tracking` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 593 | `compile-knowledge` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 594 | `comprehensive-review-pr-enhance` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 595 | `computer-use-agents` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 596 | `container-security-hardening` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 597 | `content-strategy` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 598 | `context7-auto-research` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 599 | `create-branch` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 600 | `cro` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 601 | `cucumber-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 602 | `cypress-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 603 | `database-cloud-optimization-cost-optimize` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 604 | `dbos-typescript` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 605 | `debug-buttercup` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 606 | `debugging-code` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 607 | `defuddle` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 608 | `design-system` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 609 | `design-thinking` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 610 | `design-ux` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 611 | `deterministic-design` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 612 | `devcontainer-setup` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 613 | `developer-audience-context` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 614 | `developer-newsletter` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 615 | `developer-sandbox` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 616 | `developer-seo` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 617 | `developer-signup-flow` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 618 | `devrel-content` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 619 | `distributed-debugging-debug-trace` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 620 | `docker-expert` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 621 | `docs-as-marketing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 622 | `documentation-and-adrs` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 623 | `dos-verify-done-claims` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 624 | `doubt-driven-development` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 625 | `dwarf-expert` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 626 | `ejentum-reasoning-harness` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 627 | `ethical-hacking-methodology` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 628 | `event-sourcing-architect` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 629 | `exa-search` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 630 | `expo-examples` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 631 | `expo-module` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 632 | `find-complementary-founders` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 633 | `firebase` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 634 | `firecrawl-scraper` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 635 | `fixing-metadata` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 636 | `fixing-motion-performance` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 637 | `flowhunt-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 638 | `frontend-api-integration-patterns` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 639 | `frontend-architecture` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 640 | `frontend-data-contracts` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 641 | `frontend-design` | Excelente | 0 | PODAR | Conforme e aderente aos padrões de engenharia. |
| 642 | `frontend-design-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 643 | `frontend-mobile-security-xss-scan` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 644 | `frontend-observability` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 645 | `frontend-optimistic-mutations` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 646 | `frontend-seo` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 647 | `frontend-ui-engineering` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 648 | `fsi-compliance-checker` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 649 | `gemini-api-dev` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 650 | `gemini-interactions-api` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 651 | `gemini-omni-flash-api` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 652 | `git-pr-workflows-onboard` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 653 | `git-pr-workflows-pr-enhance` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 654 | `git-pushing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 655 | `github-actions-advanced` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 656 | `github-presence` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 657 | `hf-mcp` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 658 | `hugging-face-datasets` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 659 | `hugging-face-evaluation` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 660 | `hugging-face-model-trainer` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 661 | `hugging-face-paper-publisher` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 662 | `hugging-face-papers` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 663 | `hugging-face-tool-builder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 664 | `hugging-face-trackio` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 665 | `hugging-face-vision-trainer` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 666 | `huggingface-spaces` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 667 | `huggingface-tool-builder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 668 | `hugo-to-markdown` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 669 | `hyperexecute-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 670 | `idea-refine` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 671 | `image-generator` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 672 | `javascript-typescript-typescript-scaffold` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 673 | `jest-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 674 | `junit-5-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 675 | `langfuse` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 676 | `laravel-ai-agents-ecosystem` | Excelente | 0 | PODAR | Conforme e aderente aos padrões de engenharia. |
| 677 | `laravel-ai-bank-ticket-processing-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 678 | `laravel-ai-datasheet-extraction-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 679 | `laravel-anticaptcha-integration-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 680 | `laravel-api-integration-patterns` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 681 | `laravel-authorization-policies-gates` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 682 | `laravel-brazilian-data-queries-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 683 | `laravel-brazilian-localization-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 684 | `laravel-brazilian-payments-integration` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 685 | `laravel-browser-automation-webdriver` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 686 | `laravel-cache-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 687 | `laravel-cloud-storage-integrations` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 688 | `laravel-concessionaires-connection-regulation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 689 | `laravel-digital-signatures-integration` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 690 | `laravel-editorial-calendar-event-workflow-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 691 | `laravel-electrical-calculations-dimensioning-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 692 | `laravel-engeapp-project-homologation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 693 | `laravel-exception-handling-logging` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 694 | `laravel-finance-coupons-discounts-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 695 | `laravel-frankenphp-octane-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 696 | `laravel-gemini-file-api-media-integration-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 697 | `laravel-gemini-php-sdk-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 698 | `laravel-global-helpers-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 699 | `laravel-holiday-sla-calculation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 700 | `laravel-jobs-queues-horizon-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 701 | `laravel-livekit-server-sdk-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 702 | `laravel-media-library-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 703 | `laravel-meta-graph-api-integration-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 704 | `laravel-migrations-seeders-factories-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 705 | `laravel-multitenancy-data-isolation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 706 | `laravel-pdf-handling-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 707 | `laravel-performance-and-profiling-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 708 | `laravel-pest-testing-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 709 | `laravel-php-code-quality-tooling` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 710 | `laravel-power-of-attorney-generation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 711 | `laravel-qrcode-generation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 712 | `laravel-rate-limiting-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 713 | `laravel-redis-integration-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 714 | `laravel-reverb-websockets-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 715 | `laravel-scout-searchable-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 716 | `laravel-security-hardening-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 717 | `laravel-service-providers-dependency-injection-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 718 | `laravel-services-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 719 | `laravel-social-media-oauth-token-lifecycle-management-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 720 | `laravel-socialite-oauth-integration-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 721 | `laravel-task-scheduling-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 722 | `laravel-telescope-debugging-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 723 | `laravel-trello-api-integration` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 724 | `laravel-typescript-transformer-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 725 | `laravel-user-impersonation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 726 | `laravel-vue-geocoordinates-maps-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 727 | `laravel-vue-login-maxauthcard-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 728 | `laravel-vuefinder-media-library-integration` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 729 | `laravel-whatsapp-cloud-api-integration` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 730 | `laravel-ziggy-routing-integration-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 731 | `lightning-architecture-review` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 732 | `linux-privilege-escalation` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 733 | `linux-shell-scripting` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 734 | `liuguang-banlan-ui` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 735 | `llm-application-dev-ai-assistant` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 736 | `llm-application-dev-prompt-optimize` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 737 | `logic-diff` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 738 | `logic-locate` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 739 | `longbridge` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 740 | `longbridge-market-data` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 741 | `lookdev-auto` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 742 | `lovable-cleanup` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 743 | `marketing-plan` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 744 | `mcp-builder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 745 | `metasploit-framework` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 746 | `mmx-cli` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 747 | `mock-hunter` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 748 | `molykit` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 749 | `monopoly` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 750 | `monorepo-architect` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 751 | `monte-carlo-analyze-root-cause` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 752 | `monte-carlo-performance-diagnosis` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 753 | `monte-carlo-remediation` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 754 | `multi-agent-patterns` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 755 | `n8n-expression-syntax` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 756 | `n8n-node-configuration` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 757 | `native-data-fetching` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 758 | `neon-ai-gateway` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 759 | `neon-functions` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 760 | `neon-object-storage` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 761 | `neon-postgres` | Excelente | 0 | PODAR | Conforme e aderente aos padrões de engenharia. |
| 762 | `nestjs-expert` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 763 | `network-101` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 764 | `notebooklm` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 765 | `obsidian-bases` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 766 | `obsidian-markdown` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 767 | `open-source-marketing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 768 | `paid-ads` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 769 | `pdf-conversion-router` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 770 | `pdf-official` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 771 | `pentest-commands` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 772 | `postman-newman-automation` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 773 | `privacy-mask` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 774 | `product-design` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 775 | `product-marketing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 776 | `production-code-audit` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 777 | `project-history` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 778 | `project-setup` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 779 | `pubmed-database` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 780 | `pytest-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 781 | `python-concessionarias-automation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 782 | `react-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 783 | `red-team-tools` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 784 | `redis-cli` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 785 | `referral-program` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 786 | `review-and-simplify-changes` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 787 | `revops` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 788 | `robot-framework-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 789 | `scanning-tools` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 790 | `sdk-dx` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 791 | `security-and-hardening` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 792 | `security-compliance-compliance-check` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 793 | `selenium-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 794 | `sendblue-api` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 795 | `senior-frontend` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 796 | `seo-aeo-blog-writer` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 797 | `seo-aeo-content-cluster` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 798 | `seo-aeo-content-quality-auditor` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 799 | `seo-aeo-internal-linking` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 800 | `seo-aeo-keyword-research` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 801 | `seo-aeo-landing-page-writer` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 802 | `seo-aeo-meta-description-generator` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 803 | `seo-competitor-pages` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 804 | `seo-hreflang` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 805 | `seo-images` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 806 | `seo-page` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 807 | `seo-plan` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 808 | `seo-programmatic` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 809 | `seo-sitemap` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 810 | `seo-technical` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 811 | `sharp-coder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 812 | `site-architecture` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 813 | `skill-creator` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 814 | `skill-improver` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 815 | `slack-bot-builder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 816 | `smartui-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 817 | `smtp-penetration-testing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 818 | `snowflake-development` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 819 | `social-content` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 820 | `social-orchestrator` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 821 | `socialclaw` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 822 | `source-driven-development` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 823 | `spec-to-code-compliance` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 824 | `ssh-penetration-testing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 825 | `stitch-ui-design` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 826 | `styleseed-design-review` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 827 | `supabase` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 828 | `systematic-debugging-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 829 | `technical-documentation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 830 | `telegram-bot-builder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 831 | `test-fixing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 832 | `test-framework-migration-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 833 | `threat-modeling-expert` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 834 | `tools-page-seo-optimizer` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 835 | `top-web-vulnerabilities` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 836 | `transformers-js` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 837 | `tune-monitor` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 838 | `typescript-advanced-types-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 839 | `typescript-billing-core-architecture-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 840 | `typescript-max-banks-efi-gateway-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 841 | `typescript-tooling-monorepo-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 842 | `ui-motion` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 843 | `uniprot-database` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 844 | `unslop-commit` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 845 | `unslop-file` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 846 | `usage-based-pricing` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 847 | `using-neon` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 848 | `variant-analysis` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 849 | `vector-database-engineer` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 850 | `vibecode-production-qa-validator` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 851 | `videodb` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 852 | `vitest-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 853 | `vue-auto-import-components-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 854 | `vue-boleto-utils-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 855 | `vue-brand-positioning-character-management-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 856 | `vue-complex-modal-forms-autosave-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 857 | `vue-dayjs-date-manipulation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 858 | `vue-debugging-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 859 | `vue-eslint-stylelint-quality-standards` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 860 | `vue-frontend-bug-fixing-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 861 | `vue-inputs-masks-validation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 862 | `vue-keyboard-shortcuts-navigation-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 863 | `vue-max-components-ui-popovers-confirmations-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 864 | `vue-max-ecosystem-api-reference` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 865 | `vue-max-stack-frontend-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 866 | `vue-max-use-development-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 867 | `vue-max-use-usecachedapi-state-cache-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 868 | `vue-meta-api-oauth-integration-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 869 | `vue-pinia-state-management-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 870 | `vue-rss-news-moderation-dashboard-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 871 | `vue-toast-notifications-toastify-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 872 | `vue-typescript-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 873 | `vue-vitest-testing-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 874 | `vue-whatsapp-interactive-messages-simulator-best-practices` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 875 | `web-media-getter` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 876 | `webdriverio-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 877 | `wiki-vitepress` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 878 | `wjttc-builder` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 879 | `wordpress-plugin-development` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 880 | `wordpress-theme-development` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |
| 881 | `yao-meta-skill` | Excelente | 0 | MANTER | Conforme e aderente aos padrões de engenharia. |

---

## 🛠️ Estrutura do Plano de Correção em 5 Etapas (Fase 6)

> ⛔ **PARADA OBRIGATÓRIA:** Nenhuma alteração em arquivos foi executada. O plano abaixo aguarda aprovação humana formal.

1. **Etapa 1 — Remoções + Merges (Tier 2):**
   - Nenhuma remoção destrutiva identificada como necessária.
   - Ajustes de demarcação (LAPIDAR/DEMARCAR) em pares de IA e Pinia.
2. **Etapa 2 — Críticas (Tier 2):**
   - Zero skills com arquitetura 100% inventada.
3. **Etapa 3 — Ruins (Tier 2):**
   - Correção de skills com 2 ou mais inconsistências técnicas.
4. **Etapa 4 — Regulares + Podas de Bloat (Tier 1 em Lotes):**
   - Correção da rota crua em `vue-axios-api-integration-best-practices` e podas de bloat.
5. **Etapa 5 — Boas (Tier 1 em Lotes):**
   - Ajuste e expansão das descriptions curtas (< 200 caracteres) das skills de terceiros e catálogo.