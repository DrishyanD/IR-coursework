import type { ReactNode } from "react";

export function MetadataRow({
  label,
  children,
}: {
  label: string;
  children: ReactNode;
}) {
  return (
    <div className="grid gap-1 border-b border-[var(--border)] py-4 last:border-b-0 sm:grid-cols-[150px_minmax(0,1fr)] sm:gap-5">
      <dt className="text-xs font-bold uppercase tracking-[0.11em] text-[var(--text-faint)]">
        {label}
      </dt>
      <dd className="m-0 min-w-0 text-sm leading-6 text-[var(--text-muted)]">
        {children}
      </dd>
    </div>
  );
}
