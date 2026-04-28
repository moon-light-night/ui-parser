import { useState, useRef } from 'react';
import { screenshotApi } from '@/api';
import type { Screenshot, Analysis } from '@/proto/generated/screenshot';
import { AnalysisStreamEvent } from '@/lib/streamEvents';

interface UseScreenshotAnalysisOptions {
  screenshotId: string | undefined;
  onCompleted: (screenshot: Screenshot | undefined, analysis: Analysis) => void;
  onFailed: (message: string) => void;
}

export function useScreenshotAnalysis({
  screenshotId,
  onCompleted,
  onFailed,
}: UseScreenshotAnalysisOptions) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  
  const streamRef = useRef<AbortController | null>(null);

  const runAnalysis = () => {
    if (!screenshotId || isAnalyzing) return;

    streamRef.current?.abort();
    const abort = new AbortController();
    streamRef.current = abort;
    setIsAnalyzing(true);

    const stream = screenshotApi.runAnalysis(
      { screenshotId, modelName: '' },
      { abort: abort.signal },
    );

    (async () => {
      try {
        for await (const event of stream.responses) {
          if (event.event.oneofKind === AnalysisStreamEvent.COMPLETED) {
            const { analysis, screenshot } = event.event.completed;
            if (analysis) onCompleted(screenshot, analysis);
            setIsAnalyzing(false);
            return;
          } else if (event.event.oneofKind === AnalysisStreamEvent.FAILED) {
            const msg = event.event.failed.errorMessage || 'Анализ завершился с ошибкой';
            onFailed(msg);
            setIsAnalyzing(false);
            return;
          }
        }
        setIsAnalyzing(false);
      } catch (err: unknown) {
        if (err instanceof Error && err.name === 'AbortError') {
          setIsAnalyzing(false);
          return;
        }
        onFailed(err instanceof Error ? err.message : 'Неизвестная ошибка');
        setIsAnalyzing(false);
      }
    })();
  };

  return { isAnalyzing, runAnalysis };
}
