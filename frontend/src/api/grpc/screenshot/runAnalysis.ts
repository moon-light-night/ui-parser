import type { RpcOptions, ServerStreamingCall } from '@protobuf-ts/runtime-rpc';
import type { RunAnalysisRequest, RunAnalysisEvent } from '@/proto/generated/screenshot';
import { getScreenshotServiceClient } from '@/api/grpc/transport';

export function runAnalysis(
  input: RunAnalysisRequest,
  options?: RpcOptions,
): ServerStreamingCall<RunAnalysisRequest, RunAnalysisEvent> {
  return getScreenshotServiceClient().runAnalysis(input, options);
}
