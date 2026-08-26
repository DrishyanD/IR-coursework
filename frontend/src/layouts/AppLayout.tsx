import { Outlet } from "react-router";
import { Header } from "../components/navigation/Header";
import { RouteEffects } from "../components/navigation/RouteEffects";
import { OfflineBanner } from "../components/system/OfflineBanner";
import { useGlobalSearchShortcut } from "../hooks/useGlobalSearchShortcut";

export function AppLayout() {
  useGlobalSearchShortcut();

  return (
    <div className="min-h-screen bg-[var(--background)] text-[var(--ink)]">
      <a
        href="#main-content"
        className="fixed left-4 top-3 z-[120] -translate-y-24 rounded-xl bg-[var(--ink)] px-4 py-2 text-sm font-bold text-[var(--surface)] shadow-lg transition focus:translate-y-0"
      >
        Skip to content
      </a>

      <RouteEffects />
      <OfflineBanner />
      <Header />

      <main id="main-content" tabIndex={-1} className="outline-none">
        <Outlet />
      </main>

    </div>
  );
}
