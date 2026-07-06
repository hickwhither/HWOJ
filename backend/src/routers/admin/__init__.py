from fastapi import APIRouter
router = APIRouter(prefix="/admin", tags=["admin"])

from .problemsetter import router as problem_router
router.include_router(problem_router)