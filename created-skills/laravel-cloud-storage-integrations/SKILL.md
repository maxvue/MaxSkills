---
name: laravel-cloud-storage-integrations
description: Use when configuring, implementing, or debugging cloud storage integrations in Laravel. Triggers on Storage facade calls, disk configuration, file uploads, pre-signed URLs, WebDAV file streams, and AWS S3/MinIO/Cloudflare R2/WebDAV setups.
---

# Laravel Cloud Storage Integrations Best Practices

## Goal
Provide solid guidelines, consistent patterns, and architectural standards for configuring, integrating, testing, and maintaining cloud storage (AWS S3, MinIO, Cloudflare R2, and WebDAV servers like Nextcloud/ownCloud/Seafile) securely and scalably within Laravel.

## Instructions

### 1. Configuration (config/filesystems.php)
* **S3/MinIO/R2:** Use Laravel's native `s3` driver. Leverage environment variables. For local MinIO, `AWS_USE_PATH_STYLE_ENDPOINT` must be `true`. For Cloudflare R2, set it to `false`.
* **WebDAV:** Configure connection parameters (URL, username, password). Register a custom driver in a Service Provider using `league/flysystem-webdav` and `Sabre\DAV\Client`, wrapping it into `Storage::extend('webdav', ...)`.

### 2. Processing Large Files & Streams
* **Never** read entire large files into PHP memory using `file_get_contents()` or `Storage::get()`.
* **Uploads:** Use `Storage::disk('s3')->putFile()` or stream resources (`Storage::disk('webdav')->writeStream('path', $localStream)`).
* **Downloads:** Stream remote files to local files using `Storage::disk('disk')->readStream()`.

### 3. Remote Path Incompatibility
* Remote drivers like WebDAV do not map to local file paths. `Storage::disk('webdav')->path()` will throw an exception.
* If local paths are required (e.g., for PDF generation), download the file locally to a temp directory, process it, and clean up afterwards.

### 4. File Security and Pre-signed URLs (S3)
* Keep all buckets and files private by default.
* Generate temporary, pre-signed URLs (`Storage::disk('s3')->temporaryUrl()`) when granting access to sensitive documents.

### 5. Exception Handling, Logging & Testing
* **Resilience:** Network failures and timeouts are common. Wrap storage operations in try-catch blocks and log descriptive error contexts.
* **Testing:** Never make real HTTP calls to external storage providers during test suite runs. Always use `Storage::fake('s3')` or equivalent to mock the disk.

### 6. Spatie Media Library Integration
* Define the correct target disk directly inside your model's media collections registration (`->useDisk('s3')` or `->useDisk('webdav')`).

## Constraints
* **NO Credentials in Version Control:** Never hardcode AWS/WebDAV keys or credentials. Use `env()` or `config()`.
* **NO Production Local Storage for User Files:** Do not store user-uploaded assets on `local` or `public` disks. Target a cloud disk.
* **NO Real Network Calls in Tests:** Mock the filesystem with `Storage::fake()`.
* **NEVER call `Storage::disk('webdav')->path()`:** Use local temporary file resolution via streams.
* **NEVER load entire large files into memory:** Always implement `readStream()` and `writeStream()`.
