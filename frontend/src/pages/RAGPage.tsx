import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import { ArrowLeft, Database, Search, Zap } from "lucide-react";
import { ragApi, ChunkResult, ChunkStats } from "@/services/ragApi";

export default function RAGPage() {
  const { projectId } = useParams<{ projectId: string }>();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<ChunkResult[] | null>(null);
  const [searchQuery, setSearchQuery] = useState("");

  const { data: stats, refetch: refetchStats } = useQuery<ChunkStats>({
    queryKey: ["rag-stats", projectId],
    queryFn: () => ragApi.stats(projectId!),
    enabled: !!projectId,
  });

  const ingestMutation = useMutation({
    mutationFn: () => ragApi.ingest(projectId!),
    onSuccess: () => {
      refetchStats();
      setResults(null);
    },
  });

  const searchMutation = useMutation({
    mutationFn: (q: string) => ragApi.search(projectId!, q),
    onSuccess: (data) => {
      setResults(data.results);
      setSearchQuery(data.query);
    },
  });

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim().length >= 3) {
      searchMutation.mutate(query.trim());
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <Link
          to={`/projects/${projectId}`}
          className="text-muted-foreground hover:text-foreground"
        >
          <ArrowLeft className="h-4 w-4" />
        </Link>
        <div>
          <h2 className="text-lg font-semibold">Knowledge Base (RAG)</h2>
          <p className="text-sm text-muted-foreground">
            Semantic search over all project documents
          </p>
        </div>
      </div>

      {/* Stats + Ingest */}
      <div className="rounded-lg border bg-white p-5 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <Database className="h-4 w-4" />
            {stats && stats.total_chunks > 0 ? (
              <span>
                <strong className="text-foreground">{stats.total_chunks}</strong> chunks
                {stats.document_types.length > 0 && (
                  <> &mdash; {stats.document_types.join(", ")}</>
                )}
              </span>
            ) : (
              <span>Not yet ingested</span>
            )}
          </div>
          <button
            onClick={() => ingestMutation.mutate()}
            disabled={ingestMutation.isPending}
            className="flex items-center gap-1.5 rounded-md bg-primary px-3 py-1.5 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
          >
            <Zap className="h-3.5 w-3.5" />
            {ingestMutation.isPending ? "Ingesting…" : "Ingest Documents"}
          </button>
        </div>

        {ingestMutation.isSuccess && (
          <p className="text-sm text-green-700 bg-green-50 rounded px-3 py-2">
            {ingestMutation.data.message}
          </p>
        )}
        {ingestMutation.isError && (
          <p className="text-sm text-destructive bg-destructive/10 rounded px-3 py-2">
            {(ingestMutation.error as Error).message}
          </p>
        )}
      </div>

      {/* Search */}
      <div className="rounded-lg border bg-white p-5 space-y-4">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search across project documents…"
            className="flex-1 rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
            minLength={3}
          />
          <button
            type="submit"
            disabled={searchMutation.isPending || query.trim().length < 3}
            className="flex items-center gap-1.5 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-60"
          >
            <Search className="h-3.5 w-3.5" />
            {searchMutation.isPending ? "Searching…" : "Search"}
          </button>
        </form>

        {searchMutation.isError && (
          <p className="text-sm text-destructive">
            {(searchMutation.error as Error).message}
          </p>
        )}

        {results !== null && (
          <div className="space-y-3">
            <p className="text-xs text-muted-foreground">
              {results.length} result{results.length !== 1 ? "s" : ""} for &ldquo;{searchQuery}&rdquo;
            </p>
            {results.length === 0 ? (
              <p className="text-sm text-muted-foreground">
                No matching chunks found. Try ingesting documents first.
              </p>
            ) : (
              results.map((r) => (
                <div
                  key={r.chunk_id}
                  className="rounded-md border p-4 space-y-1.5"
                >
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span className="rounded bg-muted px-1.5 py-0.5 font-mono">
                      {r.document_type}
                    </span>
                    <span>score: {r.score.toFixed(3)}</span>
                  </div>
                  <p className="text-sm leading-relaxed line-clamp-4">{r.chunk_text}</p>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
