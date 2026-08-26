import {
  BookOpenText,
  CalendarClock,
  CircleStop,
  ExternalLink,
  FileClock,
  Play,
  RefreshCcw,
  Save,
  ShieldCheck,
  TerminalSquare,
  TriangleAlert,
} from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Button } from "../components/ui/Button";
import { Card } from "../components/ui/Card";
import { Container } from "../components/ui/Container";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { useSystemDashboard } from "../hooks/useSystemDashboard";
import { ApiError } from "../services/api";
import {
  getCrawlEvents,
  startPublicationCrawl,
  stopPublicationCrawl,
  updateSchedulerConfiguration,
} from "../services/system";
import type { CrawlEvent, CrawlRun } from "../types/system";
import { formatLocalDateTime, formatLocalTime } from "../utils/dateTime";

type Notice = { tone: "success" | "warning" | "error"; text: string };

const DAY_OPTIONS = [
  ["mon", "Monday"],
  ["tue", "Tuesday"],
  ["wed", "Wednesday"],
  ["thu", "Thursday"],
  ["fri", "Friday"],
  ["sat", "Saturday"],
  ["sun", "Sunday"],
] as const;

const TIMEZONE_OPTIONS = ["UTC", "Europe/London", "Asia/Kathmandu"];

export function DataManagementPage() {
  useDocumentTitle("Data Management");
  const dashboard = useSystemDashboard();
  const [notice, setNotice] = useState<Notice | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [selectedRunId, setSelectedRunId] = useState<number | null>(null);
  const [events, setEvents] = useState<CrawlEvent[]>([]);
  const [eventsError, setEventsError] = useState<string | null>(null);
  const [scheduleDay, setScheduleDay] = useState("sun");
  const [scheduleTime, setScheduleTime] = useState("02:00");
  const [scheduleTimezone, setScheduleTimezone] = useState("UTC");

  const runs = useMemo(() => dashboard.data?.crawlRuns ?? [], [dashboard.data?.crawlRuns]);
  const activeRun = runs.find((run) => run.status === "running");
  const refreshDashboard = dashboard.refresh;
  const crawler = dashboard.data?.crawler;
  const scheduler = dashboard.data?.scheduler;

  useEffect(() => {
    const firstId = numberId(runs[0]);
    if (selectedRunId === null && firstId !== null) setSelectedRunId(firstId);
  }, [runs, selectedRunId]);

  useEffect(() => {
    const activeId = numberId(activeRun);
    if (activeId !== null && activeId !== selectedRunId) {
      setSelectedRunId(activeId);
      setEvents([]);
    }
  }, [activeRun, selectedRunId]);

  useEffect(() => {
    if (!scheduler) return;
    if (scheduler.dayOfWeek) setScheduleDay(scheduler.dayOfWeek);
    if (scheduler.hour !== undefined && scheduler.minute !== undefined) {
      setScheduleTime(`${String(scheduler.hour).padStart(2, "0")}:${String(scheduler.minute).padStart(2, "0")}`);
    }
    if (scheduler.timezone) setScheduleTimezone(scheduler.timezone);
  }, [scheduler?.dayOfWeek, scheduler?.hour, scheduler?.minute, scheduler?.timezone]);

  const loadEvents = useCallback(async () => {
    if (selectedRunId === null) return;
    try {
      setEvents(await getCrawlEvents(selectedRunId));
      setEventsError(null);
    } catch (error) {
      setEventsError(messageFrom(error, "The crawl log could not be loaded."));
    }
  }, [selectedRunId]);

  useEffect(() => {
    void loadEvents();
    if (!activeRun) return;
    const timer = window.setInterval(() => {
      refreshDashboard();
      void loadEvents();
    }, 2500);
    return () => window.clearInterval(timer);
  }, [activeRun, loadEvents, refreshDashboard]);

  const act = async (name: string, task: () => Promise<unknown>, success: string) => {
    setBusy(name);
    setNotice(null);
    try {
      await task();
      setNotice({ tone: "success", text: success });
      refreshDashboard();
      window.setTimeout(refreshDashboard, 800);
    } catch (error) {
      setNotice({ tone: "error", text: messageFrom(error, "The action could not be completed.") });
    } finally {
      setBusy(null);
    }
  };

  const toggleScheduler = () => {
    const next = !(scheduler?.enabled ?? false);
    void act(
      "scheduler-toggle",
      () => updateSchedulerConfiguration({ enabled: next }),
      next
        ? "Automatic weekly publication updates are enabled."
        : "Automatic publication updates are disabled. Manual updates remain available.",
    );
  };

  const saveSchedule = () => {
    const [hourText, minuteText] = scheduleTime.split(":");
    const hour = Number(hourText);
    const minute = Number(minuteText);
    if (!Number.isInteger(hour) || !Number.isInteger(minute)) {
      setNotice({ tone: "error", text: "Enter a valid schedule time." });
      return;
    }

    void act(
      "scheduler-save",
      () => updateSchedulerConfiguration({
        day_of_week: scheduleDay,
        hour,
        minute,
        timezone: scheduleTimezone,
      }),
      "The weekly automatic-update schedule has been saved.",
    );
  };

  return (
    <>
      <section className="border-b border-[var(--border)] bg-[var(--surface)]">
        <Container className="py-12 sm:py-16">
          <div className="text-xs font-bold uppercase tracking-[0.15em] text-[var(--accent)]">Coursework data operations</div>
          <h1 className="mt-5 max-w-4xl text-[clamp(2.7rem,6vw,5rem)] font-extrabold leading-[0.98] tracking-[-0.055em]">
            Manage the collection.<span className="block text-[var(--text-muted)]">Manual and automatic updates.</span>
          </h1>
          <p className="mt-6 max-w-2xl text-sm leading-7 text-[var(--text-muted)] sm:text-base">
            Run publication updates on demand, configure the weekly automatic schedule and inspect clear, timestamped crawl activity from the backend.
          </p>
        </Container>
      </section>

      <Container className="space-y-6 py-10 sm:py-14">
        {notice && <NoticeBox notice={notice} />}
        {dashboard.error && <NoticeBox notice={{ tone: "error", text: dashboard.error }} />}

        {!crawler && dashboard.loading ? <LoadingCards /> : crawler && (
          <>
            <div className="grid gap-5 xl:grid-cols-[minmax(0,1.2fr)_minmax(360px,0.8fr)]">
              <Card className="p-5 sm:p-6">
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 text-sm font-bold"><BookOpenText size={16} className="text-[var(--accent)]" />Publication crawler</div>
                    <p className="mt-2 max-w-xl text-xs leading-5 text-[var(--text-muted)]">
                      Manual updates use the fixed Coventry organisation scope. robots.txt checks, request throttling and page limits are applied automatically.
                    </p>
                  </div>
                  <StatusLabel active={Boolean(activeRun)} activeText="Running" inactiveText="Ready" invert />
                </div>

                <a href={crawler.seedUrl} target="_blank" rel="noreferrer" className="mt-5 flex items-center gap-2 break-all rounded-xl bg-[var(--surface-muted)] p-3 text-xs font-medium text-[var(--ink)] hover:text-[var(--accent)]">
                  {crawler.seedUrl}<ExternalLink size={13} className="shrink-0" />
                </a>

                <div className="mt-5 grid gap-3 sm:grid-cols-4">
                  <Metric label="Stored publications" value={dashboard.data?.status.publicationCount ?? dashboard.data?.stats.publicationCount} />
                  <Metric label="Request delay" value={`${crawler.crawlDelaySeconds}s`} />
                  <Metric label="Maximum pages" value={crawler.maxPages} />
                  <Metric label="robots.txt" value={crawler.robotsChecked ? "Checked" : "—"} />
                </div>

                <div className="mt-6 flex flex-wrap gap-2">
                  <Button disabled={busy !== null || Boolean(activeRun)} onClick={() => void act("start", startPublicationCrawl, "The publication crawl has been queued.")}>
                    <Play size={15} />{busy === "start" ? "Starting..." : "Update publications"}
                  </Button>
                  {activeRun && <Button variant="secondary" disabled={busy !== null} onClick={() => void act("stop", stopPublicationCrawl, "The crawler will stop after its current request finishes.")}><CircleStop size={15} />Stop crawl</Button>}
                </div>
              </Card>

              <Card className="p-5 sm:p-6">
                <div className="flex flex-wrap items-start justify-between gap-3">
                  <div>
                    <div className="flex items-center gap-2 text-sm font-bold"><CalendarClock size={17} className="text-[var(--accent)]" />Automatic updates</div>
                    <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">APScheduler runs the same crawl-and-reindex pipeline automatically once per week.</p>
                  </div>
                  <StatusLabel active={scheduler?.enabled ?? false} activeText="Enabled" inactiveText="Disabled" />
                </div>

                <div className="mt-5 grid gap-3 sm:grid-cols-2">
                  <label className="text-xs font-medium text-[var(--text-muted)]">
                    Day
                    <select value={scheduleDay} onChange={(event) => setScheduleDay(event.target.value)} disabled={busy !== null || Boolean(activeRun)} className="mt-2 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--ink)]">
                      {DAY_OPTIONS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
                    </select>
                  </label>
                  <label className="text-xs font-medium text-[var(--text-muted)]">
                    Time
                    <input type="time" value={scheduleTime} onChange={(event) => setScheduleTime(event.target.value)} disabled={busy !== null || Boolean(activeRun)} className="mt-2 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--ink)]" />
                  </label>
                </div>

                <label className="mt-3 block text-xs font-medium text-[var(--text-muted)]">
                  Timezone
                  <select value={scheduleTimezone} onChange={(event) => setScheduleTimezone(event.target.value)} disabled={busy !== null || Boolean(activeRun)} className="mt-2 w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-3 py-2.5 text-sm text-[var(--ink)]">
                    {TIMEZONE_OPTIONS.map((value) => <option key={value} value={value}>{value}</option>)}
                  </select>
                </label>

                <div className="mt-4 rounded-xl bg-[var(--surface-muted)] p-3">
                  <div className="text-[11px] font-medium text-[var(--text-faint)]">Next scheduled update</div>
                  <div className="mt-1 text-sm font-bold text-[var(--ink)]">
                    {scheduler?.enabled && scheduler.nextRun ? formatLocalDateTime(scheduler.nextRun) : "Automatic updates disabled"}
                  </div>
                  {scheduler?.enabled && scheduler.nextRun && <div className="mt-1 text-[10px] text-[var(--text-faint)]">Displayed in this device&apos;s local time · schedule timezone {scheduler.timezone ?? scheduleTimezone}</div>}
                </div>

                <div className="mt-5 flex flex-wrap gap-2">
                  <Button variant="secondary" disabled={busy !== null || Boolean(activeRun)} onClick={toggleScheduler}>
                    {busy === "scheduler-toggle" ? "Saving..." : scheduler?.enabled ? "Disable automatic updates" : "Enable automatic updates"}
                  </Button>
                  <Button disabled={busy !== null || Boolean(activeRun)} onClick={saveSchedule}>
                    <Save size={15} />{busy === "scheduler-save" ? "Saving..." : "Save schedule"}
                  </Button>
                </div>
                {activeRun && <p className="mt-3 text-[11px] leading-4 text-[var(--text-faint)]">Schedule changes are locked while a crawl is running.</p>}
              </Card>
            </div>

            <div className="grid gap-5 xl:grid-cols-[360px_minmax(0,1fr)]">
              <RunHistory runs={runs} selectedRunId={selectedRunId} onSelect={setSelectedRunId} />
              <EventLog events={events} error={eventsError} onRefresh={() => void loadEvents()} />
            </div>
          </>
        )}
      </Container>
    </>
  );
}

function NoticeBox({ notice }: { notice: Notice }) {
  const styles = notice.tone === "error" ? "border-red-300 bg-red-50 text-red-900" : notice.tone === "warning" ? "border-amber-300 bg-amber-50 text-amber-900" : "border-emerald-300 bg-emerald-50 text-emerald-900";
  return <div className={`flex items-start gap-3 rounded-[16px] border p-4 text-sm ${styles}`}>{notice.tone === "error" ? <TriangleAlert size={18} /> : <ShieldCheck size={18} />}<span>{notice.text}</span></div>;
}

function Metric({ label, value }: { label: string; value: string | number | undefined }) {
  return <div className="rounded-xl border border-[var(--border)] p-3"><div className="text-[11px] font-medium text-[var(--text-faint)]">{label}</div><div className="mt-1 text-lg font-bold">{value ?? "—"}</div></div>;
}

function StatusLabel({ active, activeText, inactiveText, invert = false }: { active: boolean; activeText: string; inactiveText: string; invert?: boolean }) {
  const highlighted = invert ? !active : active;
  return <span className={`rounded-full px-3 py-1 text-xs font-bold ${highlighted ? "bg-emerald-100 text-emerald-800" : active ? "bg-sky-100 text-sky-800" : "bg-[var(--surface-muted)] text-[var(--text-muted)]"}`}>{active ? activeText : inactiveText}</span>;
}

function RunHistory({ runs, selectedRunId, onSelect }: { runs: CrawlRun[]; selectedRunId: number | null; onSelect: (id: number) => void }) {
  return <Card className="overflow-hidden"><div className="flex items-center gap-2 border-b border-[var(--border)] px-5 py-4 text-sm font-bold"><FileClock size={16} />Crawl history</div><div className="max-h-[520px] overflow-y-auto p-2">{runs.length === 0 ? <p className="p-4 text-xs text-[var(--text-muted)]">No crawl runs have been recorded yet.</p> : runs.map((run) => { const id = numberId(run); if (id === null) return null; return <button key={id} type="button" onClick={() => onSelect(id)} className={`w-full rounded-xl p-3 text-left transition ${selectedRunId === id ? "bg-[var(--surface-muted)]" : "hover:bg-[var(--surface-muted)]"}`}><div className="flex items-center justify-between gap-2"><span className="text-xs font-bold">Run #{id}</span><span className="text-[10px] font-bold uppercase text-[var(--text-faint)]">{run.status ?? "unknown"}</span></div><div className="mt-1 text-[11px] text-[var(--text-muted)]">{formatDate(run.runAt)} · {run.triggerType ?? "manual"}</div><div className="mt-2 text-[11px] text-[var(--text-faint)]">{run.pagesCrawled ?? 0} pages · {run.publicationsNew ?? 0} new · {run.publicationsChanged ?? 0} changed</div></button>; })}</div></Card>;
}

function EventLog({ events, error, onRefresh }: { events: CrawlEvent[]; error: string | null; onRefresh: () => void }) {
  return <Card className="overflow-hidden"><div className="flex items-center justify-between border-b border-[var(--border)] px-5 py-4"><div className="flex items-center gap-2 text-sm font-bold"><TerminalSquare size={16} />Activity log</div><Button variant="ghost" className="h-8 px-2" onClick={onRefresh}><RefreshCcw size={14} />Refresh</Button></div><div className="max-h-[520px] min-h-[300px] overflow-auto bg-[var(--background)] p-3 font-mono">{error ? <div className="p-3 text-xs text-red-600">{error}</div> : events.length === 0 ? <div className="p-3 text-xs text-[var(--text-faint)]">No events were recorded for this run. Runs created before this update only have summary statistics.</div> : events.map((event) => <div key={event.id} className="grid gap-1 border-b border-[var(--border)] px-2 py-2 text-[11px] leading-5 sm:grid-cols-[72px_76px_110px_minmax(0,1fr)]"><span className="text-[var(--text-faint)]">{formatTime(event.createdAt)}</span><span className={levelColor(event.level)}>{event.level}</span><span className="text-[var(--text-muted)]">{event.eventType}</span><span className="break-words text-[var(--ink)]">{event.message}{event.url && <span className="mt-0.5 block break-all text-[var(--text-faint)]">{event.url}</span>}</span></div>)}</div></Card>;
}

function LoadingCards() { return <div className="grid gap-5 lg:grid-cols-2"><div className="h-72 animate-pulse rounded-[22px] bg-[var(--surface-muted)]" /><div className="h-72 animate-pulse rounded-[22px] bg-[var(--surface-muted)]" /></div>; }
function numberId(run?: CrawlRun) { const value = run?.id; if (typeof value === "number") return value; if (typeof value === "string" && /^\d+$/.test(value)) return Number(value); return null; }
function messageFrom(error: unknown, fallback: string) { return error instanceof ApiError ? error.message : fallback; }
function formatDate(value?: string) { return value ? formatLocalDateTime(value) : "Unknown time"; }
function formatTime(value: string) { return formatLocalTime(value); }
function levelColor(level: string) { const key = level.toUpperCase(); return key === "ERROR" ? "font-bold text-red-600" : key === "WARNING" ? "font-bold text-amber-600" : key === "SUCCESS" ? "font-bold text-emerald-600" : "font-bold text-sky-600"; }
