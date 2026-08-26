import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../services/api";
import { listPublications } from "../services/publications";
import type { PublicationListResponse } from "../types/publication";

export function usePublications() {
  const [data, setData] = useState<PublicationListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async (signal?: AbortSignal) => {
    setLoading(true);
    setError(null);

    try {
      const response = await listPublications({
        limit: 100,
        offset: 0,
        signal,
      });
      setData(response);
    } catch (error) {
      if (signal?.aborted) return;

      let message =
        "The publication collection could not be loaded. Check that the FastAPI backend is running.";

      if (error instanceof ApiError && error.status) {
        message = `The publication service returned HTTP ${error.status}.`;
      }

      setError(message);
      setData(null);
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
