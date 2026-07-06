from fastapi import APIRouter
router = APIRouter()

from .admin import router as admin_router
from .api import router as api_router
from .judger import router as judger_router
router.include_router(admin_router)
router.include_router(api_router)
router.include_router(judger_router)