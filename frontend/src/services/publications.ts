import { apiGet } from "./api";
import type {
  PublicationListResponse,
  PublicationRecord,
  PublicationAuthor,
} from "../types/publication";
import { isRecord, pick, asString, asNumber } from "../utils/normalize";

function stringArray(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .map(asString)
    .filter((item): item is string => Boolean(item));
}

function normalizeAuthor(value: unknown): PublicationAuthor | null {
  if (typeof value === "string") {
    const name = value.trim();
    return name ? { name } : null;
  }

  if (!isRecord(value)) return null;

  const name = asString(
    pick(value, ["name", "full_name", "display_name", "author_name"]),
  );
  if (!name) return null;

  return {
    id:
      asNumber(pick(value, ["id", "author_id", "authorId"])) ??
      asString(pick(value, ["id", "author_id", "authorId"])),
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

function normalizePublication(value: unknown): PublicationRecord | null {
  if (!isRecord(value)) return null;

  const title =
    asString(pick(value, ["title", "publication_title", "name"])) ??
    "Untitled publication";

  const rawAuthors = pick(value, ["authors", "author_names", "authorNames"]);
  const authors = Array.isArray(rawAuthors)
    ? rawAuthors
        .map(normalizeAuthor)
        .filter((author): author is PublicationAuthor => author !== null)
    : [];

  return {
    id:
      asNumber(pick(value, ["id", "publication_id", "publicationId"])) ??
      asString(pick(value, ["id", "publication_id", "publicationId"])),
    title,
    year:
      asNumber(pick(value, ["year", "publication_year", "publicationYear"])) ??
      asString(pick(value, ["year", "publication_year", "publicationYear"])),
    publicationDate: asString(
      pick(value, ["publication_date", "publicationDate", "published"]),
    ),
    abstract: asString(pick(value, ["abstract", "summary", "description"])),
    keywords: stringArray(pick(value, ["keywords", "keyword_list", "keywordList"])),
    organisations: stringArray(
      pick(value, ["organisations", "organizations", "organisation_names"]),
    ),
    organisationUrls: stringArray(
      pick(value, ["organisation_urls", "organization_urls", "organisationUrls"]),
    ),
    outputType: asString(pick(value, ["output_type", "outputType", "type"])),
    doi: asString(pick(value, ["doi", "DOI"])),
    publicationUrl: asString(
      pick(value, [
        "publication_url",
        "publicationUrl",
        "url",
        "pureportal_url",
        "pureportalUrl",
      ]),
    ),
    authors,
  };
}

export async function listPublications(
  options: {
    limit?: number;
    offset?: number;
    signal?: AbortSignal;
  } = {},
): Promise<PublicationListResponse> {
  const params = new URLSearchParams({
    limit: String(options.limit ?? 100),
    offset: String(options.offset ?? 0),
  });

  const payload = await apiGet<unknown>(
    `/api/publications?${params.toString()}`,
    options.signal,
  );

  if (Array.isArray(payload)) {
    const items = payload
      .map(normalizePublication)
      .filter((item): item is PublicationRecord => item !== null);

    return {
      total: items.length,
      limit: options.limit ?? 100,
      offset: options.offset ?? 0,
      items,
    };
  }

  if (!isRecord(payload)) {
    return {
      total: 0,
      limit: options.limit ?? 100,
      offset: options.offset ?? 0,
      items: [],
    };
  }

  const rawItems = pick(payload, ["items", "results", "data", "publications"]);
  const items = Array.isArray(rawItems)
    ? rawItems
        .map(normalizePublication)
        .filter((item): item is PublicationRecord => item !== null)
    : [];

  return {
    total: asNumber(pick(payload, ["total", "count"])) ?? items.length,
    limit: asNumber(pick(payload, ["limit"])) ?? options.limit ?? 100,
    offset: asNumber(pick(payload, ["offset"])) ?? options.offset ?? 0,
    items,
  };
}


export async function getPublication(
  publicationId: string | number,
  signal?: AbortSignal,
): Promise<PublicationRecord> {
  const payload = await apiGet<unknown>(
    `/api/publications/${encodeURIComponent(String(publicationId))}`,
    signal,
  );

  const publication = normalizePublication(payload);

  if (!publication) {
    throw new Error("The publication response could not be interpreted.");
  }

  return publication;
}
