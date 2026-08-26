import { BarChart3, BrainCircuit, FileInput, RefreshCcw, TriangleAlert } from "lucide-react";
import { useRef, useState } from "react";
import { ClusterResultCard } from "../components/clustering/ClusterResultCard";
import { ClusteringMethodCard } from "../components/clustering/ClusteringMethodCard";
import { ClusteringStatusBadge } from "../components/clustering/ClusteringStatusBadge";
import { DocumentInputCard } from "../components/clustering/DocumentInputCard";
import { Task2EvidencePanel } from "../components/clustering/Task2EvidencePanel";
import { Button } from "../components/ui/Button";
import { Container } from "../components/ui/Container";
import { useClusteringStatus } from "../hooks/useClusteringStatus";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { ApiError } from "../services/api";
import { predictCluster, predictClusterFromUrl } from "../services/clustering";
import type { ClusterPrediction } from "../types/clustering";

export function ClusteringPage() {
  useDocumentTitle("Clustering");
  const status = useClusteringStatus();
  const [prediction, setPrediction] = useState<ClusterPrediction | null>(null);
  const [view, setView] = useState<"assign" | "evidence">("assign");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const controllerRef = useRef<AbortController | null>(null);

  const submit = async (value: string, fromUrl = false) => {
    controllerRef.current?.abort();
    const controller = new AbortController();
    controllerRef.current = controller;
    setBusy(true);
    setError(null);
    setPrediction(null);
    try {
      setPrediction(await (fromUrl ? predictClusterFromUrl(value, controller.signal) : predictCluster(value, controller.signal)));
    } catch (caught) {
      if (!controller.signal.aborted) setError(caught instanceof ApiError ? caught.message : "The document could not be assigned.");
    } finally {
      if (!controller.signal.aborted) setBusy(false);
    }
  };

  const modelReady = status.data?.trained === true;

  return (
    <>
      <section className="border-b border-[var(--border)] bg-[var(--surface)]">
        <Container className="py-9 sm:py-11">
          <div className="flex items-center justify-between gap-4">
            <div><div className="flex items-center gap-2 text-xs font-bold uppercase tracking-[0.15em] text-[var(--accent)]"><BrainCircuit size={14} />Task 2 · Document clustering</div><h1 className="mt-3 text-3xl font-extrabold tracking-[-0.04em] sm:text-4xl">Assign a document to a cluster</h1></div>
            <ClusteringStatusBadge loading={status.loading} trained={status.data?.trained} error={status.error} />
          </div>
          <div className="mt-6 flex gap-2">
            <Button variant={view === "assign" ? "primary" : "secondary"} onClick={() => setView("assign")}><FileInput size={14} />Assign document</Button>
            <Button variant={view === "evidence" ? "primary" : "secondary"} onClick={() => setView("evidence")}><BarChart3 size={14} />Task 2 evidence</Button>
          </div>
        </Container>
      </section>
      <Container className="py-8 sm:py-10">
        {status.error && <div className="mb-5 flex items-center justify-between rounded-xl border border-amber-300 bg-amber-50 p-4 text-sm text-amber-900"><span>{status.error}</span><Button variant="secondary" onClick={status.retry}><RefreshCcw size={14} />Retry</Button></div>}
        {!status.loading && status.data && !modelReady && <div className="mb-5 flex gap-3 rounded-xl border border-[var(--border)] p-4 text-sm"><TriangleAlert size={18} /><span>Train and save the Task 2 model before assigning documents.</span></div>}
        {view === "assign" ? <div className="grid gap-6 lg:grid-cols-[minmax(0,1.15fr)_minmax(320px,0.85fr)] lg:items-start">
          <DocumentInputCard disabled={!modelReady} busy={busy} onSubmit={(text) => void submit(text)} onSubmitUrl={(url) => void submit(url, true)} />
          <div>{busy ? <div className="h-[260px] animate-pulse rounded-[22px] bg-[var(--surface-muted)]" /> : error ? <div className="rounded-[22px] border border-red-300 p-5 text-sm text-red-700">{error}</div> : prediction ? <ClusterResultCard prediction={prediction} /> : <ClusteringMethodCard />}</div>
        </div> : <Task2EvidencePanel />}
      </Container>
    </>
  );
}
