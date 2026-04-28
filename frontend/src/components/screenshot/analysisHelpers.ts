import type { Screenshot } from '@/proto/generated/screenshot';
import { Severity, Priority } from '@/proto/generated/common';

const S3_PUBLIC = import.meta.env.VITE_APP_S3_PUBLIC_URL ?? 'http://localhost:9000';

export function screenshotImageUrl(s: Screenshot): string | null {
  if (s.storageUrl) return s.storageUrl;
  if (s.storageBucket && s.storageKey)
    return `${S3_PUBLIC}/${s.storageBucket}/${s.storageKey}`;
  return null;
}

export function severityVariant(s: Severity): 'success' | 'warning' | 'destructive' | 'secondary' {
  switch (s) {
    case Severity.LOW:    return 'success';
    case Severity.MEDIUM: return 'warning';
    case Severity.HIGH:   return 'destructive';
    default:              return 'secondary';
  }
}

export function severityLabel(s: Severity): string {
  switch (s) {
    case Severity.LOW:    return 'Low';
    case Severity.MEDIUM: return 'Medium';
    case Severity.HIGH:   return 'High';
    default:              return '?';
  }
}

export function priorityVariant(p: Priority): 'secondary' | 'default' | 'warning' {
  switch (p) {
    case Priority.LOW:    return 'secondary';
    case Priority.MEDIUM: return 'default';
    case Priority.HIGH:   return 'warning';
    default:              return 'secondary';
  }
}

export function priorityLabel(p: Priority): string {
  switch (p) {
    case Priority.LOW:    return 'Low';
    case Priority.MEDIUM: return 'Medium';
    case Priority.HIGH:   return 'High';
    default:              return '?';
  }
}

export function formatBytes(bytes: bigint | number): string {
  const n = Number(bytes);
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(0)} KB`;
  return `${(n / (1024 * 1024)).toFixed(1)} MB`;
}
