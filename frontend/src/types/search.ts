export type SearchAuthor = {
  name: string;
  profileUrl?: string;
};

export type PublicationSearchResult = {
  id?: number | string;
  title: string;
  publicationUrl?: string;
  authors: SearchAuthor[];
  year?: number | string;
  publicationDate?: string;
  score: number;
  snippet?: string;
  abstract?: string;
  outputType?: string;
  doi?: string;
};

export type PublicationSearchResponse = {
  query: string;
  count: number;
  processingTimeMs?: number;
  results: PublicationSearchResult[];
};

export type SearchSort =
  | "relevance"
  | "newest"
  | "oldest"
  | "title";

export type SearchFilters = {
  years: string[];
  authors: string[];
  outputTypes: string[];
};
