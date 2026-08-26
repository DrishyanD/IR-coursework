from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Request
from clustering.article_loader import ArticleLoader


router = APIRouter(prefix="/api/clustering", tags=["Clustering"])


class PredictionRequest(BaseModel):
    text: str = Field(..., min_length=1)


class URLPredictionRequest(BaseModel):
    url: str = Field(..., min_length=1)


@router.get("/status")
def clustering_status(request: Request):
    service = request.app.state.clustering_service
    return service.status()


@router.get("/evidence")
def clustering_evidence(request: Request):
    try:
        return request.app.state.clustering_service.evidence()
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Task 2 evidence is unavailable until the clustering model is trained.",
        )


@router.get("/analytics")
def clustering_analytics(request: Request):
    """Compatibility endpoint for older frontend builds."""
    return clustering_evidence(request)


@router.post("/predict")
def predict_cluster(
    payload: PredictionRequest,
    request: Request,
):
    service = request.app.state.clustering_service

    try:
        return service.predict(payload.text)
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail=(
                "Clustering model has not been trained yet. "
                "Train Task 2 before using prediction."
            ),
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.post("/predict-url")
def predict_cluster_from_url(payload: URLPredictionRequest, request: Request):
    service = request.app.state.clustering_service

    try:
        article = ArticleLoader().load(payload.url)
        prediction = service.predict(article["text"])
        return {**prediction, "source_url": article["url"], "source_title": article["title"]}
    except FileNotFoundError:
        raise HTTPException(
            status_code=503,
            detail="Clustering model has not been trained yet. Train Task 2 before using prediction.",
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
