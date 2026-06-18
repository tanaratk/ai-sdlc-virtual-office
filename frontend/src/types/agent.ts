export type AgentStatus = "idle" | "working" | "done" | "error";
export type ModelProvider = "ollama" | "openai";

export interface Agent {
  id: string;
  name: string;
  role: string;
  description: string | null;
  status: AgentStatus;
  home_zone: string | null;
  current_zone: string | null;
  location_x: number;
  location_y: number;
  model_provider: ModelProvider;
  model_name: string;
  is_active: boolean;
}
