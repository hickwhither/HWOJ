from fastapi import APIRouter, Query, HTTPException, Request, Depends
from sqlmodel import func, select, or_
from pydantic import BaseModel
from typing import Optional

from src.database import SessionDep
from src.models.user import User
from src.models.problem import Problem
from src.models import Submission
from src.models_public import ProblemView, ProblemPublic, SubmissionView, SubmissionPublic

# CONFIGURATIONS
router = APIRouter(prefix="/submission", tags=["submission"])

@router.get('/{id}', response_model=SubmissionPublic)
def get_submission_list(session: SessionDep, id: int):
    submission = session.get(Submission, id)
    return submission

@router.get('/problem/{code}', response_model=list[SubmissionPublic])
def get_submission_list(
    session: SessionDep, 
    code: str,
    username: str | None = Query(default=None, description="Filter by username")
):
    statement = select(Submission).where(Submission.problem_code == code)
    if username:
        statement = statement.where(Submission.user_username == username)
    statement = statement.order_by(Submission.id.desc())
    results = session.exec(statement).all()
    return results


@router.get('/rank/{code}', response_model=list[SubmissionPublic])
def get_best_submission_list(session: SessionDep, code: str):
    statement = (
        select(Submission)
        .where(Submission.problem_code == code)
        .where(Submission.status == "D") 
        # Most percentage -> Least time -> Least memory
        .order_by(Submission.percentage.desc(), Submission.time_used.asc(), Submission.memory_used.asc())
        .limit(100)
    )
    results = session.exec(statement).all()
    return results

