from fastapi import APIRouter, Depends, Query

from api.dependencies import get_search_engine


router = APIRouter(prefix="/api/search", tags=["Search"])


def serialize_result(result):
    publication = result.publication

    return {
        "id": publication.id,
        "title": publication.title,
        "authors": [
            {
                "id": author.id,
                "name": author.name,
                "profile_url": author.profile_url,
            }
            for author in publication.authors
        ],
        "year": publication.year,
        "publication_date": publication.publication_date,
        "abstract": publication.abstract,
        "keywords": publication.keywords,
        "publication_url": publication.publication_url,
        "author_profile_urls": publication.author_profile_urls,
        "output_type": publication.output_type,
        "doi": publication.doi,
        "openalex_id": publication.openalex_id,
        "cited_by_count": publication.cited_by_count,
        "is_open_access": publication.is_open_access,
        "open_access_url": publication.open_access_url,
        "openalex_topics": publication.openalex_topics,
        "score": round(result.score, 6),
        "snippet": result.snippet,
        "execution_time_ms": result.execution_time_ms,
    }


@router.get("")
def search(
    q: str = Query(..., min_length=1, description="Search query"),
    top_k: int = Query(10, ge=1, le=100),
    min_score: float = Query(0.0, ge=0.0, le=1.0),
    engine=Depends(get_search_engine),
):
    results = engine.search(
        query=q,
        top_k=top_k,
        min_score=min_score,
    )

    return {
        "query": q,
        "count": len(results),
        "results": [serialize_result(result) for result in results],
    }


@router.get("/phrase")
def phrase_search(
    q: str = Query(..., min_length=1, description="Exact phrase query"),
    top_k: int = Query(50, ge=1, le=100),
    engine=Depends(get_search_engine),
):
    results = engine.phrase_search(phrase=q, top_k=top_k)

    return {
        "query": q,
        "count": len(results),
        "results": [serialize_result(result) for result in results],
    }


@router.get("/boolean")
def boolean_search(
    q: str = Query(..., min_length=1, description="Boolean query terms"),
    mode: str = Query("AND", description="Boolean mode: AND or OR"),
    engine=Depends(get_search_engine),
):
    results = engine.boolean_search(query=q, mode=mode)

    return {
        "query": q,
        "mode": mode.upper(),
        "count": len(results),
        "results": [serialize_result(result) for result in results],
    }


@router.get("/proximity")
def proximity_search(
    term1: str = Query(..., min_length=1, description="First term"),
    term2: str = Query(..., min_length=1, description="Second term"),
    distance: int = Query(5, ge=1, le=50, description="Maximum word distance"),
    top_k: int = Query(50, ge=1, le=100),
    engine=Depends(get_search_engine),
):
    results = engine.proximity_search(
        term1=term1, term2=term2, distance=distance, top_k=top_k
    )

    return {
        "term1": term1,
        "term2": term2,
        "distance": distance,
        "count": len(results),
        "results": [serialize_result(result) for result in results],
    }


@router.get("/explain")
def explain_query(
    q: str = Query(..., min_length=1),
    engine=Depends(get_search_engine),
):
    return engine.explain_query(q)
