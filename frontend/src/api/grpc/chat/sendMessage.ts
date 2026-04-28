import type { RpcOptions, ServerStreamingCall } from '@protobuf-ts/runtime-rpc';
import type { SendMessageRequest, SendMessageEvent } from '@/proto/generated/chat';
import { getChatServiceClient } from '@/api/grpc/transport';

export function sendMessage(
  input: SendMessageRequest,
  options?: RpcOptions,
): ServerStreamingCall<SendMessageRequest, SendMessageEvent> {
  return getChatServiceClient().sendMessage(input, options);
}
