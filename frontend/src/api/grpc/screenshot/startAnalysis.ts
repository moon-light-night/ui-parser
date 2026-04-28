import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { StartAnalysisRequest, StartAnalysisResponse } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function startAnalysis(
  input: StartAnalysisRequest,
  options?: RpcOptions,
): UnaryCall<StartAnalysisRequest, StartAnalysisResponse> {
  return getScreenshotServiceClient().startAnalysis(input, options);
}
