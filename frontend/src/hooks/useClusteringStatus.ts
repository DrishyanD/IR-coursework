import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../services/api";
import { getClusteringStatus } from "../services/clustering";
import type { ClusteringStatus } from "../types/clustering";

export function useClusteringStatus() {
  const [data, setData] = useState<ClusteringStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);

    try {
      const status = await getClusteringStatus(signal);
      setData(status);
    } catch (error) {
      if (signal?.aborted) return;

      setData(null);
      setError(
        error instanceof ApiError
          ? error.message
          : "The clustering model status could not be loaded.",
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

  return {
    data,
    loading,
    error,
    retry: () => void load(),
  };
}
