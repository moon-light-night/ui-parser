import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { DeleteScreenshotRequest, DeleteScreenshotResponse } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function deleteScreenshot(
  input: DeleteScreenshotRequest,
  options?: RpcOptions,
): UnaryCall<DeleteScreenshotRequest, DeleteScreenshotResponse> {
  return getScreenshotServiceClient().deleteScreenshot(input, options);
}
