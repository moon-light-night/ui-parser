import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft, MessageSquare, Sparkles, RefreshCw, Loader2, AlertCircle,
} from 'lucide-react';
import { screenshotApi } from '@/api';
import type { Screenshot, Analysis } from '@/proto/generated/screenshot';
import { ScreenshotStatus } from '@/proto/generated/common';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ScreenshotPreview } from '@/components/screenshot/ScreenshotPreview';
import { AnalysisPanel } from '@/components/screenshot/AnalysisPanel';
import { AppHeader } from '@/components/AppHeader';
import { useScreenshotAnalysis } from '@/hooks/useScreenshotAnalysis';

export default function ScreenshotDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [screenshot, setScreenshot] = useState<Screenshot | null>(null);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [loadedScreenshotId, setLoadedScreenshotId] = useState<string | null | undefined>(undefined);
  const [loadedAnalysisId, setLoadedAnalysisId] = useState<string | null | undefined>(undefined);
  const [error, setError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const loadingScreenshot = loadedScreenshotId === undefined;
  const loadingAnalysis = !!id && loadedAnalysisId !== id;

  const { isAnalyzing, runAnalysis } = useScreenshotAnalysis({
    screenshotId: id,
    onCompleted: (s, a) => {
      if (s) setScreenshot(s);
      setAnalysis(a);
      setAnalysisError(null);
    },
    onFailed: (msg) => {
      setAnalysisError(msg);
      setScreenshot((prev) => prev ? { ...prev, status: ScreenshotStatus.FAILED } : prev);
    },
  });

  useEffect(() => {
    if (!id) return;
    screenshotApi
      .getScreenshot({ screenshotId: id })
      .then(({ response: res }) => {
        const s = res.screenshot ?? null;
        setScreenshot(s);
        setLoadedScreenshotId(id);
        if (s?.status === ScreenshotStatus.ANALYZING) runAnalysis();
      })
      .catch((err) => {
        setError(err.message || 'Не удалось загрузить скриншот');
        setLoadedScreenshotId(id);
      });
  }, [id]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!id) return;
    screenshotApi
      .getLatestAnalysis({ screenshotId: id })
      .then(({ response: res }) => { setAnalysis(res.analysis ?? null); setLoadedAnalysisId(id); })
      .catch(() => { setAnalysis(null); setLoadedAnalysisId(id); });
  }, [id]);

  if (loadingScreenshot) {
    return (
      <div className="h-full bg-background flex items-center justify-center">
        <Loader2 className="w-6 h-6 text-muted-foreground animate-spin" />
      </div>
    );
  }

  if (error || !screenshot) {
    return (
      <div className="h-full bg-background flex items-center justify-center">
        <div className="text-center space-y-4">
          <Alert variant="destructive" className="text-left">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error || 'Скриншот не найден'}</AlertDescription>
          </Alert>
          <Button variant="outline" size="sm" onClick={() => navigate('/')}>К списку</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full flex flex-col bg-background">
      <AppHeader
        right={
          <>
            <Button variant="outline" size="sm" onClick={() => navigate(`/screenshots/${id}/chat`)}>
              <MessageSquare className="w-4 h-4" />
              Чат
            </Button>
            {isAnalyzing ? (
              <Button size="sm" disabled>
                <Loader2 className="w-4 h-4 animate-spin" />
                Анализируется…
              </Button>
            ) : (
              <Button size="sm" onClick={runAnalysis}>
                {analysis ? (
                  <><RefreshCw className="w-4 h-4" />Повторить анализ</>
                ) : (
                  <><Sparkles className="w-4 h-4" />Анализировать</>
                )}
              </Button>
            )}
          </>
        }
      />

      <div className="bg-background border-b border-border px-4 h-9 flex items-center gap-1.5 text-sm text-muted-foreground shrink-0">
        <Button variant="ghost" size="sm" className="h-6 px-2 gap-1.5 text-xs" onClick={() => navigate('/')}>
          <ArrowLeft className="w-3 h-3" />
          Скриншоты
        </Button>
        <span>/</span>
        <span className="text-foreground font-medium truncate max-w-[300px]">
          {screenshot.title || screenshot.originalFilename}
        </span>
      </div>

      <main className="flex-1 min-h-0 overflow-hidden">
        <div className="h-full max-w-6xl mx-auto px-6 py-6 grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="overflow-y-auto">
            <ScreenshotPreview screenshot={screenshot} isAnalyzing={isAnalyzing} />
          </div>

          <div className="overflow-y-auto pr-1 space-y-4">
            {analysisError && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{analysisError}</AlertDescription>
              </Alert>
            )}
            <AnalysisPanel
              analysis={analysis}
              loading={loadingAnalysis}
              isAnalyzing={isAnalyzing}
            />
          </div>
        </div>
      </main>
    </div>
  );
}
