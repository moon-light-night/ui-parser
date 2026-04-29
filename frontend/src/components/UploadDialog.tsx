import { useState, useRef } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2, Upload, ImageIcon, FolderOpen } from 'lucide-react';
import { screenshotApi, s3Api } from '@/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Progress } from '@/components/ui/progress';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { ALLOWED_IMAGE_TYPES, UPLOAD_SUCCESS_DELAY_MS } from '@/lib/constants';
import {
  uploadFormSchema,
  imageFileSchema,
  type UploadFormValues,
} from '@/lib/schemas';

interface Props {
  onClose: () => void;
  onUploaded: () => void;
}

const UploadStep = {
  SELECT:      'select',
  UPLOADING:   'uploading',
  REGISTERING: 'registering',
  DONE:        'done',
} as const;
type UploadStep = (typeof UploadStep)[keyof typeof UploadStep];

export default function UploadDialog({ onClose, onUploaded }: Props) {
  const [step, setStep] = useState<UploadStep>(UploadStep.SELECT);
  const [progress, setProgress] = useState(0);
  const [previewFile, setPreviewFile] = useState<File | null>(null);

  const inputRef = useRef<HTMLInputElement>(null);

  const {
    register,
    handleSubmit,
    setValue,
    setError,
    clearErrors,
    formState: { errors, isSubmitting },
  } = useForm<UploadFormValues>({
    resolver: zodResolver(uploadFormSchema),
    mode: 'onChange',
    defaultValues: { title: '' },
  });

  const isUploading = isSubmitting || step === UploadStep.UPLOADING || step === UploadStep.REGISTERING;

  const handleFile = (f: File) => {
    setPreviewFile(f);
    const result = imageFileSchema.safeParse(f);
    if (!result.success) {
      setError('file', { message: result.error.issues[0]?.message ?? 'Неверный файл' });
    } else {
      clearErrors('file');
      setValue('file', f, { shouldDirty: true });
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const onSubmit = async (values: UploadFormValues) => {
    setStep(UploadStep.UPLOADING);
    setProgress(0);

    try {
      const { response: urlResp } = await screenshotApi.createUploadUrl({
        filename: values.file.name,
        mimeType: values.file.type,
        fileSize: BigInt(values.file.size),
      });

      await s3Api.uploadToS3(urlResp.uploadUrl, values.file, (p) => setProgress(p));

      setStep(UploadStep.REGISTERING);

      await screenshotApi.registerScreenshot({
        originalFilename: values.file.name,
        mimeType: values.file.type,
        fileSize: BigInt(values.file.size),
        storageBucket: urlResp.storageBucket,
        storageKey: urlResp.storageKey,
        title: values.title?.trim() || values.file.name,
      });

      setStep(UploadStep.DONE);
      setTimeout(onUploaded, UPLOAD_SUCCESS_DELAY_MS);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Ошибка загрузки';
      setError('root.serverError', { message });
      setStep(UploadStep.SELECT);
    }
  };

  return (
    <Dialog open onOpenChange={(open) => { if (!open && !isUploading) onClose(); }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Загрузить скриншот</DialogTitle>
          <DialogDescription className="sr-only">
            Выберите файл изображения для загрузки и анализа
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit(onSubmit)} noValidate className="flex flex-col gap-4">
          <div>
            <div
              onDrop={isUploading ? undefined : handleDrop}
              onDragOver={isUploading ? undefined : (e) => e.preventDefault()}
              onClick={isUploading ? undefined : () => inputRef.current?.click()}
              className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
                isUploading
                  ? 'border-border bg-muted/30 cursor-default pointer-events-none'
                  : errors.file
                  ? 'border-red-400 bg-red-50/40 cursor-pointer'
                  : previewFile
                  ? 'border-primary/60 bg-primary/5 cursor-pointer'
                  : 'border-border hover:border-primary/40 hover:bg-muted/50 cursor-pointer'
              }`}
            >
              <input
                ref={inputRef}
                type="file"
                accept={ALLOWED_IMAGE_TYPES.join(',')}
                className="hidden"
                onChange={(e) => {
                  const f = e.target.files?.[0];
                  if (f) handleFile(f);
                  e.target.value = '';
                }}
              />
              {previewFile ? (
                <div className="flex flex-col items-center gap-2">
                  <ImageIcon className="w-8 h-8 text-primary" />
                  <p className="text-sm font-medium text-foreground">{previewFile.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {(previewFile.size / 1024).toFixed(0)} KB · {previewFile.type.replace('image/', '')}
                  </p>
                </div>
              ) : (
                <div className="flex flex-col items-center gap-2">
                  <FolderOpen className="w-8 h-8 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Перетащите скриншот сюда или{' '}
                    <span className="text-primary underline">выберите файл</span>
                  </p>
                  <p className="text-xs text-muted-foreground">JPEG, PNG, GIF, WebP · до 20 МБ</p>
                </div>
              )}
            </div>
            {errors.file && (
              <p role="alert" className="mt-1.5 text-xs text-red-600 leading-tight">
                {errors.file.message as string}
              </p>
            )}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="upload-title">
              Название{' '}
              <span className="text-muted-foreground font-normal">(необязательно)</span>
            </Label>
            <Input
              id="upload-title"
              {...register('title')}
              placeholder="Название скриншота…"
              disabled={isUploading}
              aria-invalid={!!errors.title}
              className={errors.title ? 'border-red-400 focus-visible:ring-red-300' : ''}
            />
            {errors.title && (
              <p role="alert" className="text-xs text-red-600 leading-tight">
                {errors.title.message as string}
              </p>
            )}
          </div>

          <div className={`space-y-2 ${isUploading ? 'visible' : 'invisible pointer-events-none'}`}>
            <Progress
              value={step === UploadStep.REGISTERING ? 100 : progress}
              className="h-1.5"
            />
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <Loader2 className="w-3.5 h-3.5 animate-spin" />
              {step === UploadStep.UPLOADING
                ? `Загрузка файла… ${progress}%`
                : 'Сохранение скриншота…'}
            </div>
          </div>

          {errors.root?.serverError && (
            <p role="alert" className="text-xs text-red-600 leading-tight">
              {errors.root.serverError.message}
            </p>
          )}

          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              className="flex-1"
              onClick={onClose}
              disabled={isUploading}
            >
              Отмена
            </Button>
            <Button type="submit" className="flex-1" disabled={!previewFile || !!errors.file || isUploading}>
              {isUploading ? (
                <><Loader2 className="w-4 h-4 animate-spin" />Загрузка…</>
              ) : (
                <><Upload className="w-4 h-4" />Загрузить</>
              )}
            </Button>
          </div>
        </form>
      </DialogContent>
    </Dialog>
  );
}
