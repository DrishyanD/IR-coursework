import { Search, UserRoundSearch } from "lucide-react";
import { Link } from "react-router";
import type { PublicationRecord } from "../../types/publication";
import { Card } from "../ui/Card";

export function PublicationActions({
  publication,
}: {
  publication: PublicationRecord;
}) {
  const firstAuthor = publication.authors[0]?.name;

  return (
    <Card className="p-5">
      <div className="text-xs font-bold uppercase tracking-[0.13em] text-[var(--text-faint)]">
        Continue exploring
      </div>

      <div className="mt-4 grid gap-2">
        {firstAuthor && (
          <Link
            to={`/search?q=${encodeURIComponent(firstAuthor)}`}
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-[var(--ink)] transition hover:bg-[var(--surface-muted)]"
          >
            <UserRoundSearch size={16} className="text-[var(--accent)]" />
            Search {firstAuthor}
          </Link>
        )}

        {publication.keywords[0] && (
          <Link
            to={`/search?q=${encodeURIComponent(publication.keywords[0])}`}
            className="flex items-center gap-3 rounded-xl px-3 py-3 text-sm font-semibold text-[var(--ink)] transition hover:bg-[var(--surface-muted)]"
          >
            <Search size={16} className="text-[var(--accent)]" />
            Search “{publication.keywords[0]}”
          </Link>
        )}
      </div>
    </Card>
  );
}
