import { useRef, useState } from "react";
import { Paperclip, Upload } from "lucide-react";
import type { InputType, RequirementInputCreate } from "@/types/requirement";

const INPUT_TYPES: { value: InputType; label: string }[] = [
  { value: "manual_text", label: "Manual Text" },
  { value: "meeting_transcript", label: "Meeting Transcript" },
  { value: "chat_log", label: "Chat Log" },
  { value: "markdown_document", label: "Markdown Document" },
  { value: "email_content", label: "Email Content" },
  { value: "audio_transcript", label: "Audio Transcript" },
];

const EXT_TO_TYPE: Record<string, InputType> = {
  md: "markdown_document",
  markdown: "markdown_document",
  log: "chat_log",
  txt: "manual_text",
};

interface RequirementUploadProps {
  onSubmit: (data: RequirementInputCreate) => void;
  isLoading?: boolean;
}

export function RequirementUpload({ onSubmit, isLoading = false }: RequirementUploadProps) {
  const [inputType, setInputType] = useState<InputType>("manual_text");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [fileName, setFileName] = useState<string | null>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext = file.name.split(".").pop()?.toLowerCase() ?? "";
    const detectedType = EXT_TO_TYPE[ext];
    if (detectedType) setInputType(detectedType);

    if (!title) setTitle(file.name.replace(/\.[^.]+$/, ""));
    setFileName(file.name);

    const reader = new FileReader();
    reader.onload = (ev) => {
      setContent((ev.target?.result as string) ?? "");
    };
    reader.readAsText(file, "utf-8");

    e.target.value = "";
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!content.trim()) return;
    onSubmit({ input_type: inputType, title: title || undefined, content });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Input Type</label>
        <select
          value={inputType}
          onChange={(e) => setInputType(e.target.value as InputType)}
          className="w-full rounded-md border bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        >
          {INPUT_TYPES.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Title (optional)</label>
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="e.g. Kickoff meeting 2026-06-18"
          className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">Attach File</label>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => fileRef.current?.click()}
            className="flex items-center gap-2 rounded-md border px-3 py-2 text-sm hover:bg-accent"
          >
            <Paperclip className="h-4 w-4" />
            {fileName ? fileName : "Choose file…"}
          </button>
          {fileName && (
            <button
              type="button"
              onClick={() => { setFileName(null); setContent(""); }}
              className="text-xs text-muted-foreground hover:text-destructive"
            >
              Clear
            </button>
          )}
        </div>
        <p className="mt-1 text-xs text-muted-foreground">
          Supports .txt, .md, .log — content is loaded into the text area below.
        </p>
        <input
          ref={fileRef}
          type="file"
          accept=".txt,.md,.markdown,.log,.csv"
          onChange={handleFileSelect}
          className="hidden"
        />
      </div>

      <div>
        <label className="block text-sm font-medium mb-1">
          Content <span className="text-destructive">*</span>
        </label>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          rows={10}
          placeholder="Paste your requirement text here, or attach a file above…"
          className="w-full rounded-md border px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-ring resize-y"
          required
        />
      </div>

      <button
        type="submit"
        disabled={isLoading || !content.trim()}
        className="flex items-center gap-2 rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <Upload className="h-4 w-4" />
        {isLoading ? "Saving…" : "Save Requirement"}
      </button>
    </form>
  );
}
