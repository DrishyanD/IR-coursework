import { WifiOff } from "lucide-react";
import { useOnlineStatus } from "../../hooks/useOnlineStatus";

export function OfflineBanner() {
  const online = useOnlineStatus();

  if (online) return null;

  return (
    <div
      role="status"
      aria-live="polite"
      className="border-b border-amber-300/70 bg-amber-50 px-4 py-2 text-center text-xs font-semibold text-amber-900"
    >
      <span className="inline-flex items-center gap-2">
        <WifiOff size={13} />
        You are offline. Previously loaded pages remain visible, but live API
        requests may fail.
      </span>
    </div>
  );
}
