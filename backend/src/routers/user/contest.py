from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import select
from fastapi_pagination import Page
from fastapi_pagination.ext.sqlmodel import paginate

from src.database import SessionDep

from src.models.contest import ContestBase, Contest
from src.public import ContestPublic, ContestView
from src.dependencies.contest import *

from src.models.links import ContestRegistration

from src.models.user import User
from src.dependencies.user import verify_auth

from src.models.problem import Problem

from src.models.submission import Submission
from src.public import ProblemPublic, SubmissionPublic

# CONFIGURATIONS
router = APIRouter(prefix="/contest", tags=["user.contest"], dependencies=[Depends(verify_auth)])


# SCHEMAS
class ContestRegisterRequest(BaseModel):
    password: Optional[str] = None


# ROUTERS
@router.get("", response_model=Page[ContestPublic])
def get_list_contest(session: SessionDep):
    return paginate(session, select(Contest))


@router.get("/{code}", response_model=ContestView)
def get_contest(session: SessionDep, code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    if not is_contest_running(contest):
        contest_data = ContestView.model_validate(contest)
        contest_data.problems = None
        return contest_data
    return contest


@router.post("/{code}/register")
def register_contest(
    session: SessionDep,
    code: str,
    payload: ContestRegisterRequest,
    current_user: User = Depends(verify_auth),
):
    contest = get_contest_or_404(session, code)
    now = datetime.now()
    if contest.registration_start and now < contest.registration_start:
        raise HTTPException(403, "contest.upcoming")
    if contest.registration_end and now > contest.registration_end:
        raise HTTPException(403, "contest.ended")
    if contest.password and payload.password != contest.password:
        raise HTTPException(403, "contest.wrongpassword")
    if not is_contest_participant(session, contest, current_user):
        session.add(ContestRegistration(contest_id=contest.id, user_id=current_user.id))
        session.commit()
    return


@router.get("/{code}/problems", response_model=list[ProblemPublic])
def get_contest_problems(session: SessionDep, code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    return sorted(contest.problems, key=lambda problem: problem.code)

