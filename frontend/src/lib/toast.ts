export type ToastVariant = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  variant: ToastVariant;
  message: string;
  duration: number; // ms, 0 = no auto-dismiss
}

type Listener = (toasts: Toast[]) => void;

let toasts: Toast[] = [];
const listeners = new Set<Listener>();

function notify() {
  listeners.forEach((l) => l([...toasts]));
}

export function subscribe(listener: Listener): () => void {
  listeners.add(listener);
  listener([...toasts]);
  return () => listeners.delete(listener);
}

export function dismiss(id: string) {
  toasts = toasts.filter((t) => t.id !== id);
  notify();
}

function add(variant: ToastVariant, message: string, duration = 4000): string {
  const id = Math.random().toString(36).slice(2);
  toasts = [...toasts, { id, variant, message, duration }];
  notify();
  if (duration > 0) {
    setTimeout(() => dismiss(id), duration);
  }
  return id;
}

export const toast = {
  success: (message: string, duration?: number) => add('success', message, duration),
  error:   (message: string, duration?: number) => add('error',   message, duration),
  info:    (message: string, duration?: number) => add('info',    message, duration),
};
