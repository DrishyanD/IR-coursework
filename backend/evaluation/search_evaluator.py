"""Runs the Task 1 qrels and reports common ranked-retrieval metrics."""

import json
import statistics
import time
from pathlib import Path

from evaluation.retrieval_metrics import (
    average_precision,
    f1_at_k,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


class SearchEvaluator:
    def __init__(self, search_engine):
        self.search_engine = search_engine

    def evaluate(self, judgments: list[dict], k_values=(5, 10)) -> dict:
        per_query = []

        for judgment in judgments:
            query = judgment["query"]
            relevant_urls = set(judgment["relevant_publication_urls"])

            started = time.perf_counter()
            # AP/MAP and MRR use the full ranked list; P@K/R@K are calculated separately at each cutoff.
            corpus_size = self.search_engine.index_manager.inverted_index.document_count
            evaluation_depth = max(
                max(k_values) if k_values else 10,
                corpus_size,
            )
            results = self.search_engine.search(
                query,
                top_k=evaluation_depth,
            )
            latency_ms = (time.perf_counter() - started) * 1000

            retrieved_urls = [
                result.publication.publication_url
                for result in results
            ]

            metrics = {
                "query": query,
                "relevant_count": len(relevant_urls),
                "retrieved_count": len(retrieved_urls),
                "latency_ms": round(latency_ms, 3),
                "mrr": reciprocal_rank(retrieved_urls, relevant_urls),
                "average_precision": average_precision(
                    retrieved_urls,
                    relevant_urls,
                ),
            }

            for k in k_values:
                metrics[f"precision_at_{k}"] = precision_at_k(
                    retrieved_urls,
                    relevant_urls,
                    k,
                )
                metrics[f"recall_at_{k}"] = recall_at_k(
                    retrieved_urls,
                    relevant_urls,
                    k,
                )
                metrics[f"f1_at_{k}"] = f1_at_k(
                    retrieved_urls,
                    relevant_urls,
                    k,
                )
                metrics[f"ndcg_at_{k}"] = ndcg_at_k(
                    retrieved_urls,
                    relevant_urls,
                    k,
                )

            metrics["retrieved"] = [
                {
                    "rank": rank,
                    "publication_url": result.publication.publication_url,
                    "title": result.publication.title,
                    "year": result.publication.year,
                    "score": round(result.score, 6),
                    "relevant": (
                        result.publication.publication_url in relevant_urls
                    ),
                }
                for rank, result in enumerate(results, start=1)
            ]

            per_query.append(metrics)

        summary = self._aggregate(per_query, k_values)

        return {
            "summary": summary,
            "queries": per_query,
        }

    def _aggregate(self, per_query: list[dict], k_values) -> dict:
        if not per_query:
            return {
                "query_count": 0,
                "mean_latency_ms": 0.0,
                "median_latency_ms": 0.0,
                "mrr": 0.0,
                "map": 0.0,
            }

        summary = {
            "query_count": len(per_query),
            "mean_latency_ms": round(
                statistics.mean(item["latency_ms"] for item in per_query),
                3,
            ),
            "median_latency_ms": round(
                statistics.median(item["latency_ms"] for item in per_query),
                3,
            ),
            "mrr": statistics.mean(item["mrr"] for item in per_query),
            "map": statistics.mean(
                item["average_precision"] for item in per_query
            ),
        }

        for k in k_values:
            for metric in ("precision", "recall", "f1", "ndcg"):
                key = f"{metric}_at_{k}"
                summary[key] = statistics.mean(
                    item[key] for item in per_query
                )

        return summary

    @staticmethod
    def load_judgments(path: str | Path) -> list[dict]:
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))

        if not isinstance(data, list):
            raise ValueError("Judgment file must contain a JSON list.")

        for item in data:
            if "query" not in item or "relevant_publication_urls" not in item:
                raise ValueError(
                    "Each judgment requires query and relevant_publication_urls."
                )

        return data

    @staticmethod
    def save_report(report: dict, path: str | Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(report, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
