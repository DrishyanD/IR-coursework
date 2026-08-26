import { Landmark, Film, Vote } from "lucide-react";

const EXAMPLES = [
  {
    label: "Economics",
    icon: Landmark,
    text: "The central bank raised interest rates after inflation remained above target and borrowing costs continued to increase.",
  },
  {
    label: "Entertainment",
    icon: Film,
    text: "The new film opened in cinemas this weekend after its cast attended the premiere and discussed the production.",
  },
  {
    label: "Politics",
    icon: Vote,
    text: "Parliament debated the new legislation before lawmakers voted on the government's proposal.",
  },
];

export function ExampleDocuments({
  onSelect,
}: {
  onSelect: (text: string) => void;
}) {
  return (
    <div>
      <div className="text-xs font-bold uppercase tracking-[0.12em] text-[var(--text-faint)]">
        Try an example
      </div>

      <div className="mt-3 grid gap-2">
        {EXAMPLES.map(({ label, icon: Icon, text }) => (
          <button
            key={label}
            type="button"
            onClick={() => onSelect(text)}
            className="flex items-start gap-3 rounded-xl border border-[var(--border)] bg-[var(--surface)] p-3 text-left transition hover:border-[var(--border-strong)] hover:bg-[var(--surface-muted)]"
          >
            <div className="grid h-8 w-8 shrink-0 place-items-center rounded-xl bg-[var(--accent-soft)] text-[var(--accent)]">
              <Icon size={15} />
            </div>
            <div className="min-w-0">
              <div className="text-xs font-bold text-[var(--ink)]">
                {label}
              </div>
              <div className="mt-1 line-clamp-2 text-[11px] leading-5 text-[var(--text-muted)]">
                {text}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}
