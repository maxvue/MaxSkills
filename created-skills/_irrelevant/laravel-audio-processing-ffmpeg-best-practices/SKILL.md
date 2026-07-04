---
name: laravel-audio-processing-ffmpeg-best-practices
description: Use when creating, modifying, or debugging audio conversion routines, utilizing FFMpeg via Symfony/Laravel Process component, handling audio files formats (Opus, AAC, OGG, MP3), or configuring execution timeouts and error logging for system processes.
---

# Boas Práticas de Processamento de Áudio com FFMpeg no Laravel

## Objetivo
Estabelecer diretrizes seguras, performáticas e confiáveis para executar rotinas de conversão e processamento de áudio via o binário FFMpeg usando o componente `Process` do Symfony/Laravel no backend do Engeapp.

## Instruções

### 1. Execução de Processos e Segurança de Comandos
- Sempre invoque o binário do FFMpeg usando `Symfony\Component\Process\Process`.
- Passe todos os argumentos de linha de comando como um array para o construtor do `Process`. O componente cuida automaticamente do escaping adequado e protege contra vulnerabilidades de command injection.
  ```php
  // BOM: parâmetros de comando escapados com segurança
  $process = new Process(['ffmpeg', '-i', $inputFile, '-c:a', 'aac', '-y', $outputFile]);
  
  // RUIM: vulnerável a command injection
  $process = Process::fromShellCommandline("ffmpeg -i {$inputFile} -c:a aac -y {$outputFile}");
  ```

### 2. Timeouts e Gerenciamento de Recursos
- Configure explicitamente timeouts de execução para as tarefas do FFMpeg usando `$process->setTimeout()`. Nunca confie em janelas de execução padrão ou infinitas.
- Defina um timeout padrão sensato (ex: `120` segundos) com base na duração esperada do áudio e nos recursos do sistema.
  ```php
  $process->setTimeout(120);
  ```

### 3. Tratamento de Erros e Logging
- Use `$process->mustRun()` quando a conversão de áudio for uma etapa obrigatória.
- Capture `Symfony\Component\Process\Exception\ProcessFailedException` para tratar erros do processo de forma elegante, sem causar falhas silenciosas ou quebrar os fluxos de execução.
- Registre as falhas usando o logging estruturado do Laravel (facade `Log`), incluindo o exit code, a saída de erro e os metadados de entrada/saída.
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

### 4. Codecs e Formatos de Áudio Padrão
- Use `-c:a aac` para converter ou comprimir áudio para o formato AAC.
- Use `-c:a libopus` para converter áudio para o formato OGG/Opus (ideal para gravações web).
- Use o parâmetro `-y` para sobrescrever o arquivo de saída caso ele já exista, evitando prompts de confirmação interativos.

### 5. Arquivos Temporários e Limpeza
- Garanta que quaisquer arquivos temporários criados durante o processamento ou conversão sejam limpos em um bloco `finally` ou em uma rotina de pós-processamento, para evitar vazamentos de disco e problemas de armazenamento.

---

## Restrições
- **Idioma:** Sempre se comunique com o usuário humano em Português (pt-BR). Este é o idioma padrão de conversação Agente↔Humano, sempre, sem exceção — independentemente do idioma em que o conteúdo/corpo desta skill está escrito.
- **Não** use funções nativas de execução de shell do PHP, como `exec()`, `shell_exec()`, `system()` ou `passthru()`.
- **Não** concatene variáveis diretamente em strings de execução de linha de comando.
- **Não** omita a configuração de timeout do processo.
- **Não** use wrappers PHP complexos (ex: `php-ffmpeg/php-ffmpeg`) a menos que explicitamente necessário. Interagir diretamente com o componente nativo `Process` do Symfony é preferível.
