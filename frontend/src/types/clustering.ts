export type ClusteringStatus = {
  trained: boolean;
  modelPath?: string;
  vectorizerPath?: string;
  metadataPath?: string;
};

export type ClusterPrediction = {
  clusterId: number;
  predictedCategory: string;
  distanceToCentroid: number;
  secondNearestDistance: number;
  separationMargin: number;
};

export type Task2Evidence = {
  trained: boolean;
  collectedAt?: string;
  documentCount: number;
  featureCount: number;
  categoryCounts: Record<string, number>;
  clusterSizes: Record<string, number>;
  clusterNames: Record<string, string>;
  topTerms: Record<string, string[]>;
  metrics: Record<string, number>;
  feeds: Array<{ category: string; url: string }>;
};
