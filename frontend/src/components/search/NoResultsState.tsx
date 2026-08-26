import { SearchX } from "lucide-react";

export function NoResultsState({ query }: { query: string }) {
  return (
    <div className="grid min-h-[340px] place-items-center py-14 text-center">
      <div className="max-w-md">
        <div className="mx-auto grid h-13 w-13 place-items-center rounded-2xl bg-[var(--surface-muted)] text-[var(--text-muted)]">
          <SearchX size={22} />
        </div>
        <h2 className="mt-5 text-lg font-bold text-[var(--ink)]">
          No matching publications
        </h2>
        <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
          Nothing in the current index matched “{query}”. Try a broader topic,
          an author surname or fewer terms.
        </p>
      </div>
    </div>
  );
}
