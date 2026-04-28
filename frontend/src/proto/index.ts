import { GrpcWebFetchTransport } from '@protobuf-ts/grpcweb-transport';
import { ScreenshotServiceClient } from '@/proto/generated/screenshot.client';
import { ChatServiceClient } from '@/proto/generated/chat.client';
import { SystemServiceClient } from '@/proto/generated/system.client';

function getGrpcBaseUrl(): string {
  return import.meta.env.VITE_APP_GRPC_BASE_URL ?? 'http://localhost:8080';
}

function makeTransport() {
  return new GrpcWebFetchTransport({ baseUrl: getGrpcBaseUrl() });
}

// Singleton instances
let screenshotClient: ScreenshotServiceClient | null = null;
let chatClient: ChatServiceClient | null = null;
let systemClient: SystemServiceClient | null = null;

export function getScreenshotClient(): ScreenshotServiceClient {
  if (!screenshotClient) screenshotClient = new ScreenshotServiceClient(makeTransport());
  return screenshotClient;
}

export function getChatClient(): ChatServiceClient {
  if (!chatClient) chatClient = new ChatServiceClient(makeTransport());
  return chatClient;
}

export function getSystemClient(): SystemServiceClient {
  if (!systemClient) systemClient = new SystemServiceClient(makeTransport());
  return systemClient;
}

export function resetClients(): void {
  screenshotClient = null;
  chatClient = null;
  systemClient = null;
}

// Re-export types
export * from '@/proto/types';
export * from '@/proto/clients';
