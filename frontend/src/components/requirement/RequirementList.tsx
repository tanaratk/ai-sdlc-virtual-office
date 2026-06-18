import { FileText, Trash2 } from "lucide-react";
import type { RequirementInput } from "@/types/requirement";

interface RequirementListProps {
  inputs: RequirementInput[];
  onDelete?: (id: string) => void;
}

export function RequirementList({ inputs, onDelete }: RequirementListProps) {
  if (inputs.length === 0) {
    return (
      <div className="rounded-lg border border-dashed p-6 text-center text-sm text-muted-foreground">
        No requirements uploaded yet.
      </div>
    );
  }

  return (
    <ul className="space-y-2">
      {inputs.map((input) => (
        <li
          key={input.id}
          className="flex items-start gap-3 rounded-lg border bg-white p-3"
        >
          <FileText className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">
              {input.title ?? "(no title)"}
            </p>
            <p className="text-xs text-muted-foreground">
              {input.input_type} · {new Date(input.created_at).toLocaleDateString()}
            </p>
            <p className="mt-1 text-xs text-muted-foreground line-clamp-2">
              {input.content}
            </p>
          </div>
          {onDelete && (
            <button
              onClick={() => onDelete(input.id)}
              className="text-muted-foreground hover:text-destructive"
              aria-label="Delete"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          )}
        </li>
      ))}
    </ul>
  );
}
