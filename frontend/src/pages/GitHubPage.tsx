import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ExternalLink,
  GitBranch,
  Github,
  Loader2,
  RefreshCw,
} from "lucide-react";
import { githubApi, type GitHubSettingUpsert } from "@/services/githubApi";

export default function GitHubPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  // ── Settings form state ──────────────────────────────────────────────────────
  const [owner, setOwner] = useState("");
  const [repo, setRepo] = useState("");
  const [token, setToken] = useState("");
  const [branchName, setBranchName] = useState("");
  const [showToken, setShowToken] = useState(false);

  // ── Queries ──────────────────────────────────────────────────────────────────
  const { data: settings, isLoading: settingsLoading } = useQuery({
    queryKey: ["github-settings", projectId],
    queryFn: () => githubApi.getSettings(projectId!),
    enabled: !!projectId,
    retry: false,
  });

  const { data: issues = [], isLoading: issuesLoading } = useQuery({
    queryKey: ["github-issues", projectId],
    queryFn: () => githubApi.listIssues(projectId!),
    enabled: !!projectId && !!settings,
  });

  // ── Mutations ────────────────────────────────────────────────────────────────
  const saveMutation = useMutation({
    mutationFn: (body: GitHubSettingUpsert) =>
      githubApi.saveSettings(projectId!, body),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["github-settings", projectId] });
      queryClient.invalidateQueries({ queryKey: ["github-issues", projectId] });
      // Clear sensitive form fields after save
      setToken("");
      setOwner("");
      setRepo("");
    },
  });

  const issuesMutation = useMutation({
    mutationFn: () => githubApi.createIssues(projectId!),
    onSuccess: () =>
      queryClient.invalidateQueries({ queryKey: ["github-issues", projectId] }),
  });

  const branchMutation = useMutation({
    mutationFn: () =>
      githubApi.createBranch(projectId!, branchName),
    onSuccess: () => setBranchName(""),
  });

  // ── Derived ──────────────────────────────────────────────────────────────────
  const isConnected = !!settings;
  const canSave = owner.trim() && repo.trim() && token.trim() && !saveMutation.isPending;

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <button onClick={() => navigate(-1)} className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </button>
        <div>
          <h2 className="text-lg font-semibold flex items-center gap-2">
            <Github className="h-5 w-5" /> GitHub Integration
          </h2>
          <p className="text-sm text-muted-foreground">
            Connect a GitHub repository and push AI-generated tasks as issues.
          </p>
        </div>
      </div>

      {/* ── Connection status ────────────────────────────────────────────────── */}
      {settingsLoading ? (
        <p className="text-sm text-muted-foreground">Loading…</p>
      ) : isConnected ? (
        <div className="rounded-lg border border-green-300 bg-green-50 p-4 flex items-center justify-between">
          <div className="flex items-center gap-2 text-green-700">
            <CheckCircle2 className="h-4 w-4" />
            <span className="text-sm font-medium">
              Connected to{" "}
              <a
                href={settings.repo_url}
                target="_blank"
                rel="noreferrer"
                className="underline underline-offset-2"
              >
                {settings.repo_owner}/{settings.repo_name}
              </a>
            </span>
          </div>
          <span className="text-xs text-muted-foreground">
            Branch: {settings.default_branch}
          </span>
        </div>
      ) : null}

      {/* ── Settings form ────────────────────────────────────────────────────── */}
      <section className="space-y-4">
        <h3 className="text-sm font-semibold text-foreground">
          {isConnected ? "Update Connection" : "Connect Repository"}
        </h3>
        <div className="grid gap-3 sm:grid-cols-2">
          <div className="space-y-1">
            <label className="text-xs font-medium">Repository Owner</label>
            <input
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
              placeholder={settings?.repo_owner ?? "e.g. tanaratk"}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
          <div className="space-y-1">
            <label className="text-xs font-medium">Repository Name</label>
            <input
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              placeholder={settings?.repo_name ?? "e.g. my-project"}
              className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>
        <div className="space-y-1">
          <label className="text-xs font-medium">
            Personal Access Token (PAT)
            <span className="ml-2 text-muted-foreground font-normal">
              — needs <code className="text-xs">repo</code> scope
            </span>
          </label>
          <div className="flex gap-2">
            <input
              type={showToken ? "text" : "password"}
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
              className="flex-1 rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring font-mono"
            />
            <button
              type="button"
              onClick={() => setShowToken((v) => !v)}
              className="rounded-md border px-3 py-2 text-xs hover:bg-accent"
            >
              {showToken ? "Hide" : "Show"}
            </button>
          </div>
        </div>
        {saveMutation.isError && (
          <div className="flex items-start gap-2 rounded-md border border-destructive/40 bg-red-50 p-3 text-sm text-destructive">
            <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
            {saveMutation.error instanceof Error
              ? saveMutation.error.message
              : "Connection failed."}
          </div>
        )}
        {saveMutation.isSuccess && (
          <p className="text-sm text-green-700 flex items-center gap-1.5">
            <CheckCircle2 className="h-4 w-4" /> Repository connected successfully.
          </p>
        )}
        <button
          onClick={() => saveMutation.mutate({ repo_owner: owner, repo_name: repo, access_token: token })}
          disabled={!canSave}
          className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {saveMutation.isPending && <Loader2 className="h-4 w-4 animate-spin" />}
          {saveMutation.isPending ? "Connecting…" : isConnected ? "Update Connection" : "Connect Repository"}
        </button>
      </section>

      {/* ── Create Issues ────────────────────────────────────────────────────── */}
      {isConnected && (
        <section className="space-y-4 border-t pt-6">
          <div>
            <h3 className="text-sm font-semibold">Push Tasks as GitHub Issues</h3>
            <p className="text-xs text-muted-foreground mt-0.5">
              Reads the Developer Agent's code task list and creates one GitHub issue per
              task. Skips tasks that were already pushed. Labels: <code>ai-sdlc</code>,{" "}
              <code>needs-review</code>.
            </p>
          </div>
          {issuesMutation.isSuccess && issuesMutation.data && (
            <div className="rounded-md border border-green-300 bg-green-50 p-3 text-sm text-green-800 space-y-1">
              <p className="font-medium">
                {issuesMutation.data.created} issue(s) created
                {issuesMutation.data.skipped > 0 &&
                  `, ${issuesMutation.data.skipped} skipped (already pushed)`}
              </p>
              {issuesMutation.data.errors.length > 0 && (
                <ul className="text-xs text-destructive list-disc pl-4">
                  {issuesMutation.data.errors.map((e, i) => <li key={i}>{e}</li>)}
                </ul>
              )}
            </div>
          )}
          {issuesMutation.isError && (
            <div className="flex items-start gap-2 rounded-md border border-destructive/40 bg-red-50 p-3 text-sm text-destructive">
              <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
              {issuesMutation.error instanceof Error
                ? issuesMutation.error.message
                : "Failed to create issues."}
            </div>
          )}
          <button
            onClick={() => issuesMutation.mutate()}
            disabled={issuesMutation.isPending}
            className="flex items-center gap-2 rounded-md bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {issuesMutation.isPending
              ? <><Loader2 className="h-4 w-4 animate-spin" /> Creating issues…</>
              : <><Github className="h-4 w-4" /> Push Tasks to GitHub</>}
          </button>
        </section>
      )}

      {/* ── Create Branch ────────────────────────────────────────────────────── */}
      {isConnected && (
        <section className="space-y-3 border-t pt-6">
          <h3 className="text-sm font-semibold">Create Branch</h3>
          <div className="flex gap-2">
            <input
              value={branchName}
              onChange={(e) => setBranchName(e.target.value)}
              placeholder={`feature/ai-sdlc-sprint-1`}
              className="flex-1 rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring font-mono"
            />
            <button
              onClick={() => branchMutation.mutate()}
              disabled={!branchName.trim() || branchMutation.isPending}
              className="flex items-center gap-2 rounded-md border px-4 py-2 text-sm hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {branchMutation.isPending
                ? <Loader2 className="h-4 w-4 animate-spin" />
                : <GitBranch className="h-4 w-4" />}
              Create
            </button>
          </div>
          {branchMutation.isSuccess && branchMutation.data && (
            <p className="text-sm text-green-700 flex items-center gap-1.5">
              <CheckCircle2 className="h-4 w-4" />
              Branch <code className="font-mono">{branchMutation.data.branch}</code> created.
            </p>
          )}
          {branchMutation.isError && (
            <p className="text-sm text-destructive">
              {branchMutation.error instanceof Error
                ? branchMutation.error.message
                : "Failed to create branch."}
            </p>
          )}
        </section>
      )}

      {/* ── Issue list ───────────────────────────────────────────────────────── */}
      {isConnected && (
        <section className="space-y-3 border-t pt-6">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold">
              Pushed Issues ({issues.length})
            </h3>
            <button
              onClick={() =>
                queryClient.invalidateQueries({ queryKey: ["github-issues", projectId] })
              }
              className="text-muted-foreground hover:text-foreground"
              title="Refresh"
            >
              <RefreshCw className="h-3.5 w-3.5" />
            </button>
          </div>
          {issuesLoading ? (
            <p className="text-sm text-muted-foreground">Loading…</p>
          ) : issues.length === 0 ? (
            <p className="text-sm text-muted-foreground">
              No issues pushed yet. Click "Push Tasks to GitHub" above.
            </p>
          ) : (
            <ul className="space-y-2">
              {issues.map((issue) => (
                <li
                  key={issue.id}
                  className="flex items-start justify-between rounded-md border bg-accent/20 p-3"
                >
                  <div className="space-y-0.5">
                    <p className="text-sm font-medium">
                      #{issue.issue_number} — {issue.title}
                    </p>
                    {issue.requirement_ids && (
                      <p className="text-xs text-muted-foreground">
                        Requirements: {issue.requirement_ids}
                      </p>
                    )}
                  </div>
                  <a
                    href={issue.issue_url}
                    target="_blank"
                    rel="noreferrer"
                    className="ml-3 shrink-0 text-muted-foreground hover:text-foreground"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </li>
              ))}
            </ul>
          )}
        </section>
      )}
    </div>
  );
}
