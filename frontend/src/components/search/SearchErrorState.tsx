import { RefreshCcw, ServerOff } from "lucide-react";
import { Button } from "../ui/Button";

type SearchErrorStateProps = {
  message: string;
  onRetry: () => void;
};

export function SearchErrorState({
  message,
  onRetry,
}: SearchErrorStateProps) {
  return (
    <div className="grid min-h-[360px] place-items-center py-14 text-center">
      <div className="max-w-md">
        <div className="mx-auto grid h-13 w-13 place-items-center rounded-2xl bg-[var(--surface-muted)] text-[var(--text-muted)]">
          <ServerOff size={22} />
        </div>
        <h2 className="mt-5 text-lg font-bold text-[var(--ink)]">
          Search service unavailable
        </h2>
        <p className="mt-2 text-sm leading-6 text-[var(--text-muted)]">
          {message}
        </p>
        <Button className="mt-6" variant="secondary" onClick={onRetry}>
          <RefreshCcw size={15} />
          Try again
        </Button>
      </div>
    </div>
  );
}
