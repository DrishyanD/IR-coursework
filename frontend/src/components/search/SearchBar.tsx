import { ArrowRight, Search } from "lucide-react";
import { FormEvent, useEffect, useState } from "react";
import { useNavigate } from "react-router";

type SearchBarProps = {
  defaultValue?: string;
  compact?: boolean;
};

export function SearchBar({
  defaultValue = "",
  compact = false,
}: SearchBarProps) {
  const [query, setQuery] = useState(defaultValue);
  const navigate = useNavigate();

  useEffect(() => {
    setQuery(defaultValue);
  }, [defaultValue]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const value = query.trim();
    if (!value) return;
    navigate(`/search?q=${encodeURIComponent(value)}`);
  };

  return (
    <form onSubmit={submit} role="search" className="w-full">
      <label className="sr-only" htmlFor={compact ? "research-search-compact" : "research-search"}>
        Search publications, authors or research topics
      </label>

      <div
        className={`group flex items-center gap-3 border border-[var(--border-strong)] bg-[var(--surface)] shadow-[var(--shadow-search)] transition focus-within:border-[var(--accent)] focus-within:ring-4 focus-within:ring-[var(--accent-soft)] ${
          compact
            ? "rounded-2xl px-4 py-2.5"
            : "rounded-[20px] px-5 py-3.5 sm:px-6 sm:py-4"
        }`}
      >
        <Search
          size={compact ? 18 : 20}
          className="shrink-0 text-[var(--text-faint)] transition group-focus-within:text-[var(--accent)]"
          aria-hidden="true"
        />

        <input
          id={compact ? "research-search-compact" : "research-search"}
          data-global-search="true"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          className={`min-w-0 flex-1 bg-transparent text-[var(--ink)] outline-none placeholder:text-[var(--text-faint)] ${
            compact ? "text-sm" : "text-[16px] sm:text-[17px]"
          }`}
          placeholder="Search publications, authors or research topics..."
          autoComplete="off"
          autoCapitalize="none"
          spellCheck={false}
          enterKeyHint="search"
        />

        <kbd className="hidden rounded-md border border-[var(--border)] bg-[var(--surface-muted)] px-1.5 py-0.5 font-mono text-[10px] font-semibold text-[var(--text-faint)] md:inline-flex">
          /
        </kbd>

        <button
          type="submit"
          aria-label="Search"
          className={`grid shrink-0 place-items-center rounded-xl bg-[var(--ink)] text-[var(--surface)] transition hover:translate-x-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent)] ${
            compact ? "h-9 w-9" : "h-10 w-10"
          }`}
        >
          <ArrowRight size={18} />
        </button>
      </div>
    </form>
  );
}
