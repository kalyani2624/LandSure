from fastapi import APIRouter
from app.api.endpoints import auth, documents, records, verification, dashboard

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(documents.router)
api_router.include_router(records.router)
api_router.include_router(verification.router)
api_router.include_router(dashboard.router)
