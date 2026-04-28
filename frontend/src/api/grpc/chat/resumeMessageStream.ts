import type { RpcOptions, ServerStreamingCall } from '@protobuf-ts/runtime-rpc';
import type { ResumeMessageStreamRequest, SendMessageEvent } from '@/proto/generated/chat';
import { getChatServiceClient } from '@/api/grpc/transport';

export function resumeMessageStream(
  input: ResumeMessageStreamRequest,
  options?: RpcOptions,
): ServerStreamingCall<ResumeMessageStreamRequest, SendMessageEvent> {
  return getChatServiceClient().resumeMessageStream(input, options);
}
