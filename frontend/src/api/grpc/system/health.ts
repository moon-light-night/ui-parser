import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { HealthRequest, HealthResponse } from '@/proto/generated/system';
import { getSystemServiceClient } from '@/api/grpc/transport';

export function health(
  input: HealthRequest,
  options?: RpcOptions,
): UnaryCall<HealthRequest, HealthResponse> {
  return getSystemServiceClient().health(input, options);
}
