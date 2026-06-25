import { useEffect, useRef, useState } from "react";
import mermaid from "mermaid";

mermaid.initialize({
  startOnLoad: false,
  theme: "default",
  securityLevel: "loose",
  fontFamily: "ui-monospace, monospace",
});

let _counter = 0;

interface Props {
  code: string;
  className?: string;
}

export default function MermaidChart({ code, className }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!ref.current || !code.trim()) return;
    const id = `mermaid-${++_counter}`;
    setError(null);

    mermaid
      .render(id, code)
      .then(({ svg }) => {
        if (ref.current) ref.current.innerHTML = svg;
      })
      .catch((err: unknown) => {
        const msg = err instanceof Error ? err.message : String(err);
        setError(msg);
      });
  }, [code]);

  if (error) {
    return (
      <div className="rounded-md border border-destructive/40 bg-red-50 p-3 text-xs text-destructive font-mono whitespace-pre-wrap">
        {error}
      </div>
    );
  }

  return <div ref={ref} className={className} />;
}
