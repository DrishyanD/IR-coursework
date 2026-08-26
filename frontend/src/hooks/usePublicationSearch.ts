import { useCallback, useEffect, useRef, useState } from "react";
import { ApiError } from "../services/api";
import { searchPublications } from "../services/search";
import type { PublicationSearchResponse } from "../types/search";

type SearchState = {
  data: PublicationSearchResponse | null;
  loading: boolean;
  error: string | null;
};

export function usePublicationSearch(query: string) {
  const [state, setState] = useState<SearchState>({
    data: null,
    loading: false,
    error: null,
  });

  const requestId = useRef(0);

  const run = useCallback(
    async (signal?: AbortSignal) => {
      const cleanQuery = query.trim();

      if (!cleanQuery) {
        setState({
          data: null,
          loading: false,
          error: null,
        });
        return;
      }

      const currentRequest = ++requestId.current;

      setState((current) => ({
        ...current,
        loading: true,
        error: null,
      }));

      try {
        const response = await searchPublications(cleanQuery, {
          topK: 100,
          signal,
        });

        if (currentRequest !== requestId.current) return;

        setState({
          data: response,
          loading: false,
          error: null,
        });
      } catch (error) {
        if (signal?.aborted || currentRequest !== requestId.current) return;

        let message =
          "The search service could not be reached. Check that the FastAPI backend is running and try again.";

        if (error instanceof ApiError && error.status) {
          message = `The search service returned HTTP ${error.status}. Please try again.`;
        } else if (error instanceof Error && error.message) {
          if (!error.message.toLowerCase().includes("fetch")) {
            message = error.message;
          }
        }

        setState({
          data: null,
          loading: false,
          error: message,
        });
      }
    },
    [query],
  );

  useEffect(() => {
    const controller = new AbortController();
    void run(controller.signal);

    return () => controller.abort();
  }, [run]);

  const retry = useCallback(() => {
    void run();
  }, [run]);

  return { ...state, retry };
}
