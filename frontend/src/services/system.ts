import { API_BASE_URL } from "../config";
import { ApiError, apiGet } from "./api";
import type {
  AdminStats,
  CrawlRun,
  SchedulerStatus,
  SystemDashboardData,
  SystemStatus,
  CrawlerConfiguration,
  CrawlEvent,
} from "../types/system";
import { isRecord, pick, asString, asNumber, asBoolean } from "../utils/normalize";

function normalizeSystemStatus(payload: unknown): SystemStatus {
  if (!isRecord(payload)) return {};

  return {
    databaseExists: asBoolean(pick(payload, ["database_exists", "databaseExists"])),
    publicationCount: asNumber(pick(payload, ["publication_count", "publicationCount"])),
    indexDocuments: asNumber(pick(payload, ["index_documents", "indexDocuments"])),
    vocabularySize: asNumber(pick(payload, ["vocabulary_size", "vocabularySize"])),
    indexMatchesDatabase: asBoolean(pick(payload, ["index_matches_database", "indexMatchesDatabase"])),
    clusteringTrained: asBoolean(pick(payload, ["clustering_trained", "clusteringTrained"])),
    task1Ready: asBoolean(pick(payload, ["task1_ready", "task1Ready"])),
    task2Ready: asBoolean(pick(payload, ["task2_ready", "task2Ready"])),
    fullSystemReady: asBoolean(pick(payload, ["full_system_ready", "fullSystemReady"])),
  };
}

function normalizeStats(payload: unknown): AdminStats {
  if (!isRecord(payload)) return {};
  return {
    publicationCount: asNumber(pick(payload, ["publication_count", "publicationCount", "publications"])),
    authorCount: asNumber(pick(payload, ["author_count", "authorCount", "authors"])),
    indexDocuments: asNumber(pick(payload, ["index_documents", "indexDocuments", "documents"])),
    vocabularySize: asNumber(pick(payload, ["vocabulary_size", "vocabularySize", "vocabulary"])),
    schedulerEnabled: asBoolean(pick(payload, ["scheduler_enabled", "schedulerEnabled"])),
    robotsRespected: asBoolean(pick(payload, ["robots_respected", "robotsRespected"])),
    crawlDelaySeconds: asNumber(pick(payload, ["crawl_delay_seconds", "crawlDelaySeconds", "crawl_delay"])),
  };
}

function normalizeScheduler(payload: unknown): SchedulerStatus {
  if (!isRecord(payload)) return {};
  return {
    enabled: asBoolean(pick(payload, ["enabled", "scheduler_enabled", "schedulerEnabled"])),
    running: asBoolean(pick(payload, ["running", "is_running", "isRunning"])),
    frequency: asString(pick(payload, ["frequency"])),
    dayOfWeek: asString(pick(payload, ["day_of_week", "dayOfWeek"])),
    hour: asNumber(pick(payload, ["hour"])),
    minute: asNumber(pick(payload, ["minute"])),
    timezone: asString(pick(payload, ["timezone"])),
    nextRun: asString(pick(payload, ["next_run_time", "nextRunTime", "next_run", "nextRun"])),
    updatedAt: asString(pick(payload, ["updated_at", "updatedAt"])),
  };
}

function normalizeCrawlRun(value: unknown): CrawlRun | null {
  if (!isRecord(value)) return null;

  return {
    id: asNumber(pick(value, ["id", "run_id", "runId"])) ??
        asString(pick(value, ["id", "run_id", "runId"])),
    runAt: asString(pick(value, ["run_at", "runAt", "started_at", "startedAt"])),
    pagesCrawled: asNumber(pick(value, ["pages_crawled", "pagesCrawled", "pages_fetched", "pagesFetched"])),
    pagesFailed: asNumber(pick(value, ["pages_failed", "pagesFailed"])),
    pagesBlocked: asNumber(pick(value, ["pages_blocked", "pagesBlocked", "skipped_by_robots", "skippedByRobots", "robots_blocked"])),
    publicationsFound: asNumber(pick(value, ["publications_found", "publicationsFound", "publications", "publications_seen"])),
    publicationsNew: asNumber(pick(value, ["publications_new", "publicationsNew", "publications_inserted"])),
    publicationsChanged: asNumber(pick(value, ["publications_changed", "publicationsChanged"])),
    publicationsUnchanged: asNumber(pick(value, ["publications_unchanged", "publicationsUnchanged"])),
    publicationsRejected: asNumber(pick(value, ["publications_rejected", "publicationsRejected"])),
    status: asString(pick(value, ["status", "result"])),
    finishedAt: asString(pick(value, ["finished_at", "finishedAt"])),
    triggerType: asString(pick(value, ["trigger_type", "triggerType"])),
    publicationsUpdated: asNumber(pick(value, ["publications_updated", "publicationsUpdated"])),
    indexDocuments: asNumber(pick(value, ["index_documents", "indexDocuments"])),
    errorMessage: asString(pick(value, ["error_message", "errorMessage"])),
  };
}

function normalizeCrawlerConfiguration(payload: unknown): CrawlerConfiguration {
  if (!isRecord(payload)) throw new ApiError("Crawler configuration could not be read.");

  return {
    allowedDomain: asString(pick(payload, ["allowed_domain", "allowedDomain"])) ?? "pureportal.coventry.ac.uk",
    seedUrl: asString(pick(payload, ["seed_url", "seedUrl"])) ?? "",
    crawlDelaySeconds: asNumber(pick(payload, ["crawl_delay_seconds", "crawlDelaySeconds"])) ?? 0,
    maxPages: asNumber(pick(payload, ["max_pages", "maxPages"])) ?? 0,
    robotsChecked: asBoolean(pick(payload, ["robots_checked", "robotsChecked"])) ?? true,
  };
}

function normalizeCrawlRuns(payload: unknown): CrawlRun[] {
  let values: unknown[] = [];

  if (Array.isArray(payload)) {
    values = payload;
  } else if (isRecord(payload)) {
    const nested = pick(payload, ["runs", "items", "results", "crawl_runs", "crawlRuns"]);
    if (Array.isArray(nested)) values = nested;
  }

  return values
    .map(normalizeCrawlRun)
    .filter((item): item is CrawlRun => item !== null);
}

async function optionalGet(path: string, signal?: AbortSignal): Promise<unknown | null> {
  try {
    return await apiGet<unknown>(path, signal);
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) return null;
    throw error;
  }
}

export async function getSystemDashboard(
  signal?: AbortSignal,
): Promise<SystemDashboardData> {
  const [statusPayload, statsPayload, schedulerPayload, crawlRunsPayload, crawlerPayload] =
    await Promise.all([
      apiGet<unknown>("/api/system/status", signal),
      optionalGet("/api/admin/stats", signal),
      optionalGet("/api/admin/scheduler", signal),
      optionalGet("/api/admin/crawl-runs", signal),
      apiGet<unknown>("/api/admin/crawler/config", signal),
    ]);

  return {
    status: normalizeSystemStatus(statusPayload),
    stats: normalizeStats(statsPayload),
    scheduler: schedulerPayload ? normalizeScheduler(schedulerPayload) : null,
    crawlRuns: normalizeCrawlRuns(crawlRunsPayload),
    crawler: normalizeCrawlerConfiguration(crawlerPayload),
  };
}

async function writeJson(path: string, method: "POST" | "PATCH", body?: unknown) {
  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: { Accept: "application/json", "Content-Type": "application/json" },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("Unable to connect to the administration API.");
  }

  const payload = await response.json().catch(() => ({})) as unknown;
  if (!response.ok) {
    const detail = isRecord(payload) ? asString(payload.detail) : undefined;
    throw new ApiError(detail ?? `Administration request failed with HTTP ${response.status}.`, response.status);
  }
  return payload;
}

export async function updateSchedulerConfiguration(update: {
  enabled?: boolean;
  day_of_week?: string;
  hour?: number;
  minute?: number;
  timezone?: string;
}): Promise<SchedulerStatus> {
  const payload = await writeJson("/api/admin/scheduler", "PATCH", update);
  return normalizeScheduler(payload);
}

export async function startPublicationCrawl() {
  return writeJson("/api/admin/crawl-now", "POST");
}

export async function stopPublicationCrawl() {
  return writeJson("/api/admin/crawl-stop", "POST");
}

export async function getCrawlEvents(runId: number, afterId = 0): Promise<CrawlEvent[]> {
  const payload = await apiGet<unknown>(`/api/admin/crawl-runs/${runId}/events?after_id=${afterId}&limit=500`);
  if (!isRecord(payload) || !Array.isArray(payload.items)) return [];

  return payload.items.flatMap((value): CrawlEvent[] => {
    if (!isRecord(value)) return [];
    const id = asNumber(value.id);
    const eventRunId = asNumber(pick(value, ["run_id", "runId"]));
    const createdAt = asString(pick(value, ["created_at", "createdAt"]));
    const level = asString(value.level);
    const eventType = asString(pick(value, ["event_type", "eventType"]));
    const message = asString(value.message);
    if (id === undefined || eventRunId === undefined || !createdAt || !level || !eventType || !message) return [];
    return [{ id, runId: eventRunId, createdAt, level, eventType, message, url: asString(value.url) }];
  });
}

export async function runAdminAction(
  endpoint: "/api/admin/crawl-now" | "/api/admin/rebuild-index",
): Promise<unknown> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: { Accept: "application/json" },
    });
  } catch {
    throw new ApiError("Unable to connect to the administration API.");
  }

  if (!response.ok) {
    throw new ApiError(
      response.status === 404
        ? "This administration action is not exposed by the current backend."
        : `Administration action failed with HTTP ${response.status}.`,
      response.status,
    );
  }

  try {
    return await response.json();
  } catch {
    return {};
  }
}
