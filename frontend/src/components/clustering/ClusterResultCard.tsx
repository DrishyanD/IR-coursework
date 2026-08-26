import {
  CircleDot,
  Gauge,
  Network,
  Sparkles,
} from "lucide-react";
import type { ClusterPrediction } from "../../types/clustering";
import { Card } from "../ui/Card";

export function ClusterResultCard({
  prediction,
}: {
  prediction: ClusterPrediction;
}) {
  const separationPercent = Math.round(prediction.separationMargin * 100);

  return (
    <Card className="overflow-hidden">
      <div className="border-b border-[var(--border)] bg-[radial-gradient(circle_at_top_right,var(--accent-soft),transparent_55%)] p-6 sm:p-7">
        <div className="flex items-center justify-between gap-4">
          <div className="text-xs font-bold uppercase tracking-[0.13em] text-[var(--accent)]">
            Cluster assignment
          </div>
          <Sparkles size={17} className="text-[var(--accent)]" />
        </div>

        <div className="mt-7">
          <div className="text-xs font-semibold text-[var(--text-faint)]">
            Predicted topic
          </div>
          <div className="mt-2 text-4xl font-extrabold tracking-[-0.045em] text-[var(--ink)] sm:text-5xl">
            {prediction.predictedCategory}
          </div>
        </div>
      </div>

      <div className="grid gap-0 sm:grid-cols-2">
        <Metric
          icon={Network}
          label="Cluster ID"
          value={String(prediction.clusterId)}
          description="The numeric ID learned by K-Means."
        />
        <Metric
          icon={Gauge}
          label="Centroid distance"
          value={prediction.distanceToCentroid.toFixed(4)}
          description="Lower means closer to that cluster's centre."
          border
        />
      </div>

      <div className="border-t border-[var(--border)] p-6">
        <div className="flex items-center gap-2 text-sm font-bold text-[var(--ink)]">
          <CircleDot size={15} className="text-[var(--accent)]" />
          Cluster separation
        </div>

        <div className="mt-4 h-2 overflow-hidden rounded-full bg-[var(--surface-muted)]">
          <div
            className="h-full rounded-full bg-[var(--accent)]"
            style={{ width: `${separationPercent}%` }}
          />
        </div>

        <p className="mt-4 text-xs leading-6 text-[var(--text-muted)]">
          {separationPercent}% separation from the next-nearest centroid.
          This is a relative distance margin, not a probability or supervised confidence score.
        </p>
      </div>
    </Card>
  );
}

function Metric({
  icon: Icon,
  label,
  value,
  description,
  border = false,
}: {
  icon: typeof Network;
  label: string;
  value: string;
  description: string;
  border?: boolean;
}) {
  return (
    <div
      className={`p-6 ${
        border ? "border-t border-[var(--border)] sm:border-l sm:border-t-0" : ""
      }`}
    >
      <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.11em] text-[var(--text-faint)]">
        <Icon size={14} className="text-[var(--accent)]" />
        {label}
      </div>
      <div className="mt-3 font-mono text-2xl font-bold tabular-nums text-[var(--ink)]">
        {value}
      </div>
      <p className="mt-2 text-xs leading-5 text-[var(--text-muted)]">
        {description}
      </p>
    </div>
  );
}
