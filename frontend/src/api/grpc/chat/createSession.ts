import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { CreateSessionRequest, CreateSessionResponse } from '@/proto/generated/chat';
import { getChatServiceClient } from '@/api/grpc/transport';

export function createSession(
  input: CreateSessionRequest,
  options?: RpcOptions,
): UnaryCall<CreateSessionRequest, CreateSessionResponse> {
  return getChatServiceClient().createSession(input, options);
}
