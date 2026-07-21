from fastapi import APIRouter
router = APIRouter(prefix="/api", tags=["user"])

from .auth import router as auth_router
from .problem import router as problem_router
from .submission import router as submission_router
from .confirm import router as confirm_router
router.include_router(auth_router)
router.include_router(problem_router)
router.include_router(submission_router)
router.include_router(confirm_router)