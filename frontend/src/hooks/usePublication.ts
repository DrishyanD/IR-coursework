import { useCallback, useEffect, useState } from "react";
import { ApiError } from "../services/api";
import { getPublication } from "../services/publications";
import type { PublicationRecord } from "../types/publication";

export function usePublication(publicationId?: string) {
  const [data, setData] = useState<PublicationRecord | null>(null);
  const [loading, setLoading] = useState(Boolean(publicationId));
  const [error, setError] = useState<string | null>(null);
  const [notFound, setNotFound] = useState(false);

  const load = useCallback(
    async (signal?: AbortSignal) => {
      if (!publicationId) {
        setLoading(false);
        setError("Publication ID is missing.");
        return;
      }

      setLoading(true);
      setError(null);
      setNotFound(false);

      try {
        const publication = await getPublication(publicationId, signal);
        setData(publication);
      } catch (error) {
        if (signal?.aborted) return;

        if (error instanceof ApiError && error.status === 404) {
          setNotFound(true);
          setData(null);
        } else {
          setError(
            error instanceof ApiError && error.status
              ? `The publication service returned HTTP ${error.status}.`
              : "The publication could not be loaded. Check that the FastAPI backend is running.",
          );
          setData(null);
        }
      } finally {
        if (!signal?.aborted) setLoading(false);
      }
    },
    [publicationId],
  );

  useEffect(() => {
    const controller = new AbortController();
    void load(controller.signal);
    return () => controller.abort();
  }, [load]);

  return {
    data,
    loading,
    error,
    notFound,
    retry: () => void load(),
  };
}
