import { Check, Copy, Fingerprint } from "lucide-react";
import { useState } from "react";

export function DoiField({ doi }: { doi: string }) {
  const [copied, setCopied] = useState(false);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(doi);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="flex min-w-0 flex-wrap items-center gap-2">
      <span className="inline-flex min-w-0 items-center gap-1.5 font-mono text-xs text-[var(--ink)]">
        <Fingerprint size={13} className="shrink-0 text-[var(--accent)]" />
        <span className="break-all">{doi}</span>
      </span>

      <button
        type="button"
        onClick={copy}
        className="inline-flex items-center gap-1 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-2 py-1 text-[11px] font-semibold text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--ink)]"
      >
        {copied ? <Check size={12} /> : <Copy size={12} />}
        {copied ? "Copied" : "Copy"}
      </button>
    </div>
  );
}
