import { createUploadUrl } from '@/api/grpc/screenshot/createUploadUrl';
import { registerScreenshot } from '@/api/grpc/screenshot/registerScreenshot';
import { listScreenshots } from '@/api/grpc/screenshot/listScreenshots';
import { getScreenshot } from '@/api/grpc/screenshot/getScreenshot';
import { startAnalysis } from '@/api/grpc/screenshot/startAnalysis';
import { runAnalysis } from '@/api/grpc/screenshot/runAnalysis';
import { getLatestAnalysis } from '@/api/grpc/screenshot/getLatestAnalysis';
import { deleteScreenshot } from '@/api/grpc/screenshot/deleteScreenshot';

export const screenshotApi = {
  createUploadUrl,
  registerScreenshot,
  listScreenshots,
  getScreenshot,
  startAnalysis,
  runAnalysis,
  getLatestAnalysis,
  deleteScreenshot,
};
