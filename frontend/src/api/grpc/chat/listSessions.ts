import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { ListSessionsRequest, ListSessionsResponse } from '@/proto/generated/chat';
import { getChatServiceClient } from '@/api/grpc/transport';

export function listSessions(
  input: ListSessionsRequest,
  options?: RpcOptions,
): UnaryCall<ListSessionsRequest, ListSessionsResponse> {
  return getChatServiceClient().listSessions(input, options);
}
