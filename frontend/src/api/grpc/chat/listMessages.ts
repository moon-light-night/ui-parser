import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { ListMessagesRequest, ListMessagesResponse } from '@/proto/generated/chat';
import { getChatServiceClient } from '@/api/grpc/transport';

export function listMessages(
  input: ListMessagesRequest,
  options?: RpcOptions,
): UnaryCall<ListMessagesRequest, ListMessagesResponse> {
  return getChatServiceClient().listMessages(input, options);
}
