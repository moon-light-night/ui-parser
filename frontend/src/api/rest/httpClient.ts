import axios from 'axios';
import { applyHttpErrorInterceptor } from '@/lib/interceptors';

const httpClient = axios.create();

applyHttpErrorInterceptor(httpClient);

export { httpClient };
