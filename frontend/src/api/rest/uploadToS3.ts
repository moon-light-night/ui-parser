import { httpClient } from '@/api/rest/httpClient';

/**
 * Загружает файл напрямую в S3 хранилище через presigned URL.
 * @param url       presigned URL, от RPC CreateUploadUrl
 * @param file      Объект File для загрузки
 * @param onProgress Опциональный колбэк с прогрессом загрузки
 */
export async function uploadToS3(
  url: string,
  file: File,
  onProgress?: (percent: number) => void,
): Promise<void> {
  await httpClient.put(url, file, {
    headers: { 'Content-Type': file.type },
    onUploadProgress: (e) => {
      if (e.total && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
    },
  });
}
