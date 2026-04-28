import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { RegisterScreenshotRequest, RegisterScreenshotResponse } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function registerScreenshot(
  input: RegisterScreenshotRequest,
  options?: RpcOptions,
): UnaryCall<RegisterScreenshotRequest, RegisterScreenshotResponse> {
  return getScreenshotServiceClient().registerScreenshot(input, options);
}
