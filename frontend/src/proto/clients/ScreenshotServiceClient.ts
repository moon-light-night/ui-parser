import * as grpcWeb from 'grpc-web';
import type {
  CreateUploadUrlRequest,
  CreateUploadUrlResponse,
  RegisterScreenshotRequest,
  RegisterScreenshotResponse,
  ListScreenshotsRequest,
  ListScreenshotsResponse,
  GetScreenshotRequest,
  GetScreenshotResponse,
  StartAnalysisRequest,
  StartAnalysisResponse,
  GetLatestAnalysisRequest,
  GetLatestAnalysisResponse,
} from '../types/screenshot';

const SERVICE_NAME = 'uiparser.screenshot.ScreenshotService';

export class ScreenshotServiceClient {
  private client: grpcWeb.GrpcWebClientBase;
  private hostname: string;

  constructor(hostname: string) {
    this.hostname = hostname;
    this.client = new grpcWeb.GrpcWebClientBase({ format: 'text' });
  }

  private buildUrl(method: string): string {
    return `${this.hostname}/${SERVICE_NAME}/${method}`;
  }

  createUploadUrl(request: CreateUploadUrlRequest): Promise<CreateUploadUrlResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/CreateUploadUrl`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: CreateUploadUrlRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as CreateUploadUrlResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('CreateUploadUrl'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: CreateUploadUrlResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  registerScreenshot(request: RegisterScreenshotRequest): Promise<RegisterScreenshotResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/RegisterScreenshot`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: RegisterScreenshotRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as RegisterScreenshotResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('RegisterScreenshot'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: RegisterScreenshotResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  listScreenshots(request: ListScreenshotsRequest): Promise<ListScreenshotsResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/ListScreenshots`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: ListScreenshotsRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as ListScreenshotsResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('ListScreenshots'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: ListScreenshotsResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  getScreenshot(request: GetScreenshotRequest): Promise<GetScreenshotResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/GetScreenshot`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: GetScreenshotRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as GetScreenshotResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('GetScreenshot'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: GetScreenshotResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  startAnalysis(request: StartAnalysisRequest): Promise<StartAnalysisResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/StartAnalysis`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: StartAnalysisRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as StartAnalysisResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('StartAnalysis'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: StartAnalysisResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  getLatestAnalysis(request: GetLatestAnalysisRequest): Promise<GetLatestAnalysisResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/GetLatestAnalysis`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: GetLatestAnalysisRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as GetLatestAnalysisResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('GetLatestAnalysis'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: GetLatestAnalysisResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }
}
