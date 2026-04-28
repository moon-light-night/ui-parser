import { create } from 'zustand';
import { screenshotApi } from '@/api';
import type { Screenshot } from '@/proto/generated/screenshot';
import { PAGE_SIZE_SCREENSHOTS } from '@/lib/constants';

interface ScreenshotListState {
  screenshots: Screenshot[];
  loaded: boolean;
  error: string | null;
  showUpload: boolean;
  pendingDelete: Screenshot | null;
  deleting: boolean;

  load: (showSpinner?: boolean) => void;
  setShowUpload: (show: boolean) => void;
  setPendingDelete: (screenshot: Screenshot | null) => void;
  confirmDelete: () => Promise<void>;
}

export const useScreenshotStore = create<ScreenshotListState>()((set, get) => ({
  screenshots: [],
  loaded: false,
  error: null,
  showUpload: false,
  pendingDelete: null,
  deleting: false,

  load: (showSpinner = false) => {
    if (showSpinner) set({ loaded: false });
    set({ error: null });

    screenshotApi
      .listScreenshots({ pagination: { pageSize: PAGE_SIZE_SCREENSHOTS, pageToken: '' } })
      .then(({ response: res }) => set({ screenshots: res.screenshots, loaded: true }))
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : 'Не удалось загрузить скриншоты';
        set({ error: msg, loaded: true });
      });
  },

  setShowUpload: (show) => set({ showUpload: show }),

  setPendingDelete: (screenshot) => set({ pendingDelete: screenshot }),

  confirmDelete: async () => {
    const { pendingDelete } = get();
    if (!pendingDelete) return;

    set({ deleting: true });
    try {
      await screenshotApi.deleteScreenshot({ screenshotId: pendingDelete.id });
      set((state) => ({
        screenshots: state.screenshots.filter((s) => s.id !== pendingDelete.id),
        pendingDelete: null,
        deleting: false,
      }));
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Не удалось удалить скриншот';
      set({ error: msg, pendingDelete: null, deleting: false });
    }
  },
}));
