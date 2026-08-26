import { useEffect, useState } from "react";
import { Search as SearchIcon, ChevronLeft, ChevronRight } from "lucide-react";
import { useSearchParams } from "react-router";
import { NoResultsState } from "../components/search/NoResultsState";
import { PublicationResultCard } from "../components/search/PublicationResultCard";
import { ResultsHeader } from "../components/search/ResultsHeader";
import { SearchBar } from "../components/search/SearchBar";
import { SearchErrorState } from "../components/search/SearchErrorState";
import { SearchResultsSkeleton } from "../components/search/SearchResultsSkeleton";
import { Container } from "../components/ui/Container";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { usePublicationSearch } from "../hooks/usePublicationSearch";

const RESULTS_PER_PAGE = 10;

export function SearchPage() {
  useDocumentTitle("Search");
  const [params] = useSearchParams();
  const query = (params.get("q") ?? "").trim();
  const { data, loading, error, retry } = usePublicationSearch(query);
  const results = data?.results ?? [];

  const [currentPage, setCurrentPage] = useState(1);

  // A new search should always start on the first page.
  useEffect(() => setCurrentPage(1), [query, results.length]);

  const totalPages = Math.max(1, Math.ceil(results.length / RESULTS_PER_PAGE));
  const startIdx = (currentPage - 1) * RESULTS_PER_PAGE;
  const pageResults = results.slice(startIdx, startIdx + RESULTS_PER_PAGE);

  return (
    <>
      <section className="border-b border-[var(--border)] bg-[var(--surface)]">
        <Container className="py-8 sm:py-10">
          <div className="mb-4 flex items-center gap-2 text-xs font-bold uppercase tracking-[0.15em] text-[var(--accent)]">
            <SearchIcon size={13} /> Publication search
          </div>
          <SearchBar defaultValue={query} compact />
        </Container>
      </section>

      <Container className="py-8 sm:py-10">
        {!query && <p className="text-sm text-[var(--text-muted)]">Enter keywords to search the indexed Coventry publications.</p>}
        {query && loading && <SearchResultsSkeleton />}
        {query && !loading && error && <SearchErrorState message={error} onRetry={retry} />}
        {query && !loading && !error && data && (
          <section aria-label="Search results" className="mx-auto max-w-4xl">
            <ResultsHeader
              query={data.query || query}
              count={results.length}
              processingTimeMs={data.processingTimeMs}
            />
            {results.length === 0 ? (
              <NoResultsState query={query} />
            ) : (
              <>
                <div>
                  {pageResults.map((result, index) => (
                    <PublicationResultCard
                      key={result.id ?? result.publicationUrl ?? `${result.title}-${index}`}
                      result={result}
                      rank={startIdx + index + 1}
                    />
                  ))}
                </div>

                {/* Only show page controls when there is more than one page. */}
                {totalPages > 1 && (
                  <div className="mt-8 flex items-center justify-center gap-3">
                    <button
                      onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                      disabled={currentPage === 1}
                      className="flex items-center gap-1 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-medium text-[var(--text-secondary)] transition-all hover:border-[var(--accent)] hover:text-[var(--accent)] disabled:pointer-events-none disabled:opacity-40"
                    >
                      <ChevronLeft size={16} /> Previous
                    </button>

                    <span className="min-w-[120px] text-center text-sm text-[var(--text-muted)]">
                      Page <strong className="text-[var(--text-primary)]">{currentPage}</strong> of{" "}
                      <strong className="text-[var(--text-primary)]">{totalPages}</strong>
                    </span>

                    <button
                      onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                      disabled={currentPage === totalPages}
                      className="flex items-center gap-1 rounded-lg border border-[var(--border)] bg-[var(--surface)] px-4 py-2 text-sm font-medium text-[var(--text-secondary)] transition-all hover:border-[var(--accent)] hover:text-[var(--accent)] disabled:pointer-events-none disabled:opacity-40"
                    >
                      Next <ChevronRight size={16} />
                    </button>
                  </div>
                )}

                <p className="mt-4 text-center text-xs text-[var(--text-muted)]">
                  Showing {startIdx + 1}{'\u2013'}{Math.min(startIdx + RESULTS_PER_PAGE, results.length)} of {results.length} results
                </p>
              </>
            )}
          </section>
        )}
      </Container>
    </>
  );
}
