/**
 * Интерцепторы для обработки ошибок в gRPC и HTTP запросах.
 *
 *   - gRPC: INTERNAL, UNAVAILABLE, UNKNOWN, DATA_LOSS, DEADLINE_EXCEEDED
 *   - HTTP: 5xx коды и сетевые ошибки
 */

import type { RpcInterceptor, NextUnaryFn, NextServerStreamingFn, MethodInfo, RpcOptions } from '@protobuf-ts/runtime-rpc';
import { RpcError } from '@protobuf-ts/runtime-rpc';
import type { AxiosInstance, AxiosError } from 'axios';
import { toast } from '@/lib/toast';

const SERVER_SIDE_CODES = new Set([
  'INTERNAL',
  'UNAVAILABLE',
  'UNKNOWN',
  'DATA_LOSS',
  'DEADLINE_EXCEEDED',
]);

function isUnexpectedGrpcError(err: unknown): boolean {
  if (err instanceof RpcError) return SERVER_SIDE_CODES.has(err.code);
  return err instanceof TypeError;
}

function grpcErrorMessage(err: unknown): string {
  if (err instanceof RpcError) {
    const raw = err.message || '';
    const colonIdx = raw.indexOf(': ');
    const clean = colonIdx !== -1 ? raw.slice(colonIdx + 2) : raw;
    return clean || `Ошибка сервера (${err.code})`;
  }
  if (err instanceof Error) return err.message || 'Сетевая ошибка';
  return 'Неизвестная ошибка';
}

export const grpcErrorInterceptor: RpcInterceptor = {
  interceptUnary(
    next: NextUnaryFn,
    method: MethodInfo,
    input: object,
    options: RpcOptions,
  ) {
    const call = next(method, input, options);
    call.response.catch((err: unknown) => {
      if (isUnexpectedGrpcError(err)) {
        toast.error(grpcErrorMessage(err));
      }
    });
    return call;
  },

  interceptServerStreaming(
    next: NextServerStreamingFn,
    method: MethodInfo,
    input: object,
    options: RpcOptions,
  ) {
    const call = next(method, input, options);
    call.status.catch((err: unknown) => {
      if (isUnexpectedGrpcError(err)) {
        toast.error(grpcErrorMessage(err));
      }
    });
    return call;
  },
};

export function applyHttpErrorInterceptor(instance: AxiosInstance): void {
  instance.interceptors.response.use(
    (response) => response,
    (err: AxiosError) => {
      const isNetworkError = !err.response;
      const isServerError = (err.response?.status ?? 0) >= 500;

      if (isNetworkError || isServerError) {
        const status = err.response?.status;
        const serverMsg =
          (err.response?.data as { message?: string } | undefined)?.message;
        const message =
          serverMsg ||
          (isNetworkError ? 'Нет соединения с сервером' : `Ошибка сервера (${status})`);
        toast.error(message);
      }

      return Promise.reject(err);
    },
  );
}
