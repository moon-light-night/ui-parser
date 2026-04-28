/**
 * Значения дискриминантов для поля `event.oneofKind` серверного стрима SendChatMessage.
 */
export const ChatStreamEvent = {
  MESSAGE_CREATED: 'messageCreated',
  ASSISTANT_CHUNK: 'assistantChunk',
  ASSISTANT_DONE:  'assistantDone',
  ERROR:           'error',
} as const;

/**
 * Значения дискриминантов для поля `event.oneofKind` серверного стрима RunScreenshotAnalysis.
 */
export const AnalysisStreamEvent = {
  COMPLETED: 'completed',
  FAILED:    'failed',
} as const;
