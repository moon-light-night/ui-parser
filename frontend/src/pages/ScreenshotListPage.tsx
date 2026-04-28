import { lazy, Suspense, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { ImageIcon, Upload, RefreshCw, AlertCircle, Trash2 } from 'lucide-react';
import type { Screenshot } from '@/proto/generated/screenshot';
import { ScreenshotStatus } from '@/proto/generated/common';
import { screenshotImageUrl, formatBytes } from '@/components/screenshot/analysisHelpers';
import { LOCALE } from '@/lib/constants';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  DialogFooter,
} from '@/components/ui/dialog';
const UploadDialog = lazy(() => import('@/components/UploadDialog'));
import { AppHeader } from '@/components/AppHeader';
import { useScreenshotStore } from '@/store';

function statusBadge(status: ScreenshotStatus) {
  switch (status) {
    case ScreenshotStatus.UPLOADED:   return <Badge variant="default">Загружен</Badge>;
    case ScreenshotStatus.ANALYZING:  return <Badge variant="warning">Анализируется…</Badge>;
    case ScreenshotStatus.COMPLETED:  return <Badge variant="success">Проанализирован</Badge>;
    case ScreenshotStatus.FAILED:     return <Badge variant="destructive">Ошибка</Badge>;
    default:                          return <Badge variant="secondary">Неизвестен</Badge>;
  }
}

function formatDate(ts?: { seconds: bigint | number }): string {
  if (!ts?.seconds) return '';
  return new Date(Number(ts.seconds) * 1000).toLocaleDateString(LOCALE, {
    month: 'short', day: 'numeric', year: 'numeric',
  });
}

function ScreenshotCardSkeleton() {
  return (
    <Card className="overflow-hidden">
      <Skeleton className="w-full h-40 rounded-none" />
      <CardContent className="p-3 space-y-2">
        <div className="flex items-start justify-between gap-2">
          <Skeleton className="h-4 w-3/5" />
          <Skeleton className="h-5 w-16 rounded-full" />
        </div>
        <Skeleton className="h-3 w-2/5" />
      </CardContent>
    </Card>
  );
}

function ScreenshotCard({
  screenshot,
  onClick,
  onDelete,
}: {
  screenshot: Screenshot;
  onClick: () => void;
  onDelete: (e: React.MouseEvent) => void;
}) {
  const imgUrl = screenshotImageUrl(screenshot);
  return (
    <Card
      onClick={onClick}
      className="group overflow-hidden cursor-pointer hover:shadow-md hover:border-blue-300 transition-all"
    >
      <div className="relative w-full h-40 bg-muted/40 overflow-hidden flex items-center justify-center">
        {imgUrl && (
          <img
            src={imgUrl}
            alt={screenshot.originalFilename}
            className="w-full h-full object-cover group-hover:scale-[1.02] transition-transform duration-200"
            onError={(e) => { e.currentTarget.style.display = 'none'; }}
          />
        )}
        {!imgUrl && <ImageIcon className="w-10 h-10 text-muted-foreground/30" />}
        <button
          onClick={onDelete}
          className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity
                     bg-background/80 backdrop-blur-sm rounded-md p-1.5
                     text-muted-foreground hover:text-destructive hover:bg-destructive/10
                     focus-visible:opacity-100 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
          aria-label="Удалить скриншот"
          title="Удалить"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
      <CardContent className="p-3">
        <div className="flex items-start justify-between gap-2 mb-1.5">
          <p className="text-sm font-medium text-foreground truncate flex-1 min-w-0">
            {screenshot.title || screenshot.originalFilename}
          </p>
          {statusBadge(screenshot.status)}
        </div>
        <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
          <span>{formatBytes(screenshot.fileSize)}</span>
          <span>·</span>
          <span>{screenshot.mimeType.replace('image/', '')}</span>
          {screenshot.createdAt && (
            <><span>·</span><span>{formatDate(screenshot.createdAt)}</span></>
          )}
        </div>
      </CardContent>
    </Card>
  );
}

export default function ScreenshotListPage() {
  const {
    screenshots,
    loaded,
    error,
    showUpload,
    pendingDelete,
    deleting,
    load,
    setShowUpload,
    setPendingDelete,
    confirmDelete,
  } = useScreenshotStore();

  const navigate = useNavigate();

  useEffect(() => load(), []);  // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <div className="h-full flex flex-col bg-background">
      <AppHeader
        right={
          <>
            {loaded && (
              <Button variant="ghost" size="sm" onClick={() => load(true)} title="Обновить">
                <RefreshCw className="w-4 h-4" />
              </Button>
            )}
            <Button onClick={() => setShowUpload(true)} size="sm">
              <Upload className="w-4 h-4" />
              Загрузить
            </Button>
          </>
        }
      />

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto px-6 py-8">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription className="flex items-center justify-between">
              <span>{error}</span>
              <button onClick={() => load(true)} className="underline font-medium ml-4 shrink-0">Повторить</button>
            </AlertDescription>
          </Alert>
        )}

        {!loaded && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {Array.from({ length: 6 }).map((_, i) => <ScreenshotCardSkeleton key={i} />)}
          </div>
        )}

        {loaded && !error && screenshots.length === 0 && (
          <div className="flex flex-col items-center justify-center py-32 text-center">
            <div className="w-16 h-16 bg-muted rounded-2xl flex items-center justify-center mb-5">
              <ImageIcon className="w-8 h-8 text-muted-foreground" />
            </div>
            <h2 className="text-base font-semibold text-foreground mb-1">Нет скриншотов</h2>
            <p className="text-sm text-muted-foreground mb-6 max-w-xs">
              Загрузите первый скриншот, чтобы получить AI-анализ и обратную связь.
            </p>
            <Button onClick={() => setShowUpload(true)}>
              <Upload className="w-4 h-4" />
              Загрузить скриншот
            </Button>
          </div>
        )}

        {loaded && screenshots.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {screenshots.map((s) => (
              <ScreenshotCard
                key={s.id}
                screenshot={s}
                onClick={() => navigate(`/screenshots/${s.id}`)}
                onDelete={(e) => { e.stopPropagation(); setPendingDelete(s); }}
              />
            ))}
          </div>
        )}
        </div>
      </main>

      {showUpload && (
        <Suspense fallback={null}>
          <UploadDialog
            onClose={() => setShowUpload(false)}
            onUploaded={() => { setShowUpload(false); load(); }}
          />
        </Suspense>
      )}

      <Dialog open={!!pendingDelete} onOpenChange={(open) => { if (!open && !deleting) setPendingDelete(null); }}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Удалить скриншот?</DialogTitle>
            <DialogDescription>
              Скриншот «{pendingDelete?.title || pendingDelete?.originalFilename}» и все связанные данные
              (анализ, чаты) будут удалены без возможности восстановления.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setPendingDelete(null)}
              disabled={deleting}
            >
              Отмена
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDelete}
              disabled={deleting}
            >
              {deleting ? 'Удаление…' : 'Удалить'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
