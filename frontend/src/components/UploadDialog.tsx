import { useState, useRef } from 'react';
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
import { UPLOAD_SUCCESS_DELAY_MS } from '@/lib/constants';

interface Props {
  onClose: () => void;
  onUploaded: () => void;
}

const ALLOWED_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

const UploadStep = {
  SELECT:      'select',
  UPLOADING:   'uploading',
  REGISTERING: 'registering',
  DONE:        'done',
  ERROR:       'error',
} as const;
type UploadStep = typeof UploadStep[keyof typeof UploadStep];

export default function UploadDialog({ onClose, onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState('');
  const [step, setStep] = useState<UploadStep>(UploadStep.SELECT);
  const [errorMsg, setErrorMsg] = useState('');
  const [progress, setProgress] = useState(0);

  const inputRef = useRef<HTMLInputElement>(null);

  const handleFile = (f: File) => {
    if (!ALLOWED_TYPES.includes(f.type)) {
      setErrorMsg(`Неподдерживаемый тип файла: ${f.type}. Разрешены: JPEG, PNG, GIF, WebP.`);
      return;
    }
    setErrorMsg('');
    setFile(f);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const f = e.dataTransfer.files[0];
    if (f) handleFile(f);
  };

  const upload = async () => {
    if (!file) return;
    setStep(UploadStep.UPLOADING);
    setProgress(0);

    try {
      const { response: urlResp } = await screenshotApi.createUploadUrl({
        filename: file.name,
        mimeType: file.type,
        fileSize: BigInt(file.size),
      });

      await s3Api.uploadToS3(urlResp.uploadUrl, file, (p) => setProgress(p));

      setStep(UploadStep.REGISTERING);
      await screenshotApi.registerScreenshot({
        originalFilename: file.name,
        mimeType: file.type,
        fileSize: BigInt(file.size),
        storageBucket: urlResp.storageBucket,
        storageKey: urlResp.storageKey,
        title: title.trim() || file.name,
      });

      setStep(UploadStep.DONE);
      setTimeout(onUploaded, UPLOAD_SUCCESS_DELAY_MS);
    } catch (err: unknown) {
      setErrorMsg((err as Error).message || 'Ошибка загрузки');
      setStep(UploadStep.ERROR);
    }
  };

  const isUploading = step === UploadStep.UPLOADING || step === UploadStep.REGISTERING;

  return (
    <Dialog open onOpenChange={(open) => { if (!open && !isUploading) onClose(); }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Загрузить скриншот</DialogTitle>
          <DialogDescription className="sr-only">
            Выберите файл изображения для загрузки и анализа
          </DialogDescription>
        </DialogHeader>

        <div
          onDrop={isUploading ? undefined : handleDrop}
          onDragOver={isUploading ? undefined : (e) => e.preventDefault()}
          onClick={isUploading ? undefined : () => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-xl p-8 text-center transition-colors ${
            isUploading
              ? 'border-border bg-muted/30 cursor-default pointer-events-none'
              : file
              ? 'border-primary/60 bg-primary/5 cursor-pointer'
              : 'border-border hover:border-primary/40 hover:bg-muted/50 cursor-pointer'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept={ALLOWED_TYPES.join(',')}
            className="hidden"
            onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }}
          />
          {file ? (
            <div className="flex flex-col items-center gap-2">
              <ImageIcon className="w-8 h-8 text-primary" />
              <p className="text-sm font-medium text-foreground">{file.name}</p>
              <p className="text-xs text-muted-foreground">
                {(file.size / 1024).toFixed(0)} KB · {file.type.replace('image/', '')}
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

        <div className="space-y-1.5">
          <Label htmlFor="upload-title">
            Название{' '}
            <span className="text-muted-foreground font-normal">(необязательно)</span>
          </Label>
          <Input
            id="upload-title"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Дайте скриншоту название…"
            disabled={isUploading}
          />
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

        {errorMsg && (
          <p className="text-xs text-red-600 leading-tight">{errorMsg}</p>
        )}

        <div className="flex gap-3">
          <Button variant="outline" className="flex-1" onClick={onClose} disabled={isUploading}>
            Отмена
          </Button>
          <Button className="flex-1" onClick={upload} disabled={!file || isUploading}>
            {isUploading ? (
              <><Loader2 className="w-4 h-4 animate-spin" />Загрузка…</>
            ) : (
              <><Upload className="w-4 h-4" />Загрузить</>
            )}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
