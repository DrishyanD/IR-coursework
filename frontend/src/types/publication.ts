export type PublicationAuthor = {
  id?: number | string;
  name: string;
  profileUrl?: string;
};

export type PublicationRecord = {
  id?: number | string;
  title: string;
  year?: number | string;
  publicationDate?: string;
  abstract?: string;
  keywords: string[];
  organisations: string[];
  organisationUrls: string[];
  outputType?: string;
  doi?: string;
  publicationUrl?: string;
  authors: PublicationAuthor[];
};

export type PublicationListResponse = {
  total: number;
  limit: number;
  offset: number;
  items: PublicationRecord[];
};
