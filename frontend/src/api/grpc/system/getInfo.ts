import type { RpcOptions, UnaryCall } from '@protobuf-ts/runtime-rpc';
import type { GetInfoRequest, GetInfoResponse } from '@/proto/generated/system';
import { getSystemServiceClient } from '@/api/grpc/transport';

export function getInfo(
  input: GetInfoRequest,
  options?: RpcOptions,
): UnaryCall<GetInfoRequest, GetInfoResponse> {
  return getSystemServiceClient().getInfo(input, options);
}
