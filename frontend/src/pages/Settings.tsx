export default function Settings() {
  return (
    <div className="space-y-4 max-w-lg">
      <h2 className="text-lg font-semibold">Settings</h2>

      <section className="rounded-lg border bg-white p-4 space-y-3">
        <h3 className="text-sm font-semibold">LLM Provider</h3>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm">Provider</span>
            <span className="text-sm text-muted-foreground">Ollama (default)</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Model</span>
            <span className="text-sm text-muted-foreground">qwen3:8b</span>
          </div>
          <div className="flex items-center justify-between">
            <span className="text-sm">Base URL</span>
            <span className="text-sm text-muted-foreground">http://localhost:11434</span>
          </div>
        </div>
        <p className="text-xs text-muted-foreground">
          Full LLM settings management available in Sprint 8.
        </p>
      </section>

      <section className="rounded-lg border bg-white p-4 space-y-3">
        <h3 className="text-sm font-semibold">Backend</h3>
        <div className="flex items-center justify-between">
          <span className="text-sm">API Base URL</span>
          <span className="text-sm text-muted-foreground">/api/v1</span>
        </div>
      </section>
    </div>
  );
}
