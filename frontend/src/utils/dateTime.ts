const TIMEZONE_SUFFIX = /(Z|[+-]\d{2}:?\d{2})$/i;
const DATABASE_TIMESTAMP = /^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?$/;

/** SQLite timestamps are UTC even when the stored text has no timezone suffix. */
export function parseDateTime(value: string): Date | null {
  const timestamp = value.trim();
  if (!timestamp) return null;

  // Add Z when needed so the browser converts the UTC time correctly.
  const normalized = DATABASE_TIMESTAMP.test(timestamp) && !TIMEZONE_SUFFIX.test(timestamp)
    ? `${timestamp.replace(" ", "T")}Z`
    : timestamp;
  const date = new Date(normalized);
  return Number.isNaN(date.getTime()) ? null : date;
}

/** Show a timestamp using the user's local browser settings. */
export function formatLocalDateTime(value: string, fallback = value): string {
  const date = parseDateTime(value);
  return date ? date.toLocaleString() : fallback;
}

export function formatLocalTime(value: string, fallback = value): string {
  const date = parseDateTime(value);
  return date
    ? date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })
    : fallback;
}
