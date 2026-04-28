import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ScreenshotListPage from '@/pages/ScreenshotListPage';
import ScreenshotDetailPage from '@/pages/ScreenshotDetailPage';
import ChatPage from '@/pages/ChatPage';
import { Toaster } from '@/components/ui/toaster';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<ScreenshotListPage />} />
        <Route path="/screenshots/:id" element={<ScreenshotDetailPage />} />
        <Route path="/screenshots/:id/chat" element={<ChatPage />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
      <Toaster />
    </BrowserRouter>
  );
}
