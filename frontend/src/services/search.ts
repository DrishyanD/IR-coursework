import { apiGet } from "./api";
import type {
  PublicationSearchResponse,
  PublicationSearchResult,
  SearchAuthor,
} from "../types/search";
import { isRecord, pick, asString, asNumber, type UnknownRecord } from "../utils/normalize";

function normalizeAuthor(value: unknown, profileUrl?: unknown): SearchAuthor | null {
  if (typeof value === "string") {
    const name = value.trim();
    if (!name) return null;
    return {
      name,
      profileUrl: asString(profileUrl),
    };
  }

  if (isRecord(value)) {
    const name = asString(
      pick(value, ["name", "full_name", "display_name", "author_name"]),
    );
    if (!name) return null;

    return {
      name,
      profileUrl: asString(
        pick(value, [
          "profile_url",
          "profileUrl",
          "url",
          "pureportal_url",
          "pureportalUrl",
        ]),
      ),
    };
  }

  return null;
}

function normalizeAuthors(record: UnknownRecord): SearchAuthor[] {
  const rawAuthors = pick(record, ["authors", "author_names", "authorNames"]);
  const rawProfileUrls = pick(record, [
    "author_profile_urls",
    "authorProfileUrls",
    "profile_urls",
  ]);

  const profileUrls = Array.isArray(rawProfileUrls) ? rawProfileUrls : [];

  if (Array.isArray(rawAuthors)) {
    return rawAuthors
      .map((author, index) => normalizeAuthor(author, profileUrls[index]))
      .filter((author): author is SearchAuthor => author !== null);
  }

  if (typeof rawAuthors === "string") {
    return rawAuthors
      .split(/[,;]\s*/)
      .map((author, index) => normalizeAuthor(author, profileUrls[index]))
      .filter((author): author is SearchAuthor => author !== null);
  }

  return [];
}

function normalizeResult(value: unknown): PublicationSearchResult | null {
  if (!isRecord(value)) return null;

  const title =
    asString(pick(value, ["title", "publication_title", "name"])) ??
    "Untitled publication";

  const score =
    asNumber(
      pick(value, [
        "score",
        "cosine_similarity",
        "cosineSimilarity",
        "relevance_score",
        "relevanceScore",
      ]),
    ) ?? 0;

  return {
    id:
      asNumber(pick(value, ["publication_id", "publicationId", "id"])) ??
      asString(pick(value, ["publication_id", "publicationId", "id"])),
    title,
    publicationUrl: asString(
      pick(value, [
        "publication_url",
        "publicationUrl",
        "url",
        "pureportal_url",
        "pureportalUrl",
      ]),
    ),
    authors: normalizeAuthors(value),
    year:
      asNumber(pick(value, ["year", "publication_year", "publicationYear"])) ??
      asString(pick(value, ["year", "publication_year", "publicationYear"])),
    publicationDate: asString(
      pick(value, ["publication_date", "publicationDate", "published"]),
    ),
    score,
    snippet: asString(
      pick(value, ["snippet", "result_snippet", "resultSnippet"]),
    ),
    abstract: asString(pick(value, ["abstract", "summary", "description"])),
    outputType: asString(
      pick(value, ["output_type", "outputType", "type"]),
    ),
    doi: asString(pick(value, ["doi", "DOI"])),
  };
}

function normalizeSearchResponse(
  payload: unknown,
  requestedQuery: string,
): PublicationSearchResponse {
  let rawResults: unknown[] = [];
  let count: number | undefined;
  let processingTimeMs: number | undefined;
  let query = requestedQuery;

  if (Array.isArray(payload)) {
    rawResults = payload;
  } else if (isRecord(payload)) {
    const nested = pick(payload, ["results", "items", "data", "publications"]);
    rawResults = Array.isArray(nested) ? nested : [];

    count = asNumber(
      pick(payload, ["count", "total", "result_count", "resultCount"]),
    );

    processingTimeMs = asNumber(
      pick(payload, [
        "processing_time_ms",
        "processingTimeMs",
        "execution_time_ms",
        "executionTimeMs",
        "latency_ms",
        "latencyMs",
      ]),
    );

    query =
      asString(pick(payload, ["query", "q", "search_query", "searchQuery"])) ??
      requestedQuery;
  }

  const results = rawResults
    .map(normalizeResult)
    .filter((result): result is PublicationSearchResult => result !== null)
    .sort((a, b) => b.score - a.score);

  return {
    query,
    count: count ?? results.length,
    processingTimeMs,
    results,
  };
}

export async function searchPublications(
  query: string,
  options: {
    topK?: number;
    signal?: AbortSignal;
  } = {},
): Promise<PublicationSearchResponse> {
  const params = new URLSearchParams({
    q: query,
    top_k: String(options.topK ?? 100),
  });

  const payload = await apiGet<unknown>(
    `/api/search?${params.toString()}`,
    options.signal,
  );

  return normalizeSearchResponse(payload, query);
}
