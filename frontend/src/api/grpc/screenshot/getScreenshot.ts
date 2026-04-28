import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { GetScreenshotRequest, GetScreenshotResponse } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function getScreenshot(
  input: GetScreenshotRequest,
  options?: RpcOptions,
): UnaryCall<GetScreenshotRequest, GetScreenshotResponse> {
  return getScreenshotServiceClient().getScreenshot(input, options);
}
