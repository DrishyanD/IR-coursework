import {
  ArrowLeft,
  Building2,
  RefreshCcw,
  Search,
} from "lucide-react";
import { Link, useLocation, useParams } from "react-router";
import { DoiField } from "../components/publications/DoiField";
import { KeywordList } from "../components/publications/KeywordList";
import { MetadataRow } from "../components/publications/MetadataRow";
import { PublicationActions } from "../components/publications/PublicationActions";
import { PublicationAuthors } from "../components/publications/PublicationAuthors";
import { PublicationHero } from "../components/publications/PublicationHero";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Container } from "../components/ui/Container";
import { usePublication } from "../hooks/usePublication";
import { useDocumentTitle } from "../hooks/useDocumentTitle";

function DetailSkeleton() {
  return (
    <Container className="py-12 sm:py-16">
      <div className="animate-pulse">
        <div className="h-7 w-44 rounded-full bg-[var(--surface-muted)]" />
        <div className="mt-8 h-14 w-[85%] rounded-2xl bg-[var(--surface-muted)]" />
        <div className="mt-4 h-14 w-[65%] rounded-2xl bg-[var(--surface-muted)]" />
        <div className="mt-12 grid gap-6 lg:grid-cols-[minmax(0,1fr)_380px]">
          <div className="h-[430px] rounded-[22px] bg-[var(--surface-muted)]" />
          <div className="h-[330px] rounded-[22px] bg-[var(--surface-muted)]" />
        </div>
      </div>
    </Container>
  );
}

export function PublicationDetailPage() {
  const { publicationId } = useParams();
  const location = useLocation();
  const { data, loading, error, notFound, retry } =
    usePublication(publicationId);
  useDocumentTitle(data?.title ?? "Publication");

  const backHref =
    typeof location.state === "object" &&
    location.state !== null &&
    "from" in location.state &&
    typeof (location.state as { from?: unknown }).from === "string"
      ? (location.state as { from: string }).from
      : "/publications";

  if (loading) return <DetailSkeleton />;

  if (notFound) {
    return (
      <Container className="grid min-h-[65vh] place-items-center py-20 text-center">
        <div className="max-w-md">
          <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-[var(--surface-muted)] text-[var(--text-muted)]">
            <Search size={20} />
          </div>
          <h1 className="mt-5 text-2xl font-bold">Publication not found</h1>
          <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
            The requested publication record is not available in the current
            collection.
          </p>
          <Link
            to="/publications"
            className="mt-6 inline-flex items-center gap-2 text-sm font-bold hover:text-[var(--accent)]"
          >
            <ArrowLeft size={15} />
            Browse publications
          </Link>
        </div>
      </Container>
    );
  }

  if (error || !data) {
    return (
      <Container className="grid min-h-[65vh] place-items-center py-20 text-center">
        <div className="max-w-md">
          <h1 className="text-xl font-bold">Publication unavailable</h1>
          <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
            {error ?? "The publication could not be displayed."}
          </p>
          <Button className="mt-6" variant="secondary" onClick={retry}>
            <RefreshCcw size={14} />
            Try again
          </Button>
        </div>
      </Container>
    );
  }

  return (
    <>
      <section className="border-b border-[var(--border)] bg-[var(--surface)]">
        <Container className="py-10 sm:py-14">
          <Link
            to={backHref}
            className="inline-flex items-center gap-2 text-xs font-bold text-[var(--text-muted)] transition hover:text-[var(--accent)]"
          >
            <ArrowLeft size={14} />
            Back
          </Link>

          <div className="mt-7">
            <PublicationHero publication={data} />
          </div>
        </Container>
      </section>

      <Container className="py-10 sm:py-14">
        <div className="grid gap-7 lg:grid-cols-[minmax(0,1fr)_380px] lg:items-start">
          <div className="space-y-7">
            <Card className="p-6 sm:p-8">
              <div className="text-xs font-bold uppercase tracking-[0.13em] text-[var(--accent)]">
                Abstract
              </div>
              <div className="mt-4 text-[15px] leading-8 text-[var(--text-muted)] sm:text-base">
                {data.abstract ? (
                  data.abstract
                ) : (
                  <span className="text-[var(--text-faint)]">
                    No abstract is available for this publication.
                  </span>
                )}
              </div>
            </Card>

            <Card className="p-6 sm:p-8">
              <div className="text-xs font-bold uppercase tracking-[0.13em] text-[var(--accent)]">
                Keywords
              </div>
              <div className="mt-5">
                <KeywordList keywords={data.keywords} />
              </div>
            </Card>
          </div>

          <aside className="space-y-5 lg:sticky lg:top-[104px]">
            <Card className="p-5 sm:p-6">
              <div className="text-xs font-bold uppercase tracking-[0.13em] text-[var(--text-faint)]">
                Publication details
              </div>

              <dl className="mt-3">
                <MetadataRow label="Authors">
                  <PublicationAuthors authors={data.authors} />
                </MetadataRow>

                {data.year && (
                  <MetadataRow label="Year">{data.year}</MetadataRow>
                )}

                {data.outputType && (
                  <MetadataRow label="Output type">
                    {data.outputType}
                  </MetadataRow>
                )}

                {data.doi && (
                  <MetadataRow label="DOI">
                    <DoiField doi={data.doi} />
                  </MetadataRow>
                )}

                <MetadataRow label="Organisation">
                  {data.organisations.length > 0 ? (
                    <div className="grid gap-2">
                      {data.organisations.map((organisation, index) => {
                        const url = data.organisationUrls[index];
                        return url ? (
                          <a
                            key={`${organisation}-${index}`}
                            href={url}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-start gap-1.5 font-medium text-[var(--ink)] hover:text-[var(--accent)]"
                          >
                            <Building2 size={13} className="mt-1 shrink-0" />
                            {organisation}
                          </a>
                        ) : (
                          <span
                            key={`${organisation}-${index}`}
                            className="inline-flex items-start gap-1.5"
                          >
                            <Building2 size={13} className="mt-1 shrink-0" />
                            {organisation}
                          </span>
                        );
                      })}
                    </div>
                  ) : (
                    <span className="text-[var(--text-faint)]">
                      Organisation unavailable
                    </span>
                  )}
                </MetadataRow>
              </dl>
            </Card>

            <PublicationActions publication={data} />
          </aside>
        </div>
      </Container>
    </>
  );
}
