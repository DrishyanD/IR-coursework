import { ExternalLink, UserRound } from "lucide-react";
import type { PublicationAuthor } from "../../types/publication";

export function PublicationAuthors({
  authors,
}: {
  authors: PublicationAuthor[];
}) {
  if (authors.length === 0) {
    return (
      <span className="text-sm text-[var(--text-faint)]">
        Author information unavailable
      </span>
    );
  }

  return (
    <div className="grid gap-2">
      {authors.map((author, index) => (
        <div
          key={`${author.id ?? author.name}-${index}`}
          className="flex items-center gap-2"
        >
          <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-[var(--surface-muted)] text-[var(--text-faint)]">
            <UserRound size={14} />
          </div>
          {author.profileUrl ? (
            <a
              href={author.profileUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-1.5 text-sm font-semibold text-[var(--ink)] underline decoration-transparent underline-offset-2 transition hover:text-[var(--accent)] hover:decoration-current"
            >
              {author.name}
              <ExternalLink size={12} />
            </a>
          ) : (
            <span className="text-sm font-semibold text-[var(--ink)]">
              {author.name}
            </span>
          )}
        </div>
      ))}
    </div>
  );
}
