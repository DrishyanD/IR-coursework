from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_publication_repository


router = APIRouter(prefix="/api/publications", tags=["Publications"])


def serialize_publication(publication):
    return {
        "id": publication.id,
        "title": publication.title,
        "year": publication.year,
        "publication_date": publication.publication_date,
        "abstract": publication.abstract,
        "keywords": publication.keywords,
        "organisations": publication.organisations,
        "organisation_urls": publication.organisation_urls,
        "output_type": publication.output_type,
        "doi": publication.doi,
        "openalex_id": publication.openalex_id,
        "cited_by_count": publication.cited_by_count,
        "is_open_access": publication.is_open_access,
        "open_access_url": publication.open_access_url,
        "openalex_topics": publication.openalex_topics,
        "publication_url": publication.publication_url,
        "authors": [
            {
                "id": author.id,
                "name": author.name,
                "profile_url": author.profile_url,
            }
            for author in publication.authors
        ],
    }


@router.get("")
def list_publications(
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    repository=Depends(get_publication_repository),
):
    publications = repository.list_all()
    page = publications[offset:offset + limit]

    return {
        "total": len(publications),
        "limit": limit,
        "offset": offset,
        "items": [serialize_publication(publication) for publication in page],
    }


@router.get("/{publication_id}")
def get_publication(
    publication_id: int,
    repository=Depends(get_publication_repository),
):
    publication = repository.get_by_id(publication_id)

    if publication is None:
        raise HTTPException(
            status_code=404,
            detail="Publication not found.",
        )

    return serialize_publication(publication)
