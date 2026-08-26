import { CircleAlert, CircleCheck, LoaderCircle } from "lucide-react";

export function ClusteringStatusBadge({
  loading,
  trained,
  error,
}: {
  loading: boolean;
  trained?: boolean;
  error?: string | null;
}) {
  if (loading) {
    return (
      <span className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--surface)] px-3 py-1.5 text-xs font-semibold text-[var(--text-muted)]">
        <LoaderCircle size={13} className="animate-spin" />
        Checking model
      </span>
    );
  }

  if (error || !trained) {
    return (
      <span className="inline-flex items-center gap-2 rounded-full border border-amber-300/60 bg-amber-50 px-3 py-1.5 text-xs font-semibold text-amber-800">
        <CircleAlert size={13} />
        Model unavailable
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-2 rounded-full border border-emerald-300/60 bg-emerald-50 px-3 py-1.5 text-xs font-semibold text-emerald-800">
      <CircleCheck size={13} />
      Model ready
    </span>
  );
}
