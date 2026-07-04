---
name: laravel-audio-processing-ffmpeg-best-practices
description: Use when creating, modifying, or debugging audio conversion routines, utilizing FFMpeg via Symfony/Laravel Process component, handling audio files formats (Opus, AAC, OGG, MP3), or configuring execution timeouts and error logging for system processes.
---

# Laravel Audio Processing with FFMpeg Best Practices

## Goal
Establish secure, performant, and reliable guidelines for executing audio conversion and processing routines via the FFMpeg binary using the Symfony/Laravel `Process` component in the Engeapp backend.

## Instructions

### 1. Process Execution and Command Security
- Always invoke the FFMpeg binary using `Symfony\Component\Process\Process`.
- Pass all command-line arguments as an array to the `Process` constructor. The component automatically handles proper escaping and guards against command injection vulnerabilities.
  ```php
  // GOOD: Safely escaped command parameters
  $process = new Process(['ffmpeg', '-i', $inputFile, '-c:a', 'aac', '-y', $outputFile]);
  
  // BAD: Vulnerable to command injection
  $process = Process::fromShellCommandline("ffmpeg -i {$inputFile} -c:a aac -y {$outputFile}");
  ```

### 2. Timeouts and Resource Management
- Explicitly configure execution timeouts for FFMpeg tasks using `$process->setTimeout()`. Never rely on default or infinite execution windows.
- Set a sensible default timeout (e.g., `120` seconds) based on the expected audio length and system resources.
  ```php
  $process->setTimeout(120);
  ```

### 3. Error Handling and Logging
- Use `$process->mustRun()` when the audio conversion is a mandatory step.
- Catch `Symfony\Component\Process\Exception\ProcessFailedException` to handle process errors gracefully without causing silent failures or breaking execution flows.
- Log failures using Laravel's structured logging (`Log` facade) including the exit code, error output, and input/output metadata.
  ```php
  try {
      $process->mustRun();
  } catch (ProcessFailedException $exception) {
      Log::error('Audio conversion failed', [
          'input' => $inputFile,
          'output' => $outputFile,
          'error' => $exception->getMessage(),
          'exit_code' => $process->getExitCode(),
      ]);
      return null;
  }
  ```

### 4. Codecs and Standard Audio Formats
- Use `-c:a aac` to convert or compress audio to the AAC format.
- Use `-c:a libopus` to convert audio to the OGG/Opus format (ideal for web recordings).
- Use the `-y` parameter to overwrite the output file if it already exists, avoiding interactive confirmation prompts.

### 5. Temporary Files and Cleanup
- Ensure that any temporary files created during processing or conversion are cleaned up in a `finally` block or post-processing routine to avoid disk leaks and storage issues.

---

## Constraints
- **Language:** Always communicate with the human user in Portuguese (pt-BR). This is the default Agent↔Human conversation language, always, without exception — regardless of the language this skill's own content/body is written in.
- **Do not** use native PHP shell execution functions such as `exec()`, `shell_exec()`, `system()`, or `passthru()`.
- **Do not** concatenate variables directly into command-line execution strings.
- **Do not** omit the process timeout configuration.
- **Do not** use complex PHP wrappers (e.g., `php-ffmpeg/php-ffmpeg`) unless explicitly required. Interacting with the native Symfony `Process` component directly is preferred.
