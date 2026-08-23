"""FastAPI application setup and shared service initialisation."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.admin_routes import router as admin_router
from api.publication_routes import router as publication_router
from api.search_routes import router as search_router
from api.clustering_routes import router as clustering_router
from api.system_routes import router as system_router
from clustering.service import ClusteringService
from database.crawl_run_repository import CrawlRunRepository
from database.scheduler_settings_repository import SchedulerSettingsRepository
from crawler.scheduler import CrawlerScheduler
from crawler.update_service import CrawlUpdateService
from database.database import Database
from database.publication_repository import PublicationRepository
from indexing.index_manager import IndexManager
from search.search_engine import SearchEngine


@asynccontextmanager
async def lifespan(app: FastAPI):
    database = Database()
    database.initialize()
    CrawlRunRepository(database).stop_orphaned_runs()

    publication_repository = PublicationRepository(database)
    index_manager = IndexManager()

    try:
        index_manager.load()
    except FileNotFoundError:
        publications = publication_repository.list_all()
        index_manager.build_from_publications(publications)
        index_manager.save()

    search_engine = SearchEngine(
        index_manager=index_manager,
        publication_repository=publication_repository,
    )

    update_service = CrawlUpdateService(
        database=database,
        publication_repository=publication_repository,
        index_manager=index_manager,
        search_engine=search_engine,
    )

    crawler_scheduler = CrawlerScheduler(update_service)
    clustering_service = ClusteringService()

    app.state.database = database
    app.state.publication_repository = publication_repository
    app.state.index_manager = index_manager
    app.state.search_engine = search_engine
    app.state.update_service = update_service
    app.state.crawler_scheduler = crawler_scheduler
    app.state.clustering_service = clustering_service

    crawler_scheduler.start()
    scheduler_config = SchedulerSettingsRepository(database).get()
    crawler_scheduler.apply_configuration(scheduler_config)

    try:
        yield
    finally:
        crawler_scheduler.shutdown()


app = FastAPI(
    title="Coventry Vertical Search Engine API",
    description=(
        "Backend API for the Information Retrieval coursework vertical "
        "publication search engine."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search_router)
app.include_router(publication_router)
app.include_router(admin_router)
app.include_router(clustering_router)
app.include_router(system_router)


@app.get("/")
def root():
    return {
        "name": "Coventry Vertical Search Engine API",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
