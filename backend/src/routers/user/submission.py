from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import func, select, or_
from pydantic import BaseModel
from typing import Optional

from src.database import SessionDep
from src.models.user import User, verify_auth
from src.models.problem import Problem
from src.models import Submission
from src.models_public import ProblemView, ProblemPublic, SubmissionView, SubmissionPublic

# CONFIGURATIONS
router = APIRouter(prefix="/submission", tags=["user.submission"], dependencies=[Depends(verify_auth)])

@router.get('/{id}', response_model=SubmissionPublic)
def get_submission(session: SessionDep, id: int):
    submission = session.get(Submission, id)
    return submission

@router.get('/problem/{code}', response_model=list[SubmissionPublic])
def get_submission_list(
    session: SessionDep, 
    code: str,
    username: str | None = Query(default=None, description="Filter by username")
):
    statement = select(Submission).where(Submission.problem.has(Problem.code == code))
    if username:
        statement = statement.where(Submission.user.has(User.username == username))
    statement = statement.order_by(Submission.id.desc())
    results = session.exec(statement).all()
    return results


@router.get('/rank/{code}', response_model=list[SubmissionPublic])
def get_best_submission_list(session: SessionDep, code: str):
    statement = (
        select(Submission)
        .where(Submission.problem.has(Problem.code == code))
        .where(Submission.status == "D") 
        # Most percentage -> Least time -> Least memory
        .order_by(Submission.percentage.desc(), Submission.time_used.asc(), Submission.memory_used.asc())
        .limit(100)
    )
    results = session.exec(statement).all()
    return results

