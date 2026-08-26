import { ArrowRight, Eraser, FileInput, Link as LinkIcon } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { ExampleDocuments } from "./ExampleDocuments";

export function DocumentInputCard({
  disabled,
  busy,
  onSubmit,
  onSubmitUrl,
}: {
  disabled?: boolean;
  busy?: boolean;
  onSubmit: (text: string) => void;
  onSubmitUrl: (url: string) => void;
}) {
  const [text, setText] = useState("");
  const [mode, setMode] = useState<"text" | "url">("text");
  const [error, setError] = useState<string | null>(null);

  const words = useMemo(
    () => text.trim().split(/\s+/).filter(Boolean).length,
    [text],
  );

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const clean = text.trim();

    if (!clean) {
      setError("Paste or type a document first.");
      return;
    }

    if (mode === "url") {
      try {
        const url = new URL(clean);
        if (url.protocol !== "https:" || !/(^|\.)bbc\.(com|co\.uk)$/.test(url.hostname)) {
          throw new Error();
        }
      } catch {
        setError("Enter a valid HTTPS BBC News article URL.");
        return;
      }
      setError(null);
      onSubmitUrl(clean);
      return;
    }

    if (clean.length < 20) {
      setError("Enter a little more text so the model has meaningful terms to compare.");
      return;
    }

    setError(null);
    onSubmit(clean);
  };

  return (
    <Card className="p-5 sm:p-6">
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-bold uppercase tracking-[0.13em] text-[var(--accent)]">
            New document
          </div>
          <h2 className="mt-2 text-xl font-bold tracking-[-0.025em]">
            What topic cluster does it resemble?
          </h2>
        </div>
        <div className="grid h-10 w-10 shrink-0 place-items-center rounded-2xl bg-[var(--surface-muted)] text-[var(--accent)]">
          <FileInput size={18} />
        </div>
      </div>

      <form onSubmit={submit} className="mt-6">
        <div className="mb-4 flex gap-2">
          <Button type="button" variant={mode === "text" ? "primary" : "secondary"} onClick={() => { setMode("text"); setText(""); setError(null); }}>
            <FileInput size={14} /> Text
          </Button>
          <Button type="button" variant={mode === "url" ? "primary" : "secondary"} onClick={() => { setMode("url"); setText(""); setError(null); }}>
            <LinkIcon size={14} /> BBC article URL
          </Button>
        </div>
        <label className="sr-only" htmlFor="cluster-document">
          {mode === "text" ? "Document text" : "BBC article URL"}
        </label>

        <textarea
          id="cluster-document"
          value={text}
          onChange={(event) => {
            setText(event.target.value);
            if (error) setError(null);
          }}
          disabled={disabled || busy}
          placeholder={mode === "text" ? "Paste or type a document here..." : "https://www.bbc.com/news/articles/..."}
          className={`${mode === "text" ? "min-h-[260px] resize-y" : "min-h-[90px] resize-none"} w-full rounded-2xl border border-[var(--border-strong)] bg-[var(--surface)] p-4 text-sm leading-7 text-[var(--ink)] outline-none transition placeholder:text-[var(--text-faint)] focus:border-[var(--accent)] focus:ring-4 focus:ring-[var(--accent-soft)] disabled:cursor-not-allowed disabled:opacity-60`}
        />

        <div className="mt-2 flex flex-wrap items-center justify-between gap-2 text-[11px] text-[var(--text-faint)]">
          <span>{mode === "text" ? `${words.toLocaleString()} words` : "BBC News links only"}</span>
          <span>{text.length.toLocaleString()} characters</span>
        </div>

        {error && (
          <p className="mt-3 text-xs font-semibold text-red-600">
            {error}
          </p>
        )}

        <div className="mt-5 flex flex-wrap items-center justify-between gap-3">
          <Button
            type="button"
            variant="ghost"
            disabled={!text || busy}
            onClick={() => {
              setText("");
              setError(null);
            }}
          >
            <Eraser size={14} />
            Clear
          </Button>

          <Button type="submit" disabled={disabled || busy}>
            {busy ? "Assigning cluster..." : mode === "url" ? "Fetch and assign" : "Assign cluster"}
            <ArrowRight size={14} />
          </Button>
        </div>
      </form>

      {mode === "text" && <div className="mt-7 border-t border-[var(--border)] pt-6">
        <ExampleDocuments
          onSelect={(value) => {
            setText(value);
            setError(null);
          }}
        />
      </div>}
    </Card>
  );
}
