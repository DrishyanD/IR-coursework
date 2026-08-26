import {
  ArrowUpRight,
  CalendarDays,
  FileText,
} from "lucide-react";
import type { PublicationRecord } from "../../types/publication";
import { Badge } from "../ui/Badge";

export function PublicationHero({
  publication,
}: {
  publication: PublicationRecord;
}) {
  return (
    <div>
      <div className="flex flex-wrap items-center gap-2">
        <Badge>Publication record</Badge>
        {publication.outputType && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--surface-muted)] px-3 py-1 text-xs font-semibold text-[var(--text-muted)]">
            <FileText size={12} />
            {publication.outputType}
          </span>
        )}
        {publication.year && (
          <span className="inline-flex items-center gap-1.5 rounded-full bg-[var(--surface-muted)] px-3 py-1 text-xs font-semibold text-[var(--text-muted)]">
            <CalendarDays size={12} />
            {publication.year}
          </span>
        )}
      </div>

      <h1 className="mt-6 max-w-[1000px] text-[clamp(2.2rem,5vw,4.5rem)] font-extrabold leading-[1.02] tracking-[-0.05em] text-[var(--ink)]">
        {publication.title}
      </h1>

      {publication.publicationUrl && (
        <a
          href={publication.publicationUrl}
          target="_blank"
          rel="noreferrer"
          className="mt-7 inline-flex items-center gap-2 text-sm font-bold text-[var(--ink)] transition hover:text-[var(--accent)]"
        >
          View original publication
          <ArrowUpRight size={15} />
        </a>
      )}
    </div>
  );
}
