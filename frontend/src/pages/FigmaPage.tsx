import { useState } from "react";
import { useParams } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  CheckCircle2,
  ExternalLink,
  Figma,
  Loader2,
  Trash2,
  Upload,
  Monitor,
} from "lucide-react";
import { figmaApi } from "@/services/figmaApi";

export default function FigmaPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const qc = useQueryClient();
  const [fileUrl, setFileUrl] = useState("");
  const [showEmbed, setShowEmbed] = useState(true);

  const { data: setting, isLoading: settingLoading } = useQuery({
    queryKey: ["figma-setting", projectId],
    queryFn: () => figmaApi.getSetting(projectId!),
    enabled: !!projectId,
    retry: false,
  });

  const { data: screens = [], isLoading: screensLoading } = useQuery({
    queryKey: ["figma-screens", projectId],
    queryFn: () => figmaApi.listScreens(projectId!),
    enabled: !!projectId,
  });

  const linkMutation = useMutation({
    mutationFn: () => figmaApi.linkFile(projectId!, fileUrl.trim()),
    onSuccess: () => {
      setFileUrl("");
      qc.invalidateQueries({ queryKey: ["figma-setting", projectId] });
    },
  });

  const unlinkMutation = useMutation({
    mutationFn: () => figmaApi.unlink(projectId!),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["figma-setting", projectId] }),
  });

  const pushMutation = useMutation({
    mutationFn: () => figmaApi.pushScreens(projectId!),
  });

  const isLinked = !!setting;

  return (
    <div className="mx-auto max-w-3xl space-y-8">
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold flex items-center gap-2">
          <Figma className="h-5 w-5 text-purple-500" /> Figma Integration
        </h2>
        <p className="text-sm text-muted-foreground mt-1">
          Link a Figma file and push UX Agent screen specs as Figma comments for your design team.
        </p>
      </div>

      {/* Figma Token Warning */}
      <div className="rounded-md border border-amber-200 bg-amber-50 p-3 text-sm text-amber-800 flex items-start gap-2">
        <AlertTriangle className="h-4 w-4 shrink-0 mt-0.5" />
        <span>
          Requires a Figma Personal Access Token in{" "}
          <strong>Settings → Connectors → Figma</strong>.
        </span>
      </div>

      {/* ── Link Figma File ─────────────────────────────────────────────────── */}
      <section className="space-y-4">
        <h3 className="text-sm font-semibold">
          {isLinked ? "Linked Figma File" : "Link Figma File"}
        </h3>

        {settingLoading ? (
          <p className="text-sm text-muted-foreground">Loading…</p>
        ) : isLinked && setting ? (
          <div className="rounded-lg border border-purple-200 bg-purple-50 p-4 space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-purple-800">
                <CheckCircle2 className="h-4 w-4" />
                <span className="text-sm font-medium">{setting.file_name || setting.file_key}</span>
              </div>
              <div className="flex items-center gap-2">
                <a
                  href={setting.file_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs text-purple-600 hover:underline flex items-center gap-1"
                >
                  Open in Figma <ExternalLink className="h-3 w-3" />
                </a>
                <button
                  onClick={() => unlinkMutation.mutate()}
                  disabled={unlinkMutation.isPending}
                  className="text-xs text-red-500 hover:text-red-700 flex items-center gap-1"
                >
                  <Trash2 className="h-3 w-3" /> Unlink
                </button>
              </div>
            </div>
            <p className="text-xs text-purple-600 font-mono">Key: {setting.file_key}</p>
          </div>
        ) : null}

        {/* Always show link form so user can update */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground">
            {isLinked ? "Replace with another file URL" : "Paste Figma file URL"}
          </label>
          <div className="flex gap-2">
            <input
              value={fileUrl}
              onChange={(e) => setFileUrl(e.target.value)}
              placeholder="https://www.figma.com/file/xxxxxx/..."
              className="flex-1 rounded-md border px-3 py-2 text-sm font-mono focus:outline-none focus:ring-2 focus:ring-ring"
            />
            <button
              onClick={() => linkMutation.mutate()}
              disabled={!fileUrl.trim() || linkMutation.isPending}
              className="flex items-center gap-2 rounded-md bg-purple-600 px-4 py-2 text-sm font-medium text-white hover:bg-purple-700 disabled:opacity-50"
            >
              {linkMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Figma className="h-4 w-4" />}
              {isLinked ? "Update" : "Link File"}
            </button>
          </div>
          {linkMutation.isError && (
            <p className="text-sm text-destructive flex items-center gap-1.5">
              <AlertTriangle className="h-4 w-4" />
              {linkMutation.error instanceof Error ? linkMutation.error.message : "Failed to link file."}
            </p>
          )}
          {linkMutation.isSuccess && (
            <p className="text-sm text-green-700 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4" /> Figma file linked successfully.
            </p>
          )}
        </div>
      </section>

      {/* ── UX Agent Screens ────────────────────────────────────────────────── */}
      <section className="space-y-4 border-t pt-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold">UX Agent Screens ({screens.length})</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Parsed from the UX Agent's screen spec document.
            </p>
          </div>
          {isLinked && screens.length > 0 && (
            <button
              onClick={() => pushMutation.mutate()}
              disabled={pushMutation.isPending}
              className="flex items-center gap-2 rounded-md bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 disabled:opacity-50"
            >
              {pushMutation.isPending
                ? <><Loader2 className="h-4 w-4 animate-spin" /> Pushing…</>
                : <><Upload className="h-4 w-4" /> Push to Figma</>}
            </button>
          )}
        </div>

        {pushMutation.isSuccess && pushMutation.data && (
          <div className="rounded-md border border-green-300 bg-green-50 p-3 text-sm text-green-800 space-y-1">
            <p className="font-medium">
              {pushMutation.data.pushed} screen spec(s) pushed as Figma comments
              {pushMutation.data.skipped > 0 && `, ${pushMutation.data.skipped} skipped`}
            </p>
            {pushMutation.data.errors.length > 0 && (
              <ul className="text-xs text-destructive list-disc pl-4">
                {pushMutation.data.errors.map((e, i) => <li key={i}>{e}</li>)}
              </ul>
            )}
          </div>
        )}
        {pushMutation.isError && (
          <div className="flex items-start gap-2 rounded-md border border-destructive/40 bg-red-50 p-3 text-sm text-destructive">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {pushMutation.error instanceof Error ? pushMutation.error.message : "Push failed."}
          </div>
        )}

        {screensLoading ? (
          <p className="text-sm text-muted-foreground">Loading screens…</p>
        ) : screens.length === 0 ? (
          <p className="text-sm text-muted-foreground">
            No screens found. Run the UX Agent pipeline step to generate the screen spec.
          </p>
        ) : (
          <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
            {screens.map((screen) => (
              <div
                key={screen.screen_id}
                className="rounded-lg border bg-card p-3 space-y-1.5"
              >
                <div className="flex items-center gap-2">
                  <span className="rounded bg-purple-100 px-1.5 py-0.5 text-[10px] font-mono font-bold text-purple-700">
                    {screen.screen_id}
                  </span>
                  <p className="text-sm font-medium leading-tight">{screen.name}</p>
                </div>
                {screen.description && (
                  <p className="text-xs text-muted-foreground line-clamp-2">{screen.description}</p>
                )}
                {screen.components.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {screen.components.slice(0, 5).map((c) => (
                      <span
                        key={c}
                        className="rounded-full bg-muted px-2 py-0.5 text-[10px] text-muted-foreground"
                      >
                        {c}
                      </span>
                    ))}
                    {screen.components.length > 5 && (
                      <span className="text-[10px] text-muted-foreground">
                        +{screen.components.length - 5} more
                      </span>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </section>

      {/* ── Figma Embed Preview ──────────────────────────────────────────────── */}
      {isLinked && setting && (
        <section className="space-y-3 border-t pt-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold flex items-center gap-2">
              <Monitor className="h-4 w-4" /> Figma Preview
            </h3>
            <button
              onClick={() => setShowEmbed((v) => !v)}
              className="text-xs text-muted-foreground hover:text-foreground"
            >
              {showEmbed ? "Hide" : "Show"}
            </button>
          </div>
          {showEmbed && (
            <div className="rounded-lg border overflow-hidden bg-muted/30" style={{ height: 480 }}>
              <iframe
                src={setting.embed_url}
                className="w-full h-full border-0"
                allowFullScreen
                title="Figma preview"
              />
            </div>
          )}
        </section>
      )}
    </div>
  );
}
