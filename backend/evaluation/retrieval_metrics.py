import math


def precision_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k <= 0:
        return 0.0

    top_k = retrieved[:k]
    if not top_k:
        return 0.0

    relevant_hits = sum(1 for item in top_k if item in relevant)
    return relevant_hits / k


def recall_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if not relevant:
        return 0.0

    top_k = retrieved[:k]
    relevant_hits = sum(1 for item in top_k if item in relevant)
    return relevant_hits / len(relevant)


def f1_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    precision = precision_at_k(retrieved, relevant, k)
    recall = recall_at_k(retrieved, relevant, k)

    if precision + recall == 0:
        return 0.0

    return 2 * precision * recall / (precision + recall)


def reciprocal_rank(retrieved: list[str], relevant: set[str]) -> float:
    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            return 1.0 / rank

    return 0.0


def average_precision(retrieved: list[str], relevant: set[str]) -> float:
    if not relevant:
        return 0.0

    hits = 0
    precision_sum = 0.0

    for rank, item in enumerate(retrieved, start=1):
        if item in relevant:
            hits += 1
            precision_sum += hits / rank

    return precision_sum / len(relevant)


def ndcg_at_k(retrieved: list[str], relevant: set[str], k: int) -> float:
    if k <= 0 or not relevant:
        return 0.0

    top_k = retrieved[:k]

    dcg = 0.0
    for rank, item in enumerate(top_k, start=1):
        gain = 1.0 if item in relevant else 0.0
        dcg += gain / math.log2(rank + 1)

    ideal_hits = min(len(relevant), k)
    idcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(1, ideal_hits + 1)
    )

    if idcg == 0:
        return 0.0

    return dcg / idcg
