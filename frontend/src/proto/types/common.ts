/**
 * Common types shared across all gRPC services
 * Corresponds to proto/common.proto
 */

export interface Timestamp {
  seconds: number;
  nanos: number;
}

export interface PaginationRequest {
  pageSize: number;
  pageToken: string;
}

export interface PaginationResponse {
  nextPageToken: string;
  totalCount: number;
}

export const ScreenshotStatus = {
  UNSPECIFIED: 0,
  UPLOADED: 1,
  ANALYZING: 2,
  COMPLETED: 3,
  FAILED: 4,
} as const;
export type ScreenshotStatus = typeof ScreenshotStatus[keyof typeof ScreenshotStatus];

export const MessageRole = {
  UNSPECIFIED: 0,
  USER: 1,
  ASSISTANT: 2,
  SYSTEM: 3,
} as const;
export type MessageRole = typeof MessageRole[keyof typeof MessageRole];

export const MessageStatus = {
  UNSPECIFIED: 0,
  COMPLETED: 1,
  STREAMING: 2,
  FAILED: 3,
} as const;
export type MessageStatus = typeof MessageStatus[keyof typeof MessageStatus];

export const Severity = {
  UNSPECIFIED: 0,
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
} as const;
export type Severity = typeof Severity[keyof typeof Severity];

export const Priority = {
  UNSPECIFIED: 0,
  LOW: 1,
  MEDIUM: 2,
  HIGH: 3,
} as const;
export type Priority = typeof Priority[keyof typeof Priority];

export function timestampToDate(ts: Timestamp | undefined): Date | null {
  if (!ts) return null;
  return new Date(ts.seconds * 1000 + ts.nanos / 1000000);
}

export function dateToTimestamp(date: Date): Timestamp {
  const ms = date.getTime();
  return {
    seconds: Math.floor(ms / 1000),
    nanos: (ms % 1000) * 1000000,
  };
}
