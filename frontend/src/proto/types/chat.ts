/**
 * Chat service types
 * Corresponds to proto/chat.proto
 */

import type { Timestamp, PaginationRequest, PaginationResponse, MessageRole, MessageStatus } from './common';

// Entity types
export interface ChatSession {
  id: string;
  screenshotId: string;
  title: string;
  messageCount: number;
  createdAt?: Timestamp;
  updatedAt?: Timestamp;
}

export interface ChatMessage {
  id: string;
  sessionId: string;
  role: MessageRole;
  content: string;
  status: MessageStatus;
  modelName: string;
  createdAt?: Timestamp;
}

// Request/Response types
export interface CreateSessionRequest {
  screenshotId: string;
  title?: string;
}

export interface CreateSessionResponse {
  session: ChatSession;
}

export interface ListSessionsRequest {
  screenshotId: string;
  pagination?: PaginationRequest;
}

export interface ListSessionsResponse {
  sessions: ChatSession[];
  pagination?: PaginationResponse;
}

export interface GetSessionRequest {
  sessionId: string;
}

export interface GetSessionResponse {
  session: ChatSession;
}

export interface DeleteSessionRequest {
  sessionId: string;
}

export interface DeleteSessionResponse {
  success: boolean;
}

export interface ListMessagesRequest {
  sessionId: string;
  pagination?: PaginationRequest;
}

export interface ListMessagesResponse {
  messages: ChatMessage[];
  pagination?: PaginationResponse;
}

export interface SendMessageRequest {
  sessionId: string;
  content: string;
}

// Streaming event types
export interface MessageCreatedEvent {
  message: ChatMessage;
}

export interface AssistantChunkEvent {
  chunk: string;
  index: number;
}

export interface AssistantDoneEvent {
  message: ChatMessage;
}

export interface ErrorEvent {
  code: string;
  message: string;
}

export type SendMessageEvent =
  | { type: 'messageCreated'; data: MessageCreatedEvent }
  | { type: 'assistantChunk'; data: AssistantChunkEvent }
  | { type: 'assistantDone'; data: AssistantDoneEvent }
  | { type: 'error'; data: ErrorEvent };
