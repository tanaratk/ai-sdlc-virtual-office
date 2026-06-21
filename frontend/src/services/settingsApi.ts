import type { LlmSetting } from "@/types/agent";
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
};
