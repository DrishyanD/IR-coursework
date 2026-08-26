import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../services/api";
import { getSystemDashboard } from "../services/system";
import type { SystemDashboardData } from "../types/system";

export function useSystemDashboard() {
  const [data, setData] = useState<SystemDashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);

    try {
      setData(await getSystemDashboard(signal));
    } catch (error) {
      if (signal?.aborted) return;

      setData(null);
      setError(
        error instanceof ApiError
          ? error.message
          : "System status could not be loaded.",
      );
    } finally {
      if (!signal?.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal);
    return () => controller.abort();
  }, [load]);

  const refresh = useCallback(() => {
    void load();
  }, [load]);

  return {
    data,
    loading,
    error,
    refresh,
  };
}
