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
  skill_markdown: string | null;
  is_active: boolean;
  updated_at: string;
}

export interface AgentUpdate {
  model_provider?: ModelProvider;
  model_name?: string;
  description?: string;
  skill_markdown?: string;
  is_active?: boolean;
}

export type AgentContractLayer = "business" | "design" | "delivery" | "on_demand";

export interface AgentContractStep {
  name: string;
  order: number;
  total: number;
  auto_chain: boolean;
}

export interface AgentContractSummary {
  id: string;
  name: string;
  role: string;
  layer: AgentContractLayer;
  step: AgentContractStep;
  outputs: {
    documents: string[];
    workspace_files: string[];
  };
  handoff: {
    next_agent: string | null;
    review_gate: boolean;
    failure_action?: string;
  };
}

export interface AgentContract extends AgentContractSummary {
  model: {
    provider: string;
    default: string;
  };
  inputs: {
    required_documents: string[];
    optional_documents: string[];
    runtime_inputs: string[];
  };
  responsibilities: string[];
  workspace: {
    home_zone: string;
    writes_to: string[];
  };
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
