import { lazy, Suspense } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Loader2 } from 'lucide-react';
import { Toaster } from '@/components/ui/toaster';

const ScreenshotListPage = lazy(() => import('@/pages/ScreenshotListPage'));
const ScreenshotDetailPage = lazy(() => import('@/pages/ScreenshotDetailPage'));
const ChatPage = lazy(() => import('@/pages/ChatPage'));

function PageFallback() {
  return (
    <div className="h-screen flex items-center justify-center">
      <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <Suspense fallback={<PageFallback />}>
        <Routes>
          <Route path="/" element={<ScreenshotListPage />} />
          <Route path="/screenshots/:id" element={<ScreenshotDetailPage />} />
          <Route path="/screenshots/:id/chat" element={<ChatPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Suspense>
      <Toaster />
    </BrowserRouter>
  );
}
