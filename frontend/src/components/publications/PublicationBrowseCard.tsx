import {
  ArrowRight,
  CalendarDays,
  FileText,
  Fingerprint,
} from "lucide-react";
import { Link } from "react-router";
import type { PublicationRecord } from "../../types/publication";
import { Card } from "../ui/Card";

function excerpt(text?: string) {
  if (!text) return "No abstract is available for this publication.";
  const clean = text.replace(/\s+/g, " ").trim();
  return clean.length > 260 ? `${clean.slice(0, 257).trimEnd()}…` : clean;
}

export function PublicationBrowseCard({
  publication,
}: {
  publication: PublicationRecord;
}) {
  const detailAvailable = publication.id !== undefined;

  return (
    <Card className="p-6 transition hover:border-[var(--border-strong)] hover:shadow-[var(--shadow-hover)]">
      <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--text-faint)]">
        {publication.year && (
          <span className="inline-flex items-center gap-1">
            <CalendarDays size={12} />
            {publication.year}
          </span>
        )}
        {publication.outputType && (
          <span className="inline-flex items-center gap-1">
            <FileText size={12} />
            {publication.outputType}
          </span>
        )}
      </div>

      <h2 className="mt-4 text-xl font-bold leading-7 tracking-[-0.02em]">
        {detailAvailable ? (
          <Link
            to={`/publications/${publication.id}`}
            state={{ from: "/publications" }}
            className="transition hover:text-[var(--accent)]"
          >
            {publication.title}
          </Link>
        ) : (
          publication.title
        )}
      </h2>

      <div className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
        {publication.authors.length > 0
          ? publication.authors.map((author) => author.name).join(", ")
          : "Author unavailable"}
      </div>

      <p className="mt-4 text-sm leading-6 text-[var(--text-muted)]">
        {excerpt(publication.abstract)}
      </p>

      {publication.keywords.length > 0 && (
        <div className="mt-5 flex flex-wrap gap-2">
          {publication.keywords.slice(0, 5).map((keyword) => (
            <span
              key={keyword}
              className="rounded-full bg-[var(--surface-muted)] px-2.5 py-1 text-[11px] font-semibold text-[var(--text-muted)]"
            >
              {keyword}
            </span>
          ))}
        </div>
      )}

      <div className="mt-6 flex flex-wrap items-center gap-4">
        {detailAvailable && (
          <Link
            to={`/publications/${publication.id}`}
            state={{ from: "/publications" }}
            className="inline-flex items-center gap-1.5 text-xs font-bold text-[var(--ink)] transition hover:text-[var(--accent)]"
          >
            View details <ArrowRight size={14} />
          </Link>
        )}

        {publication.doi && (
          <span
            title={`DOI: ${publication.doi}`}
            className="inline-flex items-center gap-1.5 text-xs text-[var(--text-faint)]"
          >
            <Fingerprint size={13} />
            DOI {publication.doi}
          </span>
        )}
      </div>
    </Card>
  );
}
