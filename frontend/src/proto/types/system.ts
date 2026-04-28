/**
 * System service types
 * Corresponds to proto/system.proto
 */

export interface ServiceStatus {
  name: string;
  healthy: boolean;
  message: string;
}

export interface HealthRequest {}

export interface HealthResponse {
  healthy: boolean;
  version: string;
  services: ServiceStatus[];
}

export interface GetInfoRequest {}

export interface GetInfoResponse {
  version: string;
  environment: string;
  availableModels: string[];
}
