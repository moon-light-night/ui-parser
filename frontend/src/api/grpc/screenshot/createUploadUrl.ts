import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { CreateUploadUrlRequest, CreateUploadUrlResponse } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function createUploadUrl(
  input: CreateUploadUrlRequest,
  options?: RpcOptions,
): UnaryCall<CreateUploadUrlRequest, CreateUploadUrlResponse> {
  return getScreenshotServiceClient().createUploadUrl(input, options);
}
