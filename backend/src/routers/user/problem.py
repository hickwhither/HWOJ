from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import func, select

from src.database import SessionDep
from src.models.contest import Contest
from src.models.links import ContestParticipantLink, ContestProblemLink
from src.models.user import User, verify_auth
from src.models.problem import Problem
from src.models.submission import Submission
from src.models_public import ProblemView, ProblemPublic

# CONFIGURATION
router = APIRouter(prefix="/problem", tags=["user.problem"], dependencies=[Depends(verify_auth)])


# SCHEMAS
class SubmissionCreate(BaseModel):
    language: str
    source: str


class ProblemPageResponse(BaseModel):
    problems: list[ProblemPublic]
    total: int
    total_pages: int


def get_problem_or_404(session: SessionDep, code: str) -> Problem:
    problem = session.exec(select(Problem).where(Problem.code == code)).one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


def get_contest_or_404(session: SessionDep, code: str) -> Contest:
    contest = session.exec(select(Contest).where(Contest.code == code)).one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest


def ensure_user_joined_contest(session: SessionDep, contest: Contest, user: User) -> None:
    if not session.get(ContestParticipantLink, (contest.id, user.username)):
        raise HTTPException(status_code=403, detail="You are not registered for this contest")


def ensure_problem_in_contest(session: SessionDep, contest: Contest, problem: Problem) -> None:
    if not session.get(ContestProblemLink, (contest.id, problem.id)):
        raise HTTPException(status_code=404, detail="Problem not found in contest")


def ensure_contest_running(contest: Contest) -> None:
    now = datetime.now()
    if now < contest.start_time:
        raise HTTPException(status_code=403, detail="Contest has not started")
    if now > contest.end_time:
        raise HTTPException(status_code=403, detail="Contest has ended")


def validate_contest_problem_access(
    session: SessionDep,
    contest_code: str | None,
    problem: Problem,
    current_user: User,
    require_running: bool = False,
) -> Contest | None:
    if not contest_code:
        if not problem.is_public:
            raise HTTPException(status_code=403, detail="Problem is not public")
        return None

    contest = get_contest_or_404(session, contest_code)
    ensure_user_joined_contest(session, contest, current_user)
    ensure_problem_in_contest(session, contest, problem)
    if require_running:
        ensure_contest_running(contest)
    return contest


# ROUTERS
@router.get("", response_model=ProblemPageResponse)
def get_problem_list(
    session: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    code: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
):
    query = select(Problem).where(Problem.is_public == True)
    if code:
        query = query.where(Problem.code.icontains(code))
    if name:
        query = query.where(Problem.name.icontains(name))

    count_query = select(func.count()).select_from(query.subquery())
    total = session.exec(count_query).one()
    total_pages = max(1, (total + limit - 1) // limit)
    query = query.offset((page - 1) * limit).limit(limit)
    problems = session.exec(query).all()

    return {
        "problems": problems,
        "total": total,
        "total_pages": total_pages
    }


@router.get("/{code}", response_model=ProblemView)
def get_problem(
    session: SessionDep,
    code: str,
    contest: str | None = Query(default=None),
    current_user: User = Depends(verify_auth),
):
    problem = get_problem_or_404(session, code)
    validate_contest_problem_access(
        session, contest, problem, current_user, require_running=bool(contest)
    )
    return problem


@router.post("/{code}/submit")
def post_submit(
    session: SessionDep,
    code: str,
    submit_form: SubmissionCreate,
    contest: str | None = Query(default=None),
    current_user: User = Depends(verify_auth),
):
    problem = get_problem_or_404(session, code)
    active_contest = validate_contest_problem_access(
        session, contest, problem, current_user, require_running=bool(contest)
    )
    if submit_form.language not in ["cpp", "py", "text"]:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    submit_data = submit_form.model_dump()
    new_submission = Submission(user=current_user, problem=problem, contest=active_contest, **submit_data)
    session.add(new_submission)
    session.commit()
    session.refresh(new_submission)
    return new_submission.id
