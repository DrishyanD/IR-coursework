import {
  Binary,
  Braces,
  Network,
  Tags,
} from "lucide-react";
import { Card } from "../ui/Card";

const STEPS = [
  {
    icon: Braces,
    title: "Preprocess",
    text: "Normalize the new text using the clustering text pipeline.",
  },
  {
    icon: Binary,
    title: "Vectorize",
    text: "Transform it with the already-fitted TF-IDF vectorizer.",
  },
  {
    icon: Network,
    title: "K-Means",
    text: "Measure the document against the learned cluster centroids.",
  },
  {
    icon: Tags,
    title: "Interpret",
    text: "Display the category associated with that cluster after training.",
  },
];

export function ClusteringMethodCard() {
  return (
    <Card className="p-5 sm:p-6">
      <div className="text-xs font-bold uppercase tracking-[0.13em] text-[var(--text-faint)]">
        How this works
      </div>

      <div className="mt-5 space-y-5">
        {STEPS.map(({ icon: Icon, title, text }) => (
          <div key={title} className="flex gap-3">
            <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl bg-[var(--surface-muted)] text-[var(--accent)]">
              <Icon size={16} />
            </div>
            <div>
              <div className="text-sm font-bold text-[var(--ink)]">{title}</div>
              <p className="mt-1 text-xs leading-5 text-[var(--text-muted)]">
                {text}
              </p>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 rounded-xl bg-[var(--surface-muted)] p-4 text-xs leading-5 text-[var(--text-muted)]">
        The category labels are not training targets for K-Means. They are used
        afterward to interpret and evaluate the clusters.
      </div>
    </Card>
  );
}
