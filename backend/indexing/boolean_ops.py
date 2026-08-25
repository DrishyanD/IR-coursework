"""Boolean posting-list operations using merge-based algorithms.

All functions expect and return **sorted** lists of document IDs (ascending).
They exploit the sorted order for O(n+m) merge efficiency.

Usage with InvertedIndex::

    from indexing.boolean_ops import postings_and, postings_or, postings_not

    ids_a = index.sorted_doc_ids("community")
    ids_b = index.sorted_doc_ids("healthcare")
    result = postings_and(ids_a, ids_b)                    # AND
    result = postings_or(ids_a, ids_b)                     # OR
    result = postings_not(ids_a, index.all_doc_ids_sorted()) # NOT
"""


def postings_and(list_a: list[int], list_b: list[int]) -> list[int]:
    """Merge-intersect two sorted doc-ID lists (Boolean AND).

    Returns the sorted list of IDs present in *both* inputs.
    """
    result = []
    i, j = 0, 0

    while i < len(list_a) and j < len(list_b):
        if list_a[i] == list_b[j]:
            result.append(list_a[i])
            i += 1
            j += 1
        elif list_a[i] < list_b[j]:
            i += 1
        else:
            j += 1

    return result


def postings_or(list_a: list[int], list_b: list[int]) -> list[int]:
    """Merge-union two sorted doc-ID lists (Boolean OR).

    Returns the sorted list of IDs present in *either* input.
    """
    result = []
    i, j = 0, 0

    while i < len(list_a) and j < len(list_b):
        if list_a[i] == list_b[j]:
            result.append(list_a[i])
            i += 1
            j += 1
        elif list_a[i] < list_b[j]:
            result.append(list_a[i])
            i += 1
        else:
            result.append(list_b[j])
            j += 1

    result.extend(list_a[i:])
    result.extend(list_b[j:])

    return result


def postings_not(list_a: list[int], all_doc_ids: list[int]) -> list[int]:
    """Complement of *list_a* against the complete document-ID universe.

    Both *list_a* and *all_doc_ids* must be sorted ascending.
    Returns the sorted list of IDs in *all_doc_ids* that are **not** in
    *list_a*.

    The *all_doc_ids* parameter must be the full indexed document-ID
    universe (e.g. ``index.all_doc_ids_sorted()``), not a partial subset.
    """
    result = []
    i, j = 0, 0

    while i < len(all_doc_ids) and j < len(list_a):
        if all_doc_ids[i] == list_a[j]:
            i += 1
            j += 1
        elif all_doc_ids[i] < list_a[j]:
            result.append(all_doc_ids[i])
            i += 1
        else:
            j += 1

    result.extend(all_doc_ids[i:])

    return result
