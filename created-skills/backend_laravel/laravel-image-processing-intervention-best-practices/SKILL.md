---
name: laravel-image-processing-intervention-best-practices
description: Use when manipulating, processing, resizing, scaling, or optimizing images using the Intervention Image v3 library in the Laravel backend. Triggers on ImageManager usage, image uploads processing, watermark application, format conversion, and responsive image generation.
---

# Boas Práticas de Processamento de Imagens no Laravel com Intervention Image v3

## Objetivo
Fornecer diretrizes sólidas e padronizadas para manipular, redimensionar, otimizar e converter imagens usando a biblioteca Intervention Image v3 no backend Laravel do Engeapp.

## Instruções
1. **Instanciação do Driver**:
   Sempre instancie o `ImageManager` passando o driver explicitamente para o construtor (prefira `Gd` como padrão na aplicação, ou `Imagick` se operações avançadas como formatos complexos forem necessárias):
   ```php
   use Intervention\Image\ImageManager;
   use Intervention\Image\Drivers\Gd\Driver;

   $manager = new ImageManager(new Driver());
   ```

2. **Leitura de Imagens**:
   Use `$manager->read()` para ler imagens a partir de caminhos de arquivo, dados binários, recursos GD ou instâncias de UploadedFile:
   ```php
   $image = $manager->read($uploadedFile);
   ```

3. **Redimensionamento e Escala**:
   - **Escala Proporcional**: Use `$image->scale(width: 800, height: 600)` para escalar a imagem proporcionalmente. Omita uma dimensão para escalar dinamicamente em relação à outra.
   - **Limitar Redução**: Use `$image->scaleDown(width: 1024)` para reduzir a escala apenas se a imagem for maior que o limite especificado, evitando o aumento de escala de imagens pequenas.
   - **Cover / Crop**: Use `$image->cover(width: 300, height: 300)` para recortar e redimensionar de modo a caber exatamente nas dimensões.

4. **Conversão de Formato e Otimização de Qualidade**:
   - Converta imagens para formatos modernos como WebP ou AVIF para obter tamanhos de arquivo ótimos:
     ```php
     $webp = $image->toWebp(quality: 80);
     $jpeg = $image->toJpeg(quality: 75);
     ```
   - Salve diretamente: `$image->save($path);` (preserva o formato a menos que convertido).
   - Obtenha a string bruta: `$rawData = $image->toWebp()->toString();`.

5. **Compatibilidade com Octane**:
   - Não armazene instâncias de `ImageManager` ou de `Image` bruta em propriedades estáticas ou como singletons globais, pois isso pode levar ao acúmulo de memória.
   - Libere as referências assim que o processamento da imagem terminar.

6. **Tratamento de Erros**:
   - Sempre envolva as operações de imagem em um bloco `try-catch` para tratar exceções como arquivos ausentes, dados corrompidos ou formatos não suportados:
     ```php
     use Intervention\Image\Exceptions\DecoderException;
     use Intervention\Image\Exceptions\RuntimeException;

     // OBS: intervention/image v3 não possui `ReadException`. Falhas de decode/read
     // aparecem como DecoderException; falhas de I/O como RuntimeException.
     try {
         $image = $manager->read($path);
     } catch (DecoderException | RuntimeException $e) {
         Log::error('Failed to read image: ' . $e->getMessage());
     }
     ```

7. **Processamento Assíncrono**:
   - Delegue tarefas pesadas de manipulação de imagem (como uploads em lote ou redimensionamento de fotos de alta resolução) para jobs de fila em background utilizando o contrato `ShouldQueue`.

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **NÃO** use as antigas chamadas de classe estática (`Image::make()`), que pertencem ao Intervention Image v2.
- **NÃO** use os antigos métodos de redimensionamento como `resize(300, null, function ($constraint) { $constraint->aspectRatio(); })`. Use o moderno `scale(width: 300)` em vez disso.
- **NÃO** armazene instâncias de imagem processadas em memória entre requisições em ambientes Octane.
