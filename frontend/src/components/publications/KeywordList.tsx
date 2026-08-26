import { Link } from "react-router";

export function KeywordList({
  keywords,
}: {
  keywords: string[];
}) {
  if (keywords.length === 0) {
    return (
      <span className="text-sm text-[var(--text-faint)]">
        No keywords available
      </span>
    );
  }

  return (
    <div className="flex flex-wrap gap-2">
      {keywords.map((keyword) => (
        <Link
          key={keyword}
          to={`/search?q=${encodeURIComponent(keyword)}`}
          className="rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-xs font-semibold text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--accent)]"
          title={`Search for ${keyword}`}
        >
          {keyword}
        </Link>
      ))}
    </div>
  );
}
