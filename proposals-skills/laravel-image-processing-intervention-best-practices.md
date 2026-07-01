# PROPOSTA DE SKILL: laravel-image-processing-intervention-best-practices

* **Tipo de proposta:** CRIAR
* **Nível da Skill:** 1
* **Wake Word (YAML Description):** Use when manipulating, processing, resizing, scaling, or optimizing images using the Intervention Image v3 library in the Laravel backend. Triggers on ImageManager usage, image uploads processing, watermark application, format conversion, and responsive image generation.
* **Estrutura de Diretórios:** Apenas SKILL.md (Nível 1).
* **Necessidade:** O Engeapp realiza processamentos de imagem em Helpers (ex: `resizeImage` em `FilesHelpers`) e ferramentas de automação (ex: `BrowserTakeScreenshot`). O uso do Intervention Image v3 exige drivers específicos (como Gd ou Imagick) e métodos atualizados da API v3 (como `scale()`, `cover()`, etc.), demandando padrões de reuso para evitar vazamento de memória e processamento ineficiente no ciclo de vida Octane.
* **Recursos:** Configuração correta de drivers Gd/Imagick na v3, redimensionamento escalável e proporcional, conversão automática para formatos modernos e otimizados (WebP, AVIF), aplicação segura de marcas d'água (watermarks), otimização de qualidade de compressão, e delegação de processamento pesado em segundo plano usando filas.
* **Objetivo:** Fornecer diretrizes sólidas e padronizadas para manipulação de imagens utilizando a API atualizada da biblioteca Intervention Image v3 no backend Laravel do Engeapp.
* **Casos de uso:** Redimensionamento de capturas de tela tiradas por automações de navegador, otimização de anexos e mídias enviadas por usuários, geração e aplicação de assinaturas em imagens, e criação de thumbnails dinâmicos.
* **Workflows:**
  - bug-fix-back-end
* **Skills próprias utilizadas:**
  - `laravel-jobs-queues-horizon-best-practices` — Utilizará as regras de filas para o processamento assíncrono de lote de imagens.
  - `laravel-exception-handling-logging` — Utilizará o tratamento centralizado para falhas de formato não suportado ou imagens corrompidas.
  - `laravel-media-library-best-practices` — Cooperará com as coleções de mídia do Spatie para aplicar conversões customizadas eficientes.
* **Skills auxiliares:** laravel-specialist, laravel-best-practices
* **Skills beneficiadas:** Nenhuma no momento.
* **Benefícios:** Melhoria de desempenho na renderização de imagens no frontend, economia de armazenamento e banda (conversão para WebP/AVIF), prevenção de estouro de memória no servidor Octane, e código limpo e padronizado na manipulação de mídias.
