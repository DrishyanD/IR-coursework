import { ExternalLink } from "lucide-react";
import type { SearchAuthor } from "../../types/search";

type AuthorListProps = {
  authors: SearchAuthor[];
};

export function AuthorList({ authors }: AuthorListProps) {
  if (authors.length === 0) {
    return <span className="text-[var(--text-faint)]">Author unavailable</span>;
  }

  return (
    <span>
      {authors.map((author, index) => (
        <span key={`${author.name}-${index}`}>
          {index > 0 && <span className="text-[var(--text-faint)]">, </span>}
          {author.profileUrl ? (
            <a
              href={author.profileUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex items-center gap-0.5 font-medium text-[var(--text-muted)] underline decoration-transparent underline-offset-2 transition hover:text-[var(--accent)] hover:decoration-current"
              onClick={(event) => event.stopPropagation()}
            >
              {author.name}
              <ExternalLink size={10} aria-hidden="true" />
            </a>
          ) : (
            <span className="font-medium text-[var(--text-muted)]">
              {author.name}
            </span>
          )}
        </span>
      ))}
    </span>
  );
}
