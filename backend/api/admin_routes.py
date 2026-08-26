"""Administration endpoints for crawling, scheduling, index status and crawl history."""

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field

from api.dependencies import (
    get_crawler_scheduler,
    get_index_manager,
    get_publication_repository,
    get_search_engine,
)
from database.crawl_run_repository import CrawlRunRepository
from database.crawl_event_repository import CrawlEventRepository
from database.scheduler_settings_repository import SchedulerSettingsRepository
from config import settings


router = APIRouter(prefix="/api/admin", tags=["Administration"])


class SchedulerConfigurationUpdate(BaseModel):
    enabled: bool | None = None
    day_of_week: str | None = None
    hour: int | None = Field(default=None, ge=0, le=23)
    minute: int | None = Field(default=None, ge=0, le=59)
    timezone: str | None = None


def _public_crawl_run(run: dict) -> dict:
    allowed = {
        "id",
        "started_at",
        "finished_at",
        "status",
        "pages_fetched",
        "pages_failed",
        "robots_blocked",
        "publications_seen",
        "publications_inserted",
        "publications_updated",
        "publications_changed",
        "publications_unchanged",
        "publications_rejected",
        "index_documents",
        "error_message",
        "trigger_type",
    }
    return {key: value for key, value in run.items() if key in allowed}


def _public_event(event: dict) -> dict | None:
    event_type = str(event.get("event_type", "")).lower()
    if event_type not in {
        "start", "policy", "blocked", "fetch", "retry", "content_type",
        "rss_discovery", "openalex", "insert", "update", "reject",
        "stop", "complete", "failed",
    }:
        return None

    result = dict(event)
    if event_type == "start":
        result["message"] = "Publication crawl started."
    return result


@router.get("/stats")
def stats(
    repository=Depends(get_publication_repository),
    index_manager=Depends(get_index_manager),
):
    return {
        "publications": repository.count(),
        "index": index_manager.stats(),
    }


@router.post("/rebuild-index")
def rebuild_index(
    repository=Depends(get_publication_repository),
    index_manager=Depends(get_index_manager),
    search_engine=Depends(get_search_engine),
):
    publications = repository.list_all()

    index_manager.build_from_publications(publications)
    index_manager.save()

    search_engine.refresh_index_references()

    return {
        "status": "rebuilt",
        "index": index_manager.stats(),
    }


@router.get("/scheduler")
def scheduler_status(
    request: Request,
    crawler_scheduler=Depends(get_crawler_scheduler),
):
    configuration = SchedulerSettingsRepository(request.app.state.database).get()
    job = crawler_scheduler.get_job()
    return {
        "enabled": configuration["enabled"],
        "running": crawler_scheduler.scheduler.running,
        "frequency": "weekly",
        "day_of_week": configuration["day_of_week"],
        "hour": configuration["hour"],
        "minute": configuration["minute"],
        "timezone": configuration["timezone"],
        "next_run_time": (
            job.next_run_time.isoformat() if job is not None and job.next_run_time else None
        ),
        "updated_at": configuration.get("updated_at"),
    }


@router.patch("/scheduler")
def update_scheduler_configuration(
    payload: SchedulerConfigurationUpdate,
    request: Request,
):
    update_service = request.app.state.update_service
    if update_service.current_run_id is not None:
        raise HTTPException(
            status_code=409,
            detail="The automatic-update schedule cannot be changed while a crawl is running.",
        )

    repository = SchedulerSettingsRepository(request.app.state.database)
    try:
        configuration = repository.update(
            enabled=payload.enabled,
            day_of_week=payload.day_of_week,
            hour=payload.hour,
            minute=payload.minute,
            timezone=payload.timezone,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    scheduler = request.app.state.crawler_scheduler
    scheduler.apply_configuration(configuration)
    job = scheduler.get_job()

    return {
        "enabled": configuration["enabled"],
        "running": scheduler.scheduler.running,
        "frequency": "weekly",
        "day_of_week": configuration["day_of_week"],
        "hour": configuration["hour"],
        "minute": configuration["minute"],
        "timezone": configuration["timezone"],
        "next_run_time": (
            job.next_run_time.isoformat() if job is not None and job.next_run_time else None
        ),
        "updated_at": configuration.get("updated_at"),
        "message": (
            "Automatic weekly publication updates are enabled."
            if configuration["enabled"]
            else "Automatic publication updates are disabled. Manual updates remain available."
        ),
    }


@router.get("/crawler/config")
def crawler_configuration():
    return {
        "allowed_domain": settings.allowed_domain,
        "seed_url": settings.seed_url,
        "crawl_delay_seconds": settings.crawl_delay,
        "max_pages": settings.max_pages,
        "robots_checked": True,
    }


@router.post("/crawl-now", status_code=202)
def crawl_now(
    crawler_scheduler=Depends(get_crawler_scheduler),
):
    scheduler = crawler_scheduler.scheduler

    if not scheduler.running:
        raise HTTPException(
            status_code=503,
            detail="The background job engine is not running.",
        )

    if crawler_scheduler.update_service.current_run_id is not None:
        raise HTTPException(
            status_code=409,
            detail="A publication crawl is already running.",
        )

    scheduler.add_job(
        crawler_scheduler.update_service.run,
        kwargs={"trigger_type": "manual"},
        trigger="date",
        id="manual_coventry_crawl",
        name="Manual Coventry crawl and index update",
        replace_existing=True,
        max_instances=1,
    )

    return {
        "status": "accepted",
        "message": "The publication crawl has been queued.",
    }


@router.post("/crawl-stop")
def stop_crawl(request: Request):
    service = request.app.state.update_service
    run_id = service.current_run_id
    if not service.request_stop():
        raise HTTPException(status_code=409, detail="No publication crawl is running.")

    return {
        "status": "stopping",
        "run_id": run_id,
        "message": "The crawler will stop after its current request finishes.",
    }


@router.get("/crawl-runs")
def crawl_runs(
    limit: int = Query(20, ge=1, le=100),
    repository=Depends(get_publication_repository),
):
    run_repository = CrawlRunRepository(repository.database)

    return {
        "items": [_public_crawl_run(run) for run in run_repository.latest(limit)],
    }


@router.get("/crawl-runs/{run_id}")
def crawl_run(run_id: int, request: Request):
    repository = CrawlRunRepository(request.app.state.database)
    result = repository.get(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Crawl run not found.")
    return _public_crawl_run(result)


@router.get("/crawl-runs/{run_id}/events")
def crawl_events(
    run_id: int,
    request: Request,
    after_id: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
):
    run_repository = CrawlRunRepository(request.app.state.database)
    if run_repository.get(run_id) is None:
        raise HTTPException(status_code=404, detail="Crawl run not found.")

    events = CrawlEventRepository(request.app.state.database).list_for_run(
        run_id, after_id, limit
    )
    public_events = []
    for event in events:
        normalized = _public_event(event)
        if normalized is not None:
            public_events.append(normalized)
    return {"run_id": run_id, "items": public_events}
