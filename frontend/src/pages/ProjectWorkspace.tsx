import { useQuery } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { ArrowLeft, Bot, Building2, FileText, GitBranch, Upload, Zap } from "lucide-react";
import { projectApi } from "@/services/projectApi";
import { sourceApi } from "@/services/sourceApi";

export default function ProjectWorkspace() {
  const { projectId } = useParams<{ projectId: string }>();

  const { data: project, isLoading } = useQuery({
    queryKey: ["project", projectId],
    queryFn: () => projectApi.get(projectId!),
    enabled: !!projectId,
  });

  const { data: inputs } = useQuery({
    queryKey: ["inputs", projectId],
    queryFn: () => sourceApi.list(projectId!),
    enabled: !!projectId,
  });

  if (isLoading) {
    return <p className="text-sm text-muted-foreground">Loading…</p>;
  }

  if (!project) {
    return <p className="text-sm text-destructive">Project not found.</p>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link to="/" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div>
          <h2 className="text-lg font-semibold">{project.name}</h2>
          {project.description && (
            <p className="text-sm text-muted-foreground">{project.description}</p>
          )}
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <Link
          to={`/projects/${projectId}/intake`}
          className="flex flex-col items-center gap-2 rounded-lg border bg-white p-6 text-center hover:border-primary transition-colors"
        >
          <Upload className="h-6 w-6 text-primary" />
          <span className="text-sm font-medium">Requirement Intake</span>
          <span className="text-xs text-muted-foreground">
            {inputs?.total ?? 0} input{(inputs?.total ?? 0) !== 1 ? "s" : ""}
          </span>
        </Link>

        <Link
          to={`/projects/${projectId}/agents`}
          className="flex flex-col items-center gap-2 rounded-lg border bg-white p-6 text-center hover:border-primary transition-colors"
        >
          <Bot className="h-6 w-6 text-primary" />
          <span className="text-sm font-medium">Agent Console</span>
          <span className="text-xs text-muted-foreground">Run pipeline</span>
        </Link>

        <Link
          to={`/projects/${projectId}/documents`}
          className="flex flex-col items-center gap-2 rounded-lg border bg-white p-6 text-center hover:border-primary transition-colors"
        >
          <FileText className="h-6 w-6 text-primary" />
          <span className="text-sm font-medium">Documents</span>
          <span className="text-xs text-muted-foreground">View generated docs</span>
        </Link>

        <Link
          to={`/projects/${projectId}/traceability`}
          className="flex flex-col items-center gap-2 rounded-lg border bg-white p-6 text-center hover:border-primary transition-colors"
        >
          <GitBranch className="h-6 w-6 text-primary" />
          <span className="text-sm font-medium">Traceability</span>
          <span className="text-xs text-muted-foreground">Coverage matrix</span>
        </Link>

        <Link
          to={`/projects/${projectId}/office`}
          className="flex flex-col items-center gap-2 rounded-lg border bg-white p-6 text-center hover:border-primary transition-colors"
        >
          <Building2 className="h-6 w-6 text-primary" />
          <span className="text-sm font-medium">Virtual Office</span>
          <span className="text-xs text-muted-foreground">Live agent status</span>
        </Link>

        <Link
          to={`/projects/${projectId}/change-impact`}
          className="flex flex-col items-center gap-2 rounded-lg border bg-white p-6 text-center hover:border-primary transition-colors"
        >
          <Zap className="h-6 w-6 text-primary" />
          <span className="text-sm font-medium">Change Impact</span>
          <span className="text-xs text-muted-foreground">Analyse requirement changes</span>
        </Link>
      </div>
    </div>
  );
}
