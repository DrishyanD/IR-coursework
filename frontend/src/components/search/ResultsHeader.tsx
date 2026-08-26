import { Clock3 } from "lucide-react";
import type { ReactNode } from "react";

type ResultsHeaderProps = {
  query: string;
  count: number;
  totalCount?: number;
  processingTimeMs?: number;
  controls?: ReactNode;
};

export function ResultsHeader({
  query,
  count,
  totalCount,
  processingTimeMs,
  controls,
}: ResultsHeaderProps) {
  const filtered = totalCount !== undefined && totalCount !== count;

  return (
    <div className="border-b border-[var(--border)] pb-5">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <div className="text-[13px] font-semibold text-[var(--ink)]">
            {count.toLocaleString()} {count === 1 ? "result" : "results"}
            {filtered && (
              <span className="font-medium text-[var(--text-faint)]">
                {" "}of {totalCount.toLocaleString()}
              </span>
            )}
          </div>
          <div className="mt-1 text-xs text-[var(--text-faint)]">
            Ranked for “{query}”
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {processingTimeMs !== undefined && (
            <span className="inline-flex items-center gap-1.5 text-xs font-medium text-[var(--text-faint)]">
              <Clock3 size={13} />
              {processingTimeMs < 1
                ? "<1 ms"
                : `${processingTimeMs.toFixed(1)} ms`}
            </span>
          )}
          {controls}
        </div>
      </div>
    </div>
  );
}
