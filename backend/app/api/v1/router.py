from fastapi import APIRouter
from app.api.v1.auth import router as auth_router
from app.api.v1.documents import router as documents_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.queries import router as queries_router
from app.api.v1.admin import router as admin_router

api_v1_router = APIRouter()
api_v1_router.include_router(auth_router)
api_v1_router.include_router(documents_router)
api_v1_router.include_router(analysis_router)
api_v1_router.include_router(queries_router)
api_v1_router.include_router(admin_router)
