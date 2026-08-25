def cosine_similarity(
    vector_a: dict[str, float],
    vector_b: dict[str, float],
) -> float:
    if not vector_a or not vector_b:
        return 0.0

    if len(vector_a) > len(vector_b):
        vector_a, vector_b = vector_b, vector_a

    score = 0.0

    for term, weight in vector_a.items():
        score += weight * vector_b.get(term, 0.0)

    return score
