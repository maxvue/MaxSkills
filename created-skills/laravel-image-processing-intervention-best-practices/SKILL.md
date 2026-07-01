---
name: laravel-image-processing-intervention-best-practices
description: Use when manipulating, processing, resizing, scaling, or optimizing images using the Intervention Image v3 library in the Laravel backend. Triggers on ImageManager usage, image uploads processing, watermark application, format conversion, and responsive image generation.
---

# Laravel Image Processing with Intervention Image v3 Best Practices

## Goal
Provide solid, standardized guidelines for manipulating, resizing, optimizing, and converting images using the Intervention Image v3 library in the Laravel backend of Engeapp.

## Instructions
1. **Driver Instantiation**:
   Always instantiate the `ImageManager` by passing the driver explicitly to the constructor (prefer `Gd` as default in the application, or `Imagick` if advanced operations like complex formats are needed):
   ```php
   use Intervention\Image\ImageManager;
   use Intervention\Image\Drivers\Gd\Driver;

   $manager = new ImageManager(new Driver());
   ```

2. **Reading Images**:
   Use `$manager->read()` to read images from file paths, binary data, GD resources, or UploadedFile instances:
   ```php
   $image = $manager->read($uploadedFile);
   ```

3. **Resizing and Scaling**:
   - **Proportional Scaling**: Use `$image->scale(width: 800, height: 600)` to scale the image proportionally. Omit one dimension to scale dynamically relative to the other.
   - **Limit Downscaling**: Use `$image->scaleDown(width: 1024)` to scale down only if the image is larger than the specified limit, preventing upscaling of small images.
   - **Cover / Crop**: Use `$image->cover(width: 300, height: 300)` for cropping and resizing to exactly fit dimensions.

4. **Format Conversion and Quality Optimization**:
   - Convert images to modern formats like WebP or AVIF for optimal file sizes:
     ```php
     $webp = $image->toWebp(quality: 80);
     $jpeg = $image->toJpeg(quality: 75);
     ```
   - Save directly: `$image->save($path);` (preserves format unless converted).
   - Get raw string: `$rawData = $image->toWebp()->toString();`.

5. **Octane Compatibility**:
   - Do not store `ImageManager` or raw `Image` instances in static properties or as global singletons, as this can lead to memory accumulation.
   - Release references as soon as the image processing is finished.

6. **Error Handling**:
   - Always wrap image operations in a `try-catch` block to handle exceptions like missing files, corrupted data, or unsupported formats:
     ```php
     use Intervention\Image\Exceptions\ReadException;
     use Intervention\Image\Exceptions\DecoderException;

     try {
         $image = $manager->read($path);
     } catch (ReadException | DecoderException $e) {
         Log::error('Failed to read image: ' . $e->getMessage());
     }
     ```

7. **Asynchronous Processing**:
   - Delegate heavy image manipulation tasks (like batch uploads or high-resolution photo resizing) to background queue jobs utilizing the `ShouldQueue` contract.

## Constraints
- **Do NOT** use the old static class calls (`Image::make()`), which belong to Intervention Image v2.
- **Do NOT** use the old resizing methods like `resize(300, null, function ($constraint) { $constraint->aspectRatio(); })`. Use the modern `scale(width: 300)` instead.
- **Do NOT** store processed image instances in memory across requests in Octane environments.
