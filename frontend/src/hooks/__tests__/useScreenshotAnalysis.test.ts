import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useScreenshotAnalysis } from '../useScreenshotAnalysis';
import { AnalysisStreamEvent } from '@/lib/streamEvents';

const mockRunAnalysis = vi.fn();

vi.mock('@/api', () => ({
  screenshotApi: {
    runAnalysis: (...args: unknown[]) => mockRunAnalysis(...args),
  },
}));

function makeStream(events: object[]) {
  return {
    responses: (async function* () {
      for (const e of events) yield e;
    })(),
  };
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const ANALYSIS = { id: 'a1', screenshotId: 's1', summary: 'ok', modelName: 'llava', resultJson: '' } as any;
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const SCREENSHOT = { id: 's1', originalFilename: 'shot.png' } as any;

describe('useScreenshotAnalysis — начальное состояние', () => {
  it('isAnalyzing=false', () => {
    const { result } = renderHook(() =>
      useScreenshotAnalysis({
        screenshotId: 's1',
        onCompleted: vi.fn(),
        onFailed: vi.fn(),
      }),
    );
    expect(result.current.isAnalyzing).toBe(false);
  });
});

describe('useScreenshotAnalysis — защитные условия', () => {
  it('не запускает анализ без screenshotId', () => {
    const { result } = renderHook(() =>
      useScreenshotAnalysis({
        screenshotId: undefined,
        onCompleted: vi.fn(),
        onFailed: vi.fn(),
      }),
    );
    act(() => result.current.runAnalysis());
    expect(mockRunAnalysis).not.toHaveBeenCalled();
  });
});

describe('useScreenshotAnalysis — события стрима', () => {
  beforeEach(() => mockRunAnalysis.mockClear());

  it('вызывает onCompleted при COMPLETED и сбрасывает isAnalyzing', async () => {
    const onCompleted = vi.fn();
    mockRunAnalysis.mockReturnValue(
      makeStream([
        { event: { oneofKind: AnalysisStreamEvent.COMPLETED, completed: { analysis: ANALYSIS, screenshot: SCREENSHOT } } },
      ]),
    );

    const { result } = renderHook(() =>
      useScreenshotAnalysis({ screenshotId: 's1', onCompleted, onFailed: vi.fn() }),
    );
    await act(async () => result.current.runAnalysis());

    expect(onCompleted).toHaveBeenCalledWith(SCREENSHOT, ANALYSIS);
    expect(result.current.isAnalyzing).toBe(false);
  });

  it('вызывает onFailed при FAILED и сбрасывает isAnalyzing', async () => {
    const onFailed = vi.fn();
    mockRunAnalysis.mockReturnValue(
      makeStream([
        { event: { oneofKind: AnalysisStreamEvent.FAILED, failed: { errorMessage: 'timeout' } } },
      ]),
    );

    const { result } = renderHook(() =>
      useScreenshotAnalysis({ screenshotId: 's1', onCompleted: vi.fn(), onFailed }),
    );
    await act(async () => result.current.runAnalysis());

    expect(onFailed).toHaveBeenCalledWith('timeout');
    expect(result.current.isAnalyzing).toBe(false);
  });
});
