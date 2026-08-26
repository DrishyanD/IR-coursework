import { ExternalLink, RefreshCcw } from "lucide-react";
import { useEffect, useState } from "react";
import { ApiError } from "../../services/api";
import { getTask2Evidence } from "../../services/clustering";
import type { Task2Evidence } from "../../types/clustering";
import { formatLocalDateTime } from "../../utils/dateTime";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";

const metricLabels: Record<string, string> = {
  silhouette_cosine: "Silhouette (cosine)",
  adjusted_rand_index: "Adjusted Rand Index",
  normalized_mutual_information: "NMI",
  homogeneity: "Homogeneity",
  completeness: "Completeness",
  v_measure: "V-measure",
};

export function Task2EvidencePanel() {
  const [data, setData] = useState<Task2Evidence | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const load = () => {
    setLoading(true);
    setError(null);
    void getTask2Evidence().then(setData).catch((caught) => {
      setError(caught instanceof ApiError ? caught.message : "Task 2 evidence could not be loaded.");
    }).finally(() => setLoading(false));
  };

  useEffect(load, []);

  if (loading) return <div className="h-80 animate-pulse rounded-2xl bg-[var(--surface-muted)]" />;
  if (error || !data) return <Card className="p-6 text-center"><p className="text-sm text-red-600">{error}</p><Button className="mt-4" variant="secondary" onClick={load}><RefreshCcw size={14} />Retry</Button></Card>;

  return (
    <div className="space-y-5">
      <div className="grid gap-3 sm:grid-cols-3">
        <EvidenceValue label="Documents" value={data.documentCount} />
        <EvidenceValue label="TF-IDF features" value={data.featureCount} />
        <EvidenceValue label="K-Means clusters" value={Object.keys(data.clusterSizes).length} />
      </div>

      <div className="grid gap-5 lg:grid-cols-2">
        <Card className="p-5"><h2 className="font-bold">Dataset composition</h2><Rows values={data.categoryCounts} /></Card>
        <Card className="p-5"><h2 className="font-bold">Learned clusters</h2><Rows values={Object.fromEntries(Object.entries(data.clusterSizes).map(([id, count]) => [`Cluster ${id} · ${data.clusterNames[id] ?? "Unlabelled"}`, count]))} /></Card>
      </div>

      <Card className="p-5">
        <h2 className="font-bold">Evaluation metrics</h2>
        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {Object.entries(metricLabels).map(([key, label]) => <div key={key} className="rounded-xl bg-[var(--surface-muted)] p-3"><div className="text-[11px] text-[var(--text-faint)]">{label}</div><div className="mt-1 font-mono text-lg font-bold">{data.metrics[key]?.toFixed(4) ?? "—"}</div></div>)}
        </div>
        <p className="mt-4 text-xs leading-5 text-[var(--text-muted)]">Known categories are used only to evaluate and interpret the clusters; they are not supplied to K-Means as features.</p>
      </Card>

      <div className="grid gap-4 lg:grid-cols-3">
        {Object.entries(data.topTerms).map(([id, terms]) => <Card key={id} className="p-5"><div className="text-xs font-bold text-[var(--accent)]">Cluster {id} · {data.clusterNames[id]}</div><div className="mt-3 flex flex-wrap gap-2">{terms.map((term) => <span key={term} className="rounded-full bg-[var(--surface-muted)] px-2.5 py-1 text-xs">{term}</span>)}</div></Card>)}
      </div>

      <Card className="min-w-0 p-5"><h2 className="font-bold">BBC RSS sources</h2><div className="mt-3 space-y-2">{data.feeds.map((feed) => <a key={feed.url} href={feed.url} target="_blank" rel="noreferrer" className="flex min-w-0 items-center justify-between gap-3 rounded-xl bg-[var(--surface-muted)] px-3 py-2 text-xs hover:text-[var(--accent)]"><span className="min-w-0 break-all"><strong>{feed.category}</strong> · {feed.url}</span><ExternalLink size={13} className="shrink-0" /></a>)}</div>{data.collectedAt && <p className="mt-3 text-[11px] text-[var(--text-faint)]">Collected {formatLocalDateTime(data.collectedAt)}</p>}</Card>
    </div>
  );
}

function EvidenceValue({ label, value }: { label: string; value: number }) { return <Card className="p-4"><div className="text-xs text-[var(--text-faint)]">{label}</div><div className="mt-1 text-2xl font-bold">{value.toLocaleString()}</div></Card>; }
function Rows({ values }: { values: Record<string, number> }) { return <div className="mt-3 divide-y divide-[var(--border)]">{Object.entries(values).map(([label, value]) => <div key={label} className="flex justify-between gap-3 py-2 text-sm"><span>{label}</span><strong>{value}</strong></div>)}</div>; }
