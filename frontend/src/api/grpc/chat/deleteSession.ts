import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { DeleteSessionRequest, DeleteSessionResponse } from '@/proto/generated/chat';
import { getChatServiceClient } from '@/api/grpc/transport';

export function deleteSession(
  input: DeleteSessionRequest,
  options?: RpcOptions,
): UnaryCall<DeleteSessionRequest, DeleteSessionResponse> {
  return getChatServiceClient().deleteSession(input, options);
}
