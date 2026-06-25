export type ConnectorType = "github" | "figma" | "drawio" | "jira";

export interface ConnectorSetting {
  connector_type: ConnectorType;
  display_name: string;
  description: string;
  icon: string;
  token_label: string | null;
  token_hint: string | null;
  requires_token: boolean;
  has_token: boolean;
  last_tested_at: string | null;
  last_test_ok: boolean | null;
  last_error: string | null;
  extra_config: Record<string, string> | null;
}

export interface ConnectorTestResult {
  ok: boolean;
  message: string;
}
