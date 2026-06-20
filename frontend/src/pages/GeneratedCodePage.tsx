import { useState } from "react";
import { useParams } from "react-router-dom";
import { useQuery, useMutation } from "@tanstack/react-query";
import { Download, FileCode2, FolderOpen, Loader2, AlertCircle, Code2, Github, ExternalLink, CheckCircle2, XCircle } from "lucide-react";
import { generatedCodeApi, type FileEntry } from "@/services/generatedCodeApi";
import { githubApi, type PushAppResponse } from "@/services/githubApi";
import { cn } from "@/lib/utils";

// ── Language badge colour ─────────────────────────────────────────────────────

const LANG_COLOR: Record<string, string> = {
  python:     "bg-blue-100 text-blue-700",
  typescript: "bg-sky-100 text-sky-700",
  tsx:        "bg-sky-100 text-sky-700",
  javascript: "bg-yellow-100 text-yellow-700",
  sql:        "bg-orange-100 text-orange-700",
  yaml:       "bg-purple-100 text-purple-700",
  markdown:   "bg-gray-100 text-gray-600",
  dockerfile: "bg-teal-100 text-teal-700",
  json:       "bg-green-100 text-green-700",
  bash:       "bg-neutral-100 text-neutral-700",
};

function LangBadge({ lang }: { lang: string }) {
  const cls = LANG_COLOR[lang] ?? "bg-muted text-muted-foreground";
  return (
    <span className={cn("rounded px-1.5 py-0.5 text-[10px] font-medium", cls)}>
      {lang}
    </span>
  );
}

// ── File tree ─────────────────────────────────────────────────────────────────

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  return `${(bytes / 1024).toFixed(1)} KB`;
}

interface FileTreeProps {
  files: FileEntry[];
  selectedPath: string | null;
  onSelect: (path: string) => void;
}

function FileTree({ files, selectedPath, onSelect }: FileTreeProps) {
  // Group files by top-level folder
  const grouped = files.reduce<Record<string, FileEntry[]>>((acc, f) => {
    const parts = f.path.split("/");
    const folder = parts.length > 1 ? parts[0] : "(root)";
    (acc[folder] ??= []).push(f);
    return acc;
  }, {});

  const [openFolders, setOpenFolders] = useState<Set<string>>(
    () => new Set(Object.keys(grouped))
  );

  const toggle = (folder: string) =>
    setOpenFolders((prev) => {
      const next = new Set(prev);
      next.has(folder) ? next.delete(folder) : next.add(folder);
      return next;
    });

  return (
    <div className="text-sm">
      {Object.entries(grouped).map(([folder, entries]) => (
        <div key={folder}>
          <button
            onClick={() => toggle(folder)}
            className="flex w-full items-center gap-1.5 px-2 py-1.5 text-xs font-semibold text-muted-foreground hover:bg-accent rounded"
          >
            <FolderOpen className="h-3.5 w-3.5 flex-shrink-0" />
            {folder}
          </button>

          {openFolders.has(folder) && (
            <div className="ml-3 border-l pl-2 space-y-0.5">
              {entries.map((f) => {
                const name = f.path.split("/").pop() ?? f.path;
                const selected = f.path === selectedPath;
                return (
                  <button
                    key={f.path}
                    onClick={() => onSelect(f.path)}
                    className={cn(
                      "flex w-full items-center gap-2 rounded px-2 py-1 text-left text-xs transition-colors",
                      selected
                        ? "bg-primary/10 text-primary font-medium"
                        : "hover:bg-accent text-foreground",
                    )}
                  >
                    <FileCode2 className="h-3.5 w-3.5 flex-shrink-0 text-muted-foreground" />
                    <span className="flex-1 truncate">{name}</span>
                    <span className="text-[10px] text-muted-foreground flex-shrink-0">
                      {formatBytes(f.size)}
                    </span>
                  </button>
                );
              })}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function GeneratedCodePage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [selectedPath, setSelectedPath] = useState<string | null>(null);
  const [pushResult, setPushResult] = useState<PushAppResponse | null>(null);
  const [pushError, setPushError] = useState<string | null>(null);

  const { data: tree, isLoading: treeLoading } = useQuery({
    queryKey: ["generated-code-tree", projectId],
    queryFn: () => generatedCodeApi.getTree(projectId!),
    enabled: !!projectId,
    staleTime: 30_000,
  });

  const { data: fileContent, isLoading: fileLoading } = useQuery({
    queryKey: ["generated-code-file", projectId, selectedPath],
    queryFn: () => generatedCodeApi.getFile(projectId!, selectedPath!),
    enabled: !!projectId && !!selectedPath,
    staleTime: 60_000,
  });

  const pushMutation = useMutation({
    mutationFn: () => githubApi.pushApp(projectId!),
    onSuccess: (data) => {
      setPushResult(data);
      setPushError(null);
    },
    onError: (err: Error) => {
      setPushError(err.message);
      setPushResult(null);
    },
  });

  const downloadUrl = projectId ? generatedCodeApi.getDownloadUrl(projectId) : null;
  const hasFiles = !treeLoading && tree?.exists && tree.files.length > 0;
  const noFiles = !treeLoading && tree && (!tree.exists || tree.files.length === 0);

  return (
    <div className="flex flex-col h-full gap-0">
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b bg-white">
        <div className="flex items-center gap-2">
          <Code2 className="h-5 w-5 text-primary" />
          <h2 className="text-sm font-semibold">Generated Code</h2>
          {tree?.exists && (
            <span className="text-xs text-muted-foreground">
              {tree.files.length} file{tree.files.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          {hasFiles && (
            <button
              onClick={() => pushMutation.mutate()}
              disabled={pushMutation.isPending}
              className="flex items-center gap-1.5 rounded-md border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {pushMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Github className="h-3.5 w-3.5" />
              )}
              {pushMutation.isPending ? "Pushing…" : "Push to GitHub"}
            </button>
          )}
          {hasFiles && downloadUrl && (
            <a
              href={downloadUrl}
              download
              className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-xs font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
            >
              <Download className="h-3.5 w-3.5" />
              Download ZIP
            </a>
          )}
        </div>
      </div>

      {/* Push result banner */}
      {pushResult && (
        <div className="flex items-start gap-3 border-b bg-green-50 px-4 py-3">
          <CheckCircle2 className="h-4 w-4 text-green-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-green-800">
              Pushed {pushResult.files_pushed} file{pushResult.files_pushed !== 1 ? "s" : ""} to GitHub
            </p>
            <a
              href={pushResult.repo_url}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-1 text-xs text-green-700 underline underline-offset-2 mt-0.5"
            >
              {pushResult.repo_full_name}
              <ExternalLink className="h-3 w-3" />
            </a>
            {pushResult.errors.length > 0 && (
              <p className="text-xs text-yellow-700 mt-1">
                {pushResult.errors.length} file(s) failed: {pushResult.errors[0]}
                {pushResult.errors.length > 1 && ` (+${pushResult.errors.length - 1} more)`}
              </p>
            )}
          </div>
          <button
            onClick={() => setPushResult(null)}
            className="text-green-500 hover:text-green-700 text-xs"
          >
            ✕
          </button>
        </div>
      )}

      {/* Push error banner */}
      {pushError && (
        <div className="flex items-start gap-3 border-b bg-red-50 px-4 py-3">
          <XCircle className="h-4 w-4 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="flex-1 min-w-0">
            <p className="text-xs font-medium text-red-800">Failed to push to GitHub</p>
            <p className="text-xs text-red-700 mt-0.5">{pushError}</p>
          </div>
          <button onClick={() => setPushError(null)} className="text-red-500 hover:text-red-700 text-xs">
            ✕
          </button>
        </div>
      )}


      {/* Body */}
      {treeLoading ? (
        <div className="flex flex-1 items-center justify-center gap-2 text-sm text-muted-foreground">
          <Loader2 className="h-4 w-4 animate-spin" />
          Loading files…
        </div>
      ) : noFiles ? (
        <div className="flex flex-1 flex-col items-center justify-center gap-3 text-center p-8">
          <AlertCircle className="h-8 w-8 text-muted-foreground/50" />
          <p className="text-sm font-medium">No generated code yet</p>
          <p className="text-xs text-muted-foreground max-w-sm">
            Run the AI pipeline and approve Step 7 (Developer Agents) to generate
            source code files for your project.
          </p>
        </div>
      ) : (
        <div className="flex flex-1 min-h-0">
          {/* File tree sidebar */}
          <aside className="w-64 flex-shrink-0 border-r overflow-y-auto bg-white p-2">
            <FileTree
              files={tree!.files}
              selectedPath={selectedPath}
              onSelect={setSelectedPath}
            />
          </aside>

          {/* File viewer */}
          <main className="flex-1 overflow-auto bg-gray-50">
            {!selectedPath ? (
              <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
                Select a file to view its content
              </div>
            ) : fileLoading ? (
              <div className="flex h-full items-center justify-center gap-2 text-sm text-muted-foreground">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading…
              </div>
            ) : fileContent ? (
              <div className="flex flex-col h-full">
                {/* File header bar */}
                <div className="flex items-center gap-2 border-b bg-white px-4 py-2 sticky top-0">
                  <FileCode2 className="h-4 w-4 text-muted-foreground flex-shrink-0" />
                  <span className="text-xs font-mono text-foreground flex-1 truncate">
                    {fileContent.path}
                  </span>
                  <LangBadge lang={fileContent.lang} />
                  <span className="text-xs text-muted-foreground flex-shrink-0">
                    {formatBytes(fileContent.size)}
                  </span>
                </div>
                {/* Code content */}
                <pre className="flex-1 overflow-auto p-4 text-xs font-mono leading-relaxed text-foreground whitespace-pre">
                  {fileContent.content}
                </pre>
              </div>
            ) : null}
          </main>
        </div>
      )}
    </div>
  );
}
