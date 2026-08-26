from fastapi import Request


def get_publication_repository(request: Request):
    return request.app.state.publication_repository


def get_index_manager(request: Request):
    return request.app.state.index_manager


def get_search_engine(request: Request):
    return request.app.state.search_engine


def get_update_service(request: Request):
    return request.app.state.update_service


def get_crawler_scheduler(request: Request):
    return request.app.state.crawler_scheduler
