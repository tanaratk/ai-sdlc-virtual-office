export type AgentStatus = "idle" | "working" | "done" | "error";
export type ModelProvider = "ollama" | "openai";

export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string | null;
  goal: string | null;
  status: AgentStatus;
  home_zone: string | null;
  current_zone: string | null;
  location_x: number;
  location_y: number;
  model_provider: ModelProvider;
  model_name: string;
  is_active: boolean;
  updated_at: string;
}

export interface AgentUpdate {
  model_provider?: ModelProvider;
  model_name?: string;
  description?: string;
  is_active?: boolean;
}

export interface OllamaModel {
  name: string;
  size: number | null;
  modified_at: string | null;
}

export interface OllamaModelsResponse {
  models: OllamaModel[];
  base_url: string;
}

export interface LlmSetting {
  id: string;
  provider: ModelProvider;
  base_url: string | null;
  model_name: string;
  temperature: number;
  max_tokens: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}
