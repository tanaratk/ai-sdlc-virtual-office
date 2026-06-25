import type { LlmSetting } from "@/types/agent";
import type { ConnectorSetting, ConnectorTestResult } from "@/types/connector";
import apiClient from "./apiClient";

export const settingsApi = {
  listLlm: () =>
    apiClient.get<LlmSetting[]>("/settings/llm").then((r) => r.data),

  createLlm: (data: {
    provider: string;
    model_name: string;
    base_url?: string;
    api_key?: string;
    is_active?: boolean;
  }) => apiClient.post<LlmSetting>("/settings/llm", data).then((r) => r.data),

  patchLlm: (
    settingId: string,
    data: { is_active?: boolean; api_key?: string; temperature?: number; max_tokens?: number }
  ) => apiClient.patch<LlmSetting>(`/settings/llm/${settingId}`, data).then((r) => r.data),

  activateLlm: (settingId: string) =>
    apiClient.post<LlmSetting>(`/settings/llm/${settingId}/activate`).then((r) => r.data),

  testKey: (provider: string, apiKey: string) =>
    apiClient
      .post<{ valid: boolean; message: string }>("/settings/llm/test-key", { provider, api_key: apiKey })
      .then((r) => r.data),

  // ── Connectors ───────────────────────────────────────────────────────────────
  listConnectors: () =>
    apiClient.get<ConnectorSetting[]>("/settings/connectors").then((r) => r.data),

  upsertConnector: (connectorType: string, data: { access_token?: string; extra_config?: Record<string, string> }) =>
    apiClient.put<ConnectorSetting>(`/settings/connectors/${connectorType}`, data).then((r) => r.data),

  testConnector: (connectorType: string) =>
    apiClient.post<ConnectorTestResult>(`/settings/connectors/${connectorType}/test`).then((r) => r.data),

  deleteConnector: (connectorType: string) =>
    apiClient.delete(`/settings/connectors/${connectorType}`),
};
