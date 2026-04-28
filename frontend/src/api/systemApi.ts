import { health } from '@/api/grpc/system/health';
import { getInfo } from '@/api/grpc/system/getInfo';

export const systemApi = {
  health,
  getInfo,
};
