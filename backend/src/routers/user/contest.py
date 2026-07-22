from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import func, select

from src.database import SessionDep
from src.models.contest import *
from src.models.links import ContestRegistration
from src.models.user import User, verify_auth
from src.models.problem import Problem
from src.models.submission import Submission
from src.models_public import ContestPublic, ContestView, ProblemPublic, SubmissionPublic

# CONFIGURATIONS
router = APIRouter(prefix="/contest", tags=["user.contest"], dependencies=[Depends(verify_auth)])


# SCHEMAS
class ContestPageResponse(BaseModel):
    contests: list[ContestPublic]
    total: int
    total_pages: int


class ContestRegisterRequest(BaseModel):
    password: Optional[str] = None


# ROUTERS
@router.get("", response_model=ContestPageResponse)
def get_contest_list(
    session: SessionDep,
    current_user: User = Depends(verify_auth),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    code: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
):
    query = select(Contest)
    if code:
        query = query.where(Contest.code.icontains(code))
    if title:
        query = query.where(Contest.title.icontains(title))
    if not current_user.superuser:
        query = query.where(Contest.is_public == True)

    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    total_pages = max(1, (total + limit - 1) // limit)
    contests = session.exec(
        query.order_by(Contest.start_time.desc()).offset((page - 1) * limit).limit(limit)
    ).all()
    return {"contests": contests, "total": total, "total_pages": total_pages}


@router.get("/{code}", response_model=ContestView)
def get_contest(session: SessionDep, code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
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
        raise HTTPException(status_code=403, detail="Registration has not started")
    if contest.registration_end and now > contest.registration_end:
        raise HTTPException(status_code=403, detail="Registration has ended")
    if contest.password and payload.password != contest.password:
        raise HTTPException(status_code=403, detail="Incorrect contest password")
    if not is_contest_participant(session, contest, current_user):
        session.add(ContestRegistration(contest_id=contest.id, user_id=current_user.id))
        session.commit()
    return {"message": "Registered successfully"}


@router.get("/{code}/problems", response_model=list[ProblemPublic])
def get_contest_problems(session: SessionDep, code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    return sorted(contest.problems, key=lambda problem: problem.code)


@router.get("/{code}/submissions", response_model=list[SubmissionPublic])
def get_contest_submissions(
    session: SessionDep,
    code: str,
    current_user: User = Depends(verify_auth),
    problem_code: Optional[str] = Query(None),
    username: Optional[str] = Query(None),
):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    statement = select(Submission).where(Submission.contest_id == contest.id)
    if problem_code:
        problem = session.exec(select(Problem).where(Problem.code == problem_code)).one_or_none()
        if not problem:
            raise HTTPException(status_code=404, detail="Problem not found")
        statement = statement.where(Submission.problem_id == problem.id)
    if username:
        user = session.exec(select(User).where(User.username == username)).one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        statement = statement.where(Submission.user_id == user.id)
    return session.exec(statement.order_by(Submission.id.desc())).all()

