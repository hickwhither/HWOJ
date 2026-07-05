import os
from datetime import datetime

from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select

router = APIRouter(prefix="/admin/p", tags=["user"])

PROBLEMS_DIR = os.getenv("PROBLEMS_DIR", "/data/problems")
os.makedirs(PROBLEMS_DIR, exist_ok=True)

# -- MODELS --
from database import Problem, ProblemShort

@router.post("/create")
def login(request: Request, PasswordForm: PasswordForm, session: SessionDep):
    ...

