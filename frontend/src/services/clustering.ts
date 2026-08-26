import { apiGet, ApiError } from "./api";
import { API_BASE_URL } from "../config";
import type {
  ClusterPrediction,
  ClusteringStatus,
  Task2Evidence,
} from "../types/clustering";
import { isRecord, pick, asString, asNumber, asBoolean } from "../utils/normalize";

export async function getClusteringStatus(
  signal?: AbortSignal,
): Promise<ClusteringStatus> {
  const payload = await apiGet<unknown>("/api/clustering/status", signal);

  if (!isRecord(payload)) {
    return { trained: false };
  }

  return {
    trained:
      asBoolean(
        pick(payload, [
          "trained",
          "is_trained",
          "isTrained",
          "ready",
          "available",
        ]),
      ) ?? false,
    modelPath: asString(
      pick(payload, ["model_path", "modelPath"]),
    ),
    vectorizerPath: asString(
      pick(payload, ["vectorizer_path", "vectorizerPath"]),
    ),
    metadataPath: asString(
      pick(payload, ["metadata_path", "metadataPath"]),
    ),
  };
}

function numberMap(value: unknown): Record<string, number> {
  if (!isRecord(value)) return {};
  return Object.fromEntries(Object.entries(value).flatMap(([key, raw]) => {
    const value = asNumber(raw);
    return value === undefined ? [] : [[key, value]];
  }));
}

function stringMap(value: unknown): Record<string, string> {
  if (!isRecord(value)) return {};
  return Object.fromEntries(Object.entries(value).flatMap(([key, raw]) => {
    const value = asString(raw);
    return value ? [[key, value]] : [];
  }));
}

export async function getTask2Evidence(signal?: AbortSignal): Promise<Task2Evidence> {
  const payload = await apiGet<unknown>("/api/clustering/evidence", signal);
  if (!isRecord(payload)) throw new ApiError("Task 2 evidence could not be read.");
  const datasetMetadata = isRecord(payload.dataset_metadata) ? payload.dataset_metadata : {};
  const report = isRecord(payload.training_report) ? payload.training_report : {};
  const dataset = isRecord(report.dataset) ? report.dataset : {};
  const evaluation = isRecord(report.evaluation) ? report.evaluation : {};
  const rawTerms = isRecord(report.top_terms) ? report.top_terms : {};
  const topTerms = Object.fromEntries(Object.entries(rawTerms).map(([key, value]) => [
    key,
    Array.isArray(value) ? value.filter((term): term is string => typeof term === "string") : [],
  ]));
  const feeds = Array.isArray(datasetMetadata.feeds)
    ? datasetMetadata.feeds.flatMap((feed) => isRecord(feed) && asString(feed.category) && asString(feed.url)
      ? [{ category: asString(feed.category)!, url: asString(feed.url)! }]
      : [])
    : [];

  return {
    trained: asBoolean(payload.trained) ?? false,
    collectedAt: asString(datasetMetadata.collected_at),
    documentCount: asNumber(dataset.document_count) ?? asNumber(datasetMetadata.total_documents) ?? 0,
    featureCount: asNumber(evaluation.feature_count) ?? 0,
    categoryCounts: numberMap(dataset.category_counts ?? datasetMetadata.category_counts),
    clusterSizes: numberMap(report.cluster_sizes),
    clusterNames: stringMap(report.cluster_names),
    topTerms,
    metrics: numberMap(evaluation),
    feeds,
  };
}

export async function predictCluster(
  text: string,
  signal?: AbortSignal,
): Promise<ClusterPrediction> {
  return requestPrediction("/api/clustering/predict", { text }, signal);
}

export async function predictClusterFromUrl(
  url: string,
  signal?: AbortSignal,
): Promise<ClusterPrediction> {
  return requestPrediction("/api/clustering/predict-url", { url }, signal);
}

async function requestPrediction(
  path: string,
  body: Record<string, string>,
  signal?: AbortSignal,
): Promise<ClusterPrediction> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Accept: "application/json",
      },
      body: JSON.stringify(body),
      signal,
    });
  } catch (error) {
    if (error instanceof DOMException && error.name === "AbortError") {
      throw error;
    }
    throw new ApiError("Unable to connect to the clustering API.");
  }

  if (!response.ok) {
    let detail = "";

    try {
      const payload = (await response.json()) as unknown;
      if (
        isRecord(payload) &&
        typeof payload.detail === "string"
      ) {
        detail = payload.detail;
      }
    } catch {
      // Keep a useful message even when the server returns plain text.
    }

    throw new ApiError(
      detail || `Clustering request failed with HTTP ${response.status}.`,
      response.status,
    );
  }

  const payload = (await response.json()) as unknown;

  if (!isRecord(payload)) {
    throw new ApiError("The clustering response could not be interpreted.");
  }

  const clusterId = asNumber(
    pick(payload, ["cluster_id", "clusterId", "cluster"]),
  );
  const predictedCategory = asString(
    pick(payload, [
      "predicted_category",
      "predictedCategory",
      "category",
      "cluster_name",
      "clusterName",
    ]),
  );
  const distanceToCentroid = asNumber(
    pick(payload, [
      "distance_to_centroid",
      "distanceToCentroid",
      "distance",
      "centroid_distance",
      "centroidDistance",
    ]),
  );
  const secondNearestDistance = asNumber(
    pick(payload, ["second_nearest_distance", "secondNearestDistance"]),
  );
  const separationMargin = asNumber(
    pick(payload, ["separation_margin", "separationMargin"]),
  );

  if (
    clusterId === undefined ||
    !predictedCategory ||
    distanceToCentroid === undefined ||
    secondNearestDistance === undefined ||
    separationMargin === undefined
  ) {
    throw new ApiError(
      "The clustering response is missing required prediction fields.",
    );
  }

  return {
    clusterId,
    predictedCategory,
    distanceToCentroid,
    secondNearestDistance,
    separationMargin,
  };
}
