from fastapi import APIRouter

from app.api.v1.endpoints.lecture import router as lecture_router

v1_router = APIRouter()
v1_router.include_router(lecture_router, prefix="/lectures", tags=["Lectures"])
