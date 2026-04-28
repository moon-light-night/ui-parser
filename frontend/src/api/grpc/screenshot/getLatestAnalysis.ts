import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { GetLatestAnalysisRequest, GetLatestAnalysisResponse } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function getLatestAnalysis(
  input: GetLatestAnalysisRequest,
  options?: RpcOptions,
): UnaryCall<GetLatestAnalysisRequest, GetLatestAnalysisResponse> {
  return getScreenshotServiceClient().getLatestAnalysis(input, options);
}
