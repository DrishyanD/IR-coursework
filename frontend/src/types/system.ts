export type SystemStatus = {
  databaseExists?: boolean;
  publicationCount?: number;
  indexDocuments?: number;
  vocabularySize?: number;
  indexMatchesDatabase?: boolean;
  clusteringTrained?: boolean;
  task1Ready?: boolean;
  task2Ready?: boolean;
  fullSystemReady?: boolean;
};

export type AdminStats = {
  publicationCount?: number;
  authorCount?: number;
  indexDocuments?: number;
  vocabularySize?: number;
  schedulerEnabled?: boolean;
  robotsRespected?: boolean;
  crawlDelaySeconds?: number;
};

export type SchedulerStatus = {
  enabled?: boolean;
  running?: boolean;
  frequency?: string;
  dayOfWeek?: string;
  hour?: number;
  minute?: number;
  timezone?: string;
  nextRun?: string;
  updatedAt?: string;
};

export type CrawlRun = {
  id?: number | string;
  runAt?: string;
  pagesCrawled?: number;
  pagesFailed?: number;
  pagesBlocked?: number;
  publicationsFound?: number;
  publicationsNew?: number;
  publicationsChanged?: number;
  publicationsUnchanged?: number;
  publicationsRejected?: number;
  status?: string;
  finishedAt?: string;
  triggerType?: string;
  publicationsUpdated?: number;
  indexDocuments?: number;
  errorMessage?: string | null;
};

export type CrawlerConfiguration = {
  allowedDomain: string;
  seedUrl: string;
  crawlDelaySeconds: number;
  maxPages: number;
  robotsChecked: boolean;
};

export type CrawlEvent = {
  id: number;
  runId: number;
  createdAt: string;
  level: string;
  eventType: string;
  message: string;
  url?: string | null;
};

export type SystemDashboardData = {
  status: SystemStatus;
  stats: AdminStats;
  scheduler: SchedulerStatus | null;
  crawlRuns: CrawlRun[];
  crawler: CrawlerConfiguration;
};
