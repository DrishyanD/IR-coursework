import {
  ArrowRight,
  ArrowUpRight,
  CalendarDays,
  FileText,
  Fingerprint,
} from "lucide-react";
import { Link, useLocation } from "react-router";
import type { PublicationSearchResult } from "../../types/search";
import { AuthorList } from "./AuthorList";
import { RelevanceScore } from "./RelevanceScore";

type PublicationResultCardProps = {
  result: PublicationSearchResult;
  rank: number;
};

function formatPublicationDate(value: string) {
  const fullDate = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value);
  if (fullDate) {
    const [, year, month, day] = fullDate;
    const date = new Date(Date.UTC(Number(year), Number(month) - 1, Number(day)));
    return new Intl.DateTimeFormat("en-GB", {
      day: "numeric",
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    }).format(date);
  }

  const monthOnly = /^(\d{4})-(\d{2})$/.exec(value);
  if (monthOnly) {
    const [, year, month] = monthOnly;
    const date = new Date(Date.UTC(Number(year), Number(month) - 1, 1));
    return new Intl.DateTimeFormat("en-GB", {
      month: "short",
      year: "numeric",
      timeZone: "UTC",
    }).format(date);
  }

  return value;
}

function doiUrl(doi: string) {
  const normalized = doi
    .trim()
    .replace(/^https?:\/\/(?:dx\.)?doi\.org\//i, "")
    .replace(/^doi:\s*/i, "");
  return `https://doi.org/${normalized}`;
}

function getExcerpt(result: PublicationSearchResult) {
  const text = result.snippet || result.abstract;
  if (!text) return "No abstract or matched snippet is available for this publication.";

  const normalized = text.replace(/\s+/g, " ").trim();
  return normalized.length > 360
    ? `${normalized.slice(0, 357).trimEnd()}…`
    : normalized;
}

export function PublicationResultCard({
  result,
  rank,
}: PublicationResultCardProps) {
  const location = useLocation();
  const detailAvailable = result.id !== undefined;

  const title = (
    <span className="text-[18px] font-bold leading-7 tracking-[-0.02em] text-[var(--ink)] transition group-hover:text-[var(--accent)] sm:text-[19px]">
      {result.title}
    </span>
  );

  return (
    <article className="group relative border-b border-[var(--border)] py-7 first:pt-1 last:border-b-0 sm:py-8">
      <div className="grid gap-4 sm:grid-cols-[34px_minmax(0,1fr)]">
        <div className="hidden pt-1 sm:block">
          <span className="font-mono text-xs font-semibold text-[var(--text-faint)]">
            {String(rank).padStart(2, "0")}
          </span>
        </div>

        <div className="min-w-0">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div className="min-w-0">
              {detailAvailable ? (
                <Link
                  to={`/publications/${result.id}`}
                  state={{
                    from: `${location.pathname}${location.search}`,
                  }}
                  className="rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
                >
                  {title}
                </Link>
              ) : result.publicationUrl ? (
                <a
                  href={result.publicationUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)]"
                >
                  {title}
                </a>
              ) : (
                <h2>{title}</h2>
              )}

              <div className="mt-2 flex flex-wrap items-center gap-x-2 gap-y-1 text-[13px] leading-5">
                <AuthorList authors={result.authors} />
                {(result.publicationDate || result.year) && (
                  <>
                    <span aria-hidden="true" className="text-[var(--border-strong)]">
                      ·
                    </span>
                    <span className="inline-flex items-center gap-1 text-[var(--text-faint)]">
                      <CalendarDays size={12} />
                      {result.publicationDate
                        ? `Published ${formatPublicationDate(result.publicationDate)}`
                        : result.year}
                    </span>
                  </>
                )}
                {result.outputType && (
                  <>
                    <span aria-hidden="true" className="text-[var(--border-strong)]">
                      ·
                    </span>
                    <span className="inline-flex items-center gap-1 text-[var(--text-faint)]">
                      <FileText size={12} />
                      {result.outputType}
                    </span>
                  </>
                )}
              </div>
            </div>

            <div className="shrink-0 lg:pt-1">
              <RelevanceScore score={result.score} />
            </div>
          </div>

          <p className="mt-4 max-w-[850px] text-[14px] leading-6 text-[var(--text-muted)]">
            {getExcerpt(result)}
          </p>

          <div className="mt-5 flex flex-wrap items-center gap-x-4 gap-y-2">
            {detailAvailable && (
              <Link
                to={`/publications/${result.id}`}
                state={{
                  from: `${location.pathname}${location.search}`,
                }}
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[var(--ink)] transition hover:text-[var(--accent)]"
              >
                View details <ArrowRight size={14} />
              </Link>
            )}

            {result.publicationUrl && (
              <a
                href={result.publicationUrl}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1.5 text-xs font-bold text-[var(--text-muted)] transition hover:text-[var(--accent)]"
              >
                PurePortal <ArrowUpRight size={14} />
              </a>
            )}

            {result.doi && (
              <a
                href={doiUrl(result.doi)}
                target="_blank"
                rel="noreferrer"
                className="inline-flex max-w-full items-center gap-1.5 truncate text-xs font-medium text-[var(--text-faint)] transition hover:text-[var(--accent)]"
                title={`Open DOI: ${result.doi}`}
              >
                <Fingerprint size={13} />
                DOI {result.doi} <ArrowUpRight size={12} />
              </a>
            )}
          </div>
        </div>
      </div>
    </article>
  );
}
