---
name: vue-image-cropping-resizing-best-practices
description: Use when creating, modifying, reviewing, or styling image cropping, resizing, or upload preview components in Vue 3 (EngeApp) for formatting fotos de projetos/instalações fotovoltaicas (ex.: fotos de telhado, módulos, datasheets) com proporções comuns (1:1, 4:3, 16:9). Triggers on Cropper.js integration, canvas data manipulation, or client-side image compression before upload.
---

## Objetivo
Fornecer boas práticas, detalhes de implementação e restrições para o recorte e redimensionamento de imagens no lado do cliente dentro de componentes Vue 3, visando o domínio fotovoltaico/solar do EngeApp (ex.: fotos de instalações, telhados, módulos e documentos), usando Cropper.js e Compressor.js, aproveitando também os pacotes locais MaxComponentsUi, MaxUse e MaxPinia.

## Instruções

1. **Arquitetura e Composition API**:
   - Implemente componentes de recorte utilizando Single-File Components (SFC) do Vue 3 com `<script setup lang="ts">`.
   - Respeite a ordem dos blocos: `<template>`, `<script>` e depois `<style lang="scss" scoped>`.
   - Mantenha todos os comentários do código em português do Brasil (`pt-BR`).
   - Formate os elementos do template mantendo os atributos na mesma linha (inline), evitando quebras de tag multilinha.

2. **Integração com o Cropper.js**:
   - Inicialize o Cropper.js dentro do hook `onMounted` e certifique-se de destruí-lo no hook `onBeforeUnmount` para evitar vazamentos de memória.
   - Use uma referência (`ref`) no elemento `<img>` em vez de selecioná-lo diretamente via query DOM.
   - Configuração de exemplo para o Cropper:
     ```ts
     import Cropper from 'cropperjs';
     import 'cropperjs/dist/cropper.css';

     // Dentro do componente
     const cropper = ref<Cropper | null>(null);
     const imageRef = ref<HTMLImageElement | null>(null);

     const initCropper = () => {
       if (!imageRef.value) return;
       cropper.value = new Cropper(imageRef.value, {
         aspectRatio: 1, // Padrão ou reativo com base nas proporções (1:1, 4:3, 16:9)
         viewMode: 1,
         dragMode: 'move',
         autoCropArea: 1,
         restore: false,
         guides: true,
         center: true,
         highlight: false,
         cropBoxMovable: true,
         cropBoxResizable: true,
         toggleDragModeOnDblclick: false,
       });
     };
     ```

3. **Proporções de Tela (Aspect Ratios)**:
   - Proporções comuns para fotos de projetos fotovoltaicos:
     - Quadrado (Square): `1` (1:1) — miniaturas/avatares de equipamento
     - Paisagem (Landscape): `4 / 3` (~1.333) — fotos de telhado/instalação
     - Widescreen: `16 / 9` (~1.777) — capas e galerias
   - Certifique-se de que a interface do usuário permita selecionar estas proporções, atualizando dinamicamente a propriedade correspondente no cropper:
     ```ts
     const changeAspectRatio = (ratio: number) => {
       if (cropper.value) {
         cropper.value.setAspectRatio(ratio);
       }
     };
     ```

4. **Manipulação de Canvas e Exportação de Alta Qualidade**:
   - Obtenha o canvas recortado com a resolução recomendada para evitar imagens borradas:
     - Quadrado (1:1): `1080x1080`
     - Paisagem (4:3): `1440x1080`
     - Widescreen (16:9): `1920x1080`
   - Utilize a função `cropper.getCroppedCanvas()` passando opções personalizadas de largura e altura.
   - Converta os dados do canvas para um arquivo (`File`) ou `Blob` para fins de upload:
     ```ts
     const getCroppedImageBlob = (): Promise<Blob | null> => {
       return new Promise((resolve) => {
         if (!cropper.value) return resolve(null);
         const canvas = cropper.value.getCroppedCanvas({
           width: targetWidth, // Ex: 1440
           height: targetHeight, // Ex: 1080 (4:3)
           imageSmoothingEnabled: true,
           imageSmoothingQuality: 'high',
         });
         canvas.toBlob((blob) => resolve(blob), 'image/jpeg', 0.9); // JPEG com 90% de qualidade
       });
     };
     ```

5. **Compressão no Lado do Cliente**:
   - Implemente a compressão de imagem no cliente antes de realizar o upload, usando `Compressor.js` ou os parâmetros de exportação do próprio canvas, garantindo que o arquivo final não exceda limites de rede razoáveis (ex: máximo de 5MB).
   - Use a função utilitária `formatBytes` de `@maxvue/max-use/format` para exibir amigavelmente o tamanho final do arquivo.

6. **Persistência via MaxPinia (obrigatório)**:
   - NÃO faça upload manual avulso (ex.: `axios.post` direto). Após gerar o `Blob`/`File` recortado, encaminhe a persistência através de uma store `@maxvue/max-pinia`, que cuida do salvamento automático (auto-save/debounced) no backend Adonis.
   - As rotas são CAMINHOS STRING `/api/...` resolvidos por `apiPostRoute` de `@maxvue/max-use` (não há `route()`/Ziggy).
   - Exemplo do fluxo de persistência:
     ```ts
     import { useProjectPhotosStore } from '@/stores/projectPhotos';

     const photosStore = useProjectPhotosStore();

     const salvarFotoRecortada = async () => {
       const blob = await getCroppedImageBlob();
       if (!blob) return;
       // A store envia o arquivo via apiPostRoute('/api/...') e gerencia o auto-save.
       await photosStore.uploadPhoto(blob);
     };
     ```

7. **Integração de Interface (UI)**:
   - Envolva o componente de recorte em um overlay `MaxModal` para exibição em janela modal.
   - Use `MaxButton` para as ações do usuário (ex: Recortar, Redefinir, Cancelar) definindo os respectivos severities (ex: `severity="primary"`, `severity="secondary"`).
   - Os componentes `@maxvue` (`MaxModal`, `MaxButton`, etc.) são auto-importados via `unplugin-vue-components` — NÃO faça import manual deles no `<script setup>`.
   - Aplique micro-animações suaves e efeitos de hover nos botões e controles para uma experiência premium.

## Restrições
- **PROIBIDO o uso da Options API**: Não utilize de forma alguma a estrutura clássica de options do Vue (`data`, `methods`, etc.). Toda a lógica de estado e funções deve ser construída na `<script setup lang="ts">`.
- **PROIBIDO o uso de Tailwind CSS**: Evite utilizar classes utilitárias do Tailwind CSS, a menos que solicitado expressamente pelo usuário. Utilize regras de SCSS com escopo fechado (`scoped`).
- **PROIBIDO manipulação direta do DOM por seletores**: Nunca utilize seletores globais como `document.getElementById` ou `document.querySelector` para obter a imagem. Utilize referências de template do Vue (`ref="imageRef"`).
- **Gerenciamento e Limpeza**: Sempre destrua a instância do Cropper no hook `onBeforeUnmount` para evitar vazamentos de memória e manter a performance da aplicação.
- **Comentários em pt-BR**: Todos os comentários no código dentro dos componentes Vue DEVEM ser redigidos em Português do Brasil.
- **Atributos Inline**: Garanta que todas as propriedades e atributos das tags HTML e componentes no template sejam declarados em uma única linha (sem quebrar atributos em várias linhas).
