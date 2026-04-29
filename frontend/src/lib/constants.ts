/** Локаль для форматирования всех дат/времени в приложении */
export const LOCALE = 'ru-RU';

/** Максимальное количество скриншотов в одном запросе */
export const PAGE_SIZE_SCREENSHOTS = 50;

/** Максимальное количество сессий в одном запросе */
export const PAGE_SIZE_SESSIONS = 50;

/** Максимальное количество сообщений в одном запросе списка */
export const PAGE_SIZE_MESSAGES = 200;

/** Задержка (мс) между успешной загрузкой и закрытием диалога */
export const UPLOAD_SUCCESS_DELAY_MS = 0;

/** Поддерживаемые форматы загружаемых изображений */
export const ALLOWED_IMAGE_TYPES = [
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
] as const;

/** Максимальный размер загружаемого файла (байты) */
export const MAX_FILE_SIZE_BYTES = 20 * 1024 * 1024; // 20 МБ

/** Максимальная длина заголовка скриншота */
export const MAX_TITLE_LENGTH = 200;

/** Максимальная длина сообщения в чате */
export const MAX_CHAT_MESSAGE_LENGTH = 8_000;