import { API_BASE_URL } from "../config";

export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export async function apiGet<T>(
  path: string,
  signal?: AbortSignal,
): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      headers: { Accept: "application/json" },
      signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }
    throw new ApiError("Unable to connect to the API.");
  }

  if (!response.ok) {
    let detail = "";
    try {
      const payload = (await response.json()) as unknown;
      if (
        typeof payload === "object" &&
        payload !== null &&
        "detail" in payload &&
        typeof (payload as { detail?: unknown }).detail === "string"
      ) {
        detail = (payload as { detail: string }).detail;
      }
    } catch {
      // Some FastAPI/server errors are plain text rather than JSON.
    }

    throw new ApiError(
      detail || `Request failed with status ${response.status}`,
      response.status,
    );
  }

  return response.json() as Promise<T>;
}
