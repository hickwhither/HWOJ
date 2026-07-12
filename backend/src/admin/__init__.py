from fastapi import APIRouter, Depends
from fastapi import Request, HTTPException, status
from src import SessionDep, User

router = APIRouter(prefix="/admin", tags=["admin"])

from .problem_manager import router as problem_router
router.include_router(problem_router)