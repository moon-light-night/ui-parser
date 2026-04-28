import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { GetSessionRequest, GetSessionResponse } from '@/proto/generated/chat';
import { getChatServiceClient } from '@/api/grpc/transport';

export function getSession(
  input: GetSessionRequest,
  options?: RpcOptions,
): UnaryCall<GetSessionRequest, GetSessionResponse> {
  return getChatServiceClient().getSession(input, options);
}
