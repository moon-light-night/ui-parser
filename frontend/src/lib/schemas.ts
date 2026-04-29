import { z } from 'zod';
import { 
    ALLOWED_IMAGE_TYPES, 
    MAX_CHAT_MESSAGE_LENGTH, 
    MAX_FILE_SIZE_BYTES, 
    MAX_TITLE_LENGTH 
} from './constants';

export const screenshotTitleSchema = z
  .string()
  .max(MAX_TITLE_LENGTH, `Название не должно превышать ${MAX_TITLE_LENGTH} символов`)
  .optional()
  .or(z.literal(''));

export const imageFileSchema = z
  .any()
  .superRefine((v, ctx) => {
    const isFilelike =
      v !== null &&
      v !== undefined &&
      typeof v === 'object' &&
      typeof (v as File).name === 'string' &&
      typeof (v as File).size === 'number' &&
      typeof (v as File).type === 'string';

    if (!isFilelike) {
      ctx.addIssue({ code: 'custom', message: 'Выберите файл' });
      return;
    }

    const f = v as File;

    if (!ALLOWED_IMAGE_TYPES.includes(f.type as (typeof ALLOWED_IMAGE_TYPES)[number])) {
      ctx.addIssue({
        code: 'custom',
        message: `Неподдерживаемый тип файла: ${f.type}. Разрешены: JPEG, PNG, GIF, WebP.`,
      });
    }

    if (f.size > MAX_FILE_SIZE_BYTES) {
      ctx.addIssue({
        code: 'custom',
        message: `Файл слишком большой: ${(f.size / 1024 / 1024).toFixed(1)} МБ. Максимум 20 МБ.`,
      });
    }
  });

export const uploadFormSchema = z.object({
  file: imageFileSchema,
  title: screenshotTitleSchema,
});

export type UploadFormValues = z.infer<typeof uploadFormSchema>;


export const chatMessageSchema = z.object({
  message: z
    .string()
    .min(1, 'Сообщение не может быть пустым')
    .max(
      MAX_CHAT_MESSAGE_LENGTH,
      `Сообщение не должно превышать ${MAX_CHAT_MESSAGE_LENGTH} символов`,
    )
    .refine((s) => s.trim().length > 0, 'Сообщение не может состоять только из пробелов'),
});

export type ChatMessageValues = z.infer<typeof chatMessageSchema>;
