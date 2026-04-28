import * as grpcWeb from 'grpc-web';
import type {
  CreateSessionRequest,
  CreateSessionResponse,
  ListSessionsRequest,
  ListSessionsResponse,
  GetSessionRequest,
  GetSessionResponse,
  DeleteSessionRequest,
  DeleteSessionResponse,
  ListMessagesRequest,
  ListMessagesResponse,
  SendMessageRequest,
  ChatMessage,
} from '../types/chat';

const SERVICE_NAME = 'uiparser.chat.ChatService';

export class ChatServiceClient {
  private client: grpcWeb.GrpcWebClientBase;
  private hostname: string;

  constructor(hostname: string) {
    this.hostname = hostname;
    this.client = new grpcWeb.GrpcWebClientBase({ format: 'text' });
  }

  private buildUrl(method: string): string {
    return `${this.hostname}/${SERVICE_NAME}/${method}`;
  }

  createSession(request: CreateSessionRequest): Promise<CreateSessionResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/CreateSession`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: CreateSessionRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as CreateSessionResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('CreateSession'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: CreateSessionResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  listSessions(request: ListSessionsRequest): Promise<ListSessionsResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/ListSessions`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: ListSessionsRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as ListSessionsResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('ListSessions'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: ListSessionsResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  getSession(request: GetSessionRequest): Promise<GetSessionResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/GetSession`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: GetSessionRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as GetSessionResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('GetSession'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: GetSessionResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  deleteSession(request: DeleteSessionRequest): Promise<DeleteSessionResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/DeleteSession`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: DeleteSessionRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as DeleteSessionResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('DeleteSession'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: DeleteSessionResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  listMessages(request: ListMessagesRequest): Promise<ListMessagesResponse> {
    return new Promise((resolve, reject) => {
      const methodDescriptor = new grpcWeb.MethodDescriptor(
        `/${SERVICE_NAME}/ListMessages`,
        grpcWeb.MethodType.UNARY,
        Object,
        Object,
        (req: ListMessagesRequest) => {
          const encoder = new TextEncoder();
          return encoder.encode(JSON.stringify(req));
        },
        (bytes: Uint8Array) => {
          const decoder = new TextDecoder();
          return JSON.parse(decoder.decode(bytes)) as ListMessagesResponse;
        }
      );

      this.client.rpcCall(
        this.buildUrl('ListMessages'),
        request,
        {},
        methodDescriptor,
        (err: grpcWeb.RpcError, response: ListMessagesResponse) => {
          if (err) reject(err);
          else resolve(response);
        }
      );
    });
  }

  sendMessage(
    request: SendMessageRequest,
    callbacks: {
      onMessageCreated?: (message: ChatMessage) => void;
      onChunk?: (chunk: string, index: number) => void;
      onDone?: (message: ChatMessage) => void;
      onError?: (error: grpcWeb.RpcError) => void;
    }
  ): grpcWeb.ClientReadableStream<unknown> {
    const methodDescriptor = new grpcWeb.MethodDescriptor(
      `/${SERVICE_NAME}/SendMessage`,
      grpcWeb.MethodType.SERVER_STREAMING,
      Object,
      Object,
      (req: SendMessageRequest) => {
        const encoder = new TextEncoder();
        return encoder.encode(JSON.stringify(req));
      },
      (bytes: Uint8Array) => {
        const decoder = new TextDecoder();
        return JSON.parse(decoder.decode(bytes));
      }
    );

    const stream = this.client.serverStreaming(
      this.buildUrl('SendMessage'),
      request,
      {},
      methodDescriptor
    );

    stream.on('data', (response: unknown) => {
      const event = response as Record<string, unknown>;
      
      if (event.messageCreated && callbacks.onMessageCreated) {
        const msgData = event.messageCreated as { message: ChatMessage };
        callbacks.onMessageCreated(msgData.message);
      } else if (event.assistantChunk && callbacks.onChunk) {
        const chunkData = event.assistantChunk as { chunk: string; index: number };
        callbacks.onChunk(chunkData.chunk, chunkData.index);
      } else if (event.assistantDone && callbacks.onDone) {
        const doneData = event.assistantDone as { message: ChatMessage };
        callbacks.onDone(doneData.message);
      } else if (event.error && callbacks.onError) {
        const errorData = event.error as { code: string; message: string };
        const rpcError = new grpcWeb.RpcError(
          grpcWeb.StatusCode.INTERNAL,
          errorData.message,
          {}
        );
        callbacks.onError(rpcError);
      }
    });

    stream.on('error', (err: grpcWeb.RpcError) => {
      if (callbacks.onError) {
        callbacks.onError(err);
      }
    });

    return stream;
  }

  async sendMessageAsync(request: SendMessageRequest): Promise<{
    userMessage: ChatMessage;
    assistantMessage: ChatMessage;
  }> {
    return new Promise((resolve, reject) => {
      let userMessage: ChatMessage | null = null;
      let assistantMessage: ChatMessage | null = null;
      let fullContent = '';

      const stream = this.sendMessage(request, {
        onMessageCreated: (message) => {
          userMessage = message;
        },
        onChunk: (chunk) => {
          fullContent += chunk;
        },
        onDone: (message) => {
          assistantMessage = message;
        },
        onError: (error) => {
          reject(error);
        },
      });

      stream.on('end', () => {
        if (userMessage && assistantMessage) {
          resolve({ userMessage, assistantMessage });
        } else {
          reject(new Error('Stream ended without complete response'));
        }
      });
    });
  }
}
