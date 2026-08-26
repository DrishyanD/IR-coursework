type RelevanceScoreProps = {
  score: number;
};

function clampScore(score: number) {
  if (!Number.isFinite(score)) return 0;
  return Math.min(1, Math.max(0, score));
}

export function RelevanceScore({ score }: RelevanceScoreProps) {
  const normalized = clampScore(score);
  const percentage = normalized * 100;

  return (
    <div
      className="flex min-w-[90px] items-center gap-2"
      aria-label={`Relevance score ${score.toFixed(4)}`}
      title={`Cosine relevance score: ${score.toFixed(4)}`}
    >
      <div className="h-1.5 min-w-10 flex-1 overflow-hidden rounded-full bg-[var(--surface-muted)]">
        <div
          className="h-full rounded-full bg-[var(--accent)]"
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="font-mono text-[11px] font-semibold tabular-nums text-[var(--text-faint)]">
        {score.toFixed(3)}
      </span>
    </div>
  );
}
