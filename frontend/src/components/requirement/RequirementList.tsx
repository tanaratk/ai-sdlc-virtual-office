import { useState } from "react";
import { ChevronDown, ChevronUp, FileText, Hash, Trash2 } from "lucide-react";
import type { InputType, RequirementInput } from "@/types/requirement";

const TYPE_LABELS: Record<InputType, string> = {
  manual_text: "Manual Text",
  meeting_transcript: "Meeting Transcript",
  chat_log: "Chat Log",
  markdown_document: "Markdown Document",
  email_content: "Email",
  audio_transcript: "Audio Transcript",
};

const TYPE_COLORS: Record<InputType, string> = {
  manual_text: "bg-gray-100 text-gray-700",
  meeting_transcript: "bg-blue-100 text-blue-700",
  chat_log: "bg-purple-100 text-purple-700",
  markdown_document: "bg-green-100 text-green-700",
  email_content: "bg-orange-100 text-orange-700",
  audio_transcript: "bg-yellow-100 text-yellow-700",
};

interface RequirementListProps {
  inputs: RequirementInput[];
  onDelete?: (id: string) => void;
}

function RequirementItem({
  input,
  onDelete,
}: {
  input: RequirementInput;
  onDelete?: (id: string) => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const charCount = input.content.length;
  const lineCount = input.content.split("\n").length;
  const isLong = charCount > 300;

  return (
    <li className="rounded-lg border bg-white overflow-hidden">
      <div className="flex items-start gap-3 p-3">
        <FileText className="mt-0.5 h-4 w-4 flex-shrink-0 text-primary" />
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <p className="text-sm font-medium truncate">
              {input.title ?? "(no title)"}
            </p>
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${TYPE_COLORS[input.input_type]}`}>
              {TYPE_LABELS[input.input_type]}
            </span>
          </div>
          <div className="flex items-center gap-2 mt-0.5 text-xs text-muted-foreground">
            <span>{new Date(input.created_at).toLocaleDateString()}</span>
            <span>·</span>
            <span className="flex items-center gap-0.5">
              <Hash className="h-3 w-3" />
              {charCount.toLocaleString()} chars · {lineCount} lines
            </span>
          </div>

          <div className="mt-2">
            <pre
              className={`whitespace-pre-wrap font-mono text-xs text-muted-foreground leading-relaxed ${
                !expanded && isLong ? "line-clamp-3" : ""
              }`}
            >
              {input.content}
            </pre>
            {isLong && (
              <button
                onClick={() => setExpanded(!expanded)}
                className="mt-1 flex items-center gap-1 text-xs text-primary hover:underline"
              >
                {expanded ? (
                  <>
                    <ChevronUp className="h-3 w-3" /> Collapse
                  </>
                ) : (
                  <>
                    <ChevronDown className="h-3 w-3" /> Show full content
                  </>
                )}
              </button>
            )}
          </div>
        </div>

        {onDelete && (
          <button
            onClick={() => onDelete(input.id)}
            className="flex-shrink-0 text-muted-foreground hover:text-destructive"
            aria-label="Delete"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        )}
      </div>
    </li>
  );
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
        <RequirementItem key={input.id} input={input} onDelete={onDelete} />
      ))}
    </ul>
  );
}
