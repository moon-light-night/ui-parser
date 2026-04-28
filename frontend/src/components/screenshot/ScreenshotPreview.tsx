import { ImageIcon, Loader2 } from 'lucide-react';
import type { Screenshot } from '@/proto/generated/screenshot';
import { screenshotImageUrl } from '@/components/screenshot/analysisHelpers';

interface ScreenshotPreviewProps {
  screenshot: Screenshot;
  isAnalyzing: boolean;
}

export function ScreenshotPreview({ screenshot, isAnalyzing }: ScreenshotPreviewProps) {
  const imageUrl = screenshotImageUrl(screenshot);
  return (
    <div className="bg-card rounded-xl border border-border overflow-hidden sticky top-0">
      {imageUrl ? (
        <img
          src={imageUrl}
          alt={screenshot.originalFilename}
          className="w-full object-contain max-h-[600px]"
        />
      ) : (
        <div className="flex flex-col items-center justify-center h-64 text-muted-foreground gap-2">
          <ImageIcon className="w-10 h-10" />
          <span className="text-sm">Превью недоступно</span>
        </div>
      )}
      {isAnalyzing && (
        <div className="flex items-center gap-2 px-4 py-2 bg-yellow-500/10 border-t border-yellow-500/20 text-yellow-600 dark:text-yellow-400 text-xs">
          <Loader2 className="w-3 h-3 animate-spin" />
          Анализ выполняется…
        </div>
      )}
    </div>
  );
}
