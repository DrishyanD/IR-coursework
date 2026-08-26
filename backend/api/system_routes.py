from fastapi import APIRouter, Request

from integration.system_validator import SystemValidator


router = APIRouter(prefix="/api/system", tags=["System"])


@router.get("/status")
def system_status(request: Request):
    validator = SystemValidator(
        database=request.app.state.database,
        publication_repository=request.app.state.publication_repository,
        index_manager=request.app.state.index_manager,
        clustering_service=request.app.state.clustering_service,
    )

    return validator.validate()
