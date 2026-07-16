from fastapi import APIRouter
router = APIRouter(tags=["webhook"])

from .judger import router as judger_router
router.include_router(judger_router)