import { BookOpenText, RefreshCcw } from "lucide-react";
import { PublicationBrowseCard } from "../components/publications/PublicationBrowseCard";
import { Button } from "../components/ui/Button";
import { Container } from "../components/ui/Container";
import { usePublications } from "../hooks/usePublications";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

export function PublicationsPage() {
  useDocumentTitle("Publications");
  const { data, loading, error, retry } = usePublications();

  return (
    <Container className="py-12 sm:py-16">
      <div className="max-w-3xl">
        <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.15em] text-[var(--accent)]">
          <BookOpenText size={13} />
          Research collection
        </div>
        <h1 className="mt-3 text-4xl font-bold tracking-[-0.04em]">
          Browse publications
        </h1>
        <p className="mt-4 max-w-2xl text-sm leading-7 text-[var(--text-muted)] sm:text-base">
          Explore publication records currently stored in the backend collection,
          independent of a search query.
        </p>
      </div>

      <div className="mt-10">
        {loading && (
          <div className="grid gap-4 md:grid-cols-2">
            {[1, 2, 3, 4].map((item) => (
              <div
                key={item}
                className="h-64 animate-pulse rounded-[22px] border border-[var(--border)] bg-[var(--surface-muted)]"
              />
            ))}
          </div>
        )}

        {!loading && error && (
          <div className="grid min-h-[360px] place-items-center text-center">
            <div className="max-w-md">
              <h2 className="text-lg font-bold">Collection unavailable</h2>
              <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
                {error}
              </p>
              <Button className="mt-6" variant="secondary" onClick={retry}>
                <RefreshCcw size={15} />
                Try again
              </Button>
            </div>
          </div>
        )}

        {!loading && !error && data && (
          <>
            <div className="mb-5 text-sm font-semibold text-[var(--ink)]">
              {data.total.toLocaleString()} publications
            </div>

            {data.items.length === 0 ? (
              <div className="rounded-2xl border border-dashed border-[var(--border-strong)] p-10 text-center text-sm text-[var(--text-muted)]">
                No publication records are currently stored.
              </div>
            ) : (
              <div className="grid gap-4 md:grid-cols-2">
                {data.items.map((publication, index) => (
                  <PublicationBrowseCard
                    key={
                      publication.id ??
                      publication.publicationUrl ??
                      `${publication.title}-${index}`
                    }
                    publication={publication}
                  />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </Container>
  );
}
