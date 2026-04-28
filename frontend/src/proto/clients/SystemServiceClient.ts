import * as grpcWeb from 'grpc-web';
import type {
  HealthRequest,
  HealthResponse,
  GetInfoRequest,
  GetInfoResponse,
} from '../types/system';

const SERVICE_NAME = 'uiparser.system.SystemService';

export class SystemServiceClient {
  private client: grpcWeb.GrpcWebClientBase;
  private hostname: string;

  constructor(hostname: string) {
    this.hostname = hostname;
    this.client = new grpcWeb.GrpcWebClientBase({ format: 'text' });
  }

  private buildUrl(method: string): string {
    return `${this.hostname}/${SERVICE_NAME}/${method}`;
  }

  health(request: HealthRequest = {}): Promise<HealthResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/Health`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: HealthRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as HealthResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('Health'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: HealthResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  getInfo(request: GetInfoRequest = {}): Promise<GetInfoResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/GetInfo`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: GetInfoRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as GetInfoResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('GetInfo'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: GetInfoResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }
}
