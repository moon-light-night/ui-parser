import { createSession } from '@/api/grpc/chat/createSession';
import { listSessions } from '@/api/grpc/chat/listSessions';
import { getSession } from '@/api/grpc/chat/getSession';
import { deleteSession } from '@/api/grpc/chat/deleteSession';
import { listMessages } from '@/api/grpc/chat/listMessages';
import { sendMessage } from '@/api/grpc/chat/sendMessage';
import { resumeMessageStream } from '@/api/grpc/chat/resumeMessageStream';

export const chatApi = {
  createSession,
  listSessions,
  getSession,
  deleteSession,
  listMessages,
  sendMessage,
  resumeMessageStream,
};

