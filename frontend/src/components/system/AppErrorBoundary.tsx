import { Component, type ErrorInfo, type ReactNode } from "react";
import { AlertTriangle, Home, RefreshCcw } from "lucide-react";

type Props = {
  children: ReactNode;
};

type State = {
  hasError: boolean;
};

export class AppErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false };

  static getDerivedStateFromError(): State {
    return { hasError: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("Unexpected frontend error:", error, info);
  }

  private reload = () => {
    window.location.reload();
  };

  private goHome = () => {
    window.location.assign("/");
  };

  render() {
    if (!this.state.hasError) {
      return this.props.children;
    }

    return (
      <main className="grid min-h-screen place-items-center bg-[var(--background)] px-5 py-16 text-[var(--ink)]">
        <div className="w-full max-w-lg rounded-[24px] border border-[var(--border)] bg-[var(--surface)] p-7 text-center shadow-[var(--shadow-soft)] sm:p-10">
          <div className="mx-auto grid h-12 w-12 place-items-center rounded-2xl bg-[var(--surface-muted)] text-[var(--accent)]">
            <AlertTriangle size={22} />
          </div>

          <h1 className="mt-5 text-2xl font-bold tracking-[-0.03em]">
            Something went wrong
          </h1>
          <p className="mt-3 text-sm leading-6 text-[var(--text-muted)]">
            An unexpected frontend error interrupted this view. Your backend
            data has not been changed.
          </p>

          <div className="mt-7 flex flex-col justify-center gap-2 sm:flex-row">
            <button
              type="button"
              onClick={this.reload}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-xl bg-[var(--ink)] px-4 text-sm font-semibold text-[var(--surface)]"
            >
              <RefreshCcw size={15} />
              Reload
            </button>
            <button
              type="button"
              onClick={this.goHome}
              className="inline-flex h-10 items-center justify-center gap-2 rounded-xl border border-[var(--border-strong)] bg-[var(--surface)] px-4 text-sm font-semibold text-[var(--ink)]"
            >
              <Home size={15} />
              Home
            </button>
          </div>
        </div>
      </main>
    );
  }
}
