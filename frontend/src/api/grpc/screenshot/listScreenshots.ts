import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { ListScreenshotsRequest, ListScreenshotsResponse } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function listScreenshots(
  input: ListScreenshotsRequest,
  options?: RpcOptions,
): UnaryCall<ListScreenshotsRequest, ListScreenshotsResponse> {
  return getScreenshotServiceClient().listScreenshots(input, options);
}
