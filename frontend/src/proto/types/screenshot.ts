/**
 * Screenshot service types
 * Corresponds to proto/screenshot.proto
 */

import type { Timestamp, PaginationRequest, PaginationResponse, ScreenshotStatus, Severity, Priority } from './common';

// Entity types
export interface Screenshot {
  id: string;
  title: string;
  originalFilename: string;
  mimeType: string;
  fileSize: number;
  storageBucket: string;
  storageKey: string;
  storageRegion: string;
  storageUrl: string;
  status: ScreenshotStatus;
  createdAt?: Timestamp;
  updatedAt?: Timestamp;
}

export interface AnalysisSection {
  name: string;
  description: string;
}

export interface UiIssue {
  title: string;
  severity: Severity;
  description: string;
  evidence: string;
  recommendation: string;
}

export interface UxSuggestion {
  title: string;
  description: string;
}

export interface ImplementationTask {
  title: string;
  description: string;
  priority: Priority;
}

export interface Analysis {
  id: string;
  screenshotId: string;
  modelName: string;
  screenType: string;
  summary: string;
  sections: AnalysisSection[];
  uiIssues: UiIssue[];
  uxSuggestions: UxSuggestion[];
  implementationTasks: ImplementationTask[];
  errorMessage: string;
  createdAt?: Timestamp;
  updatedAt?: Timestamp;
}

// Request/Response types
export interface CreateUploadUrlRequest {
  filename: string;
  mimeType: string;
  fileSize: number;
}

export interface CreateUploadUrlResponse {
  uploadUrl: string;
  storageBucket: string;
  storageKey: string;
  expiresAt: number;
}

export interface RegisterScreenshotRequest {
  originalFilename: string;
  mimeType: string;
  fileSize: number;
  storageBucket: string;
  storageKey: string;
  title?: string;
}

export interface RegisterScreenshotResponse {
  screenshot: Screenshot;
}

export interface ListScreenshotsRequest {
  pagination?: PaginationRequest;
}

export interface ListScreenshotsResponse {
  screenshots: Screenshot[];
  pagination?: PaginationResponse;
}

export interface GetScreenshotRequest {
  screenshotId: string;
}

export interface GetScreenshotResponse {
  screenshot: Screenshot;
}

export interface StartAnalysisRequest {
  screenshotId: string;
  modelName?: string;
}

export interface StartAnalysisResponse {
  analysisId: string;
  status: ScreenshotStatus;
}

export interface GetLatestAnalysisRequest {
  screenshotId: string;
}

export interface GetLatestAnalysisResponse {
  analysis: Analysis;
}
