---
name: adonisjs-drive-file-uploads-best-practices
description: Use when implementing, reviewing, or debugging file uploads, storage disks config, image manipulation, or media delivery in AdonisJS using @adonisjs/drive, sharp, or other file processing libraries. Triggers on multipart request handling, drive disk setup, file validations (size, mime types), and media processing.
---

## Objetivo
Estabelecer padrões robustos, seguros e portáveis para nuvem para uploads de arquivos, configuração de discos de armazenamento, processamento de mídias (usando Sharp) e entrega segura de arquivos no AdonisJS v6.

## Instruções

## 1. Instalação e Configuração
Para lidar com uploads de arquivos de forma nativa no AdonisJS v6 entre múltiplos provedores de armazenamento, prefira sempre o pacote oficial `@adonisjs/drive`.

### Instalação
```bash
node ace add @adonisjs/drive
```

### Configuração (`config/drive.ts`)
Sempre configure um disco local (`fs`) para desenvolvimento/testes e um disco em nuvem (como `s3` ou `gcs`) para ambientes de produção.
```typescript
import { defineConfig, services } from '@adonisjs/drive'
import env from '#start/env'

const driveConfig = defineConfig({
  default: env.get('DRIVE_DISK'),
  disks: {
    fs: services.fs({
      location: 'tmp/uploads',
      visibility: 'public',
    }),
    s3: services.s3({
      credentials: {
        accessKeyId: env.get('S3_KEY')!,
        secretAccessKey: env.get('S3_SECRET')!,
      },
      region: env.get('S3_REGION')!,
      bucket: env.get('S3_BUCKET')!,
      visibility: 'public',
    }),
  },
})

export default driveConfig
```

Certifique-se de que as variáveis de ambiente sejam validadas em `start/env.ts`:
```typescript
DRIVE_DISK: Env.schema.enum(['fs', 's3'] as const),
S3_KEY: Env.schema.string.optional({ format: 'any' }),
S3_SECRET: Env.schema.string.optional({ format: 'any' }),
S3_REGION: Env.schema.string.optional({ format: 'any' }),
S3_BUCKET: Env.schema.string.optional({ format: 'any' }),
```

---

## 2. Validação de Arquivo (VineJS)
Sempre valide os arquivos recebidos usando schemas do VineJS em vez de verificar propriedades manualmente no controller.

```typescript
import vine from '@vinejs/vine'

export const uploadAvatarValidator = vine.compile(
  vine.object({
    avatar: vine.file({
      size: '2mb',
      extnames: ['jpg', 'jpeg', 'png', 'webp'],
    })
  })
)
```

---

## 3. Uploads Padrão (`moveToDisk`)
Para arquivos que não exigem processamento (ex: PDFs, ZIPs, anexos brutos), utilize o método nativo `moveToDisk` na instância de `MultipartFile`. Isso move o arquivo diretamente para o disco padrão do drive configurado.

```typescript
import { HttpContext } from '@adonisjs/core/http'
import { cuid } from '@adonisjs/core/helpers'
import { uploadAvatarValidator } from '#validators/avatar'

export default class UploadsController {
  async store({ request, response }: HttpContext) {
    const { avatar } = await request.validateUsing(uploadAvatarValidator)
    
    // Gera um nome de arquivo seguro e único usando cuid()
    const fileName = `${cuid()}.${avatar.extname}`
    
    // Move o arquivo para o bucket/diretório do disco padrão
    await avatar.moveToDisk('avatars', { name: fileName })
    
    return response.ok({
      path: `avatars/${fileName}`
    })
  }
}
```

---

## 4. Processamento e Compressão de Imagem com Sharp
Ao fazer upload de imagens (como avatares de perfil ou anexos de posts), processe e comprima-as para economizar espaço de armazenamento e largura de banda.

### Fluxo de Trabalho:
1. Valide o payload do arquivo.
2. Leia o arquivo bruto a partir de `file.tmpPath`.
3. Processe-o usando o `sharp` (redimensionamento, conversão de formato, compressão).
4. Exporte como um `Buffer` (ou `ReadableStream`).
5. Grave diretamente no serviço de drive usando `drive.use().put(key, buffer)`.

### Exemplo de Código:
```typescript
import { HttpContext } from '@adonisjs/core/http'
import { cuid } from '@adonisjs/core/helpers'
import drive from '@adonisjs/drive/services/main'
import sharp from 'sharp'
import { uploadAvatarValidator } from '#validators/avatar'

export default class AvatarController {
  async update({ request, response, auth }: HttpContext) {
    const { avatar } = await request.validateUsing(uploadAvatarValidator)
    const user = auth.user!

    // 1. Processa a imagem usando Sharp a partir do tmpPath
    const processedBuffer = await sharp(avatar.tmpPath)
      .resize({ width: 400, height: 400, fit: 'cover' })
      .webp({ quality: 80 }) // Converte e comprime para webp
      .toBuffer()

    const key = `avatars/${user.id}/${cuid()}.webp`

    // 2. Faz o upload do buffer processado diretamente para o Drive
    await drive.use().put(key, processedBuffer, {
      contentType: 'image/webp',
    })

    // 3. Opcional: Deleta o avatar antigo do armazenamento se ele existir.
    //    A coluna armazena a KEY de storage (não uma URL), por isso pode ser
    //    passada diretamente para drive.delete().
    if (user.avatarKey) {
      await drive.use().delete(user.avatarKey)
    }

    // 4. Atualiza o perfil do usuário armazenando a KEY de storage.
    //    A URL é derivada sob demanda via getUrl(avatarKey) (veja a seção 5).
    await user.merge({ avatarKey: key }).save()

    return response.ok({ path: key })
  }
}
```

---

## 5. Entrega de Arquivos: URLs Públicas vs Privadas
No banco de dados, armazene sempre a KEY de storage (ex: `avatarKey`), nunca uma URL completa. A URL é derivada sob demanda a partir da key:
- **Ativos Públicos:** Se o disco estiver configurado como `visibility: 'public'`, resolva as URLs usando `drive.use().getUrl(avatarKey)`.
- **Ativos Privados/Protegidos:** Se os arquivos só devem ser acessados por usuários autorizados (ex: faturas, contratos), configure o armazenamento privado e gere URLs assinadas usando `drive.use().getSignedUrl(avatarKey, { expiresIn: '30m' })`.

```typescript
import drive from '@adonisjs/drive/services/main'

// URL Pública derivada da key armazenada (user.avatarKey)
const publicUrl = await drive.use().getUrl(user.avatarKey)

// URL Assinada temporária para documentos privados
const invoiceUrl = await drive.use().getSignedUrl('invoices/inv-2026.pdf', {
  expiresIn: '15m'
})
```

---

## Restrições
- **Nunca** grave arquivos diretamente na pasta pública usando `app.publicPath()` ou a API padrão `fs/promises` em produção. Sempre direcione os uploads através do `@adonisjs/drive` para manter a portabilidade para a nuvem.
- **Nunca** use `moveToDisk()` em um `MultipartFile` após tê-lo modificado com o `sharp`. Uma vez que uma imagem é processada em um buffer/stream, você deve fazer o upload usando `drive.use().put()`.
- **Nunca** exponha credenciais de armazenamento, chaves S3, regiões ou nomes de buckets diretamente nos arquivos de código. Sempre recupere-os via `env.get()` e valide-os em `start/env.ts`.
- **Evite** usar os nomes de arquivo enviados pelo cliente (`file.clientName`) diretamente no disco. Sempre sanitize ou renomeie os arquivos usando `cuid()` ou `ulid()` para evitar vulnerabilidades de path traversal.
