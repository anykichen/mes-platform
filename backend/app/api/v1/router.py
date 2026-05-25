from fastapi import APIRouter
from app.api.v1.endpoints import dashboard, projects, stations, account, tasks

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(dashboard.router)
api_router.include_router(projects.router)
api_router.include_router(stations.router)
api_router.include_router(account.router)
api_router.include_router(tasks.router)
