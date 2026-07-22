from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import func, select

from src.database import SessionDep
from src.models.contest import Contest
from src.models.links import ContestParticipantLink
from src.models.problem import Problem
from src.models.submission import Submission
from src.models.user import User, verify_auth
from src.models_public import ContestPublic, ContestView, ProblemPublic, SubmissionPublic

router = APIRouter(prefix="/contest", tags=["user.contest"], dependencies=[Depends(verify_auth)])


class ContestPageResponse(BaseModel):
    contests: list[ContestPublic]
    total: int
    total_pages: int


class SubmissionCreate(BaseModel):
    language: str
    source: str


class ContestRegisterRequest(BaseModel):
    password: Optional[str] = None


def get_contest_or_404(session: SessionDep, code: str) -> Contest:
    contest = session.exec(select(Contest).where(Contest.code == code)).one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest


def ensure_can_view_contest(contest: Contest, user: User, session: SessionDep) -> None:
    if contest.is_public:
        return
    participant = session.get(ContestParticipantLink, (contest.id, user.username))
    if not participant:
        raise HTTPException(status_code=403, detail="You are not registered for this contest")


def ensure_contest_running(contest: Contest) -> None:
    now = datetime.now()
    if now < contest.start_time:
        raise HTTPException(status_code=403, detail="Contest has not started")
    if now > contest.end_time:
        raise HTTPException(status_code=403, detail="Contest has ended")


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
    if not session.get(ContestParticipantLink, (contest.id, current_user.username)):
        session.add(ContestParticipantLink(contest_id=contest.id, user_username=current_user.username))
        session.commit()
    return {"message": "Registered successfully"}


@router.get("/{code}/problems", response_model=list[ProblemPublic])
def get_contest_problems(session: SessionDep, code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    return sorted(contest.problems, key=lambda problem: problem.code)


@router.get("/{code}/problem/{problem_code}", response_model=ProblemPublic)
def get_contest_problem(session: SessionDep, code: str, problem_code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    problem = next((p for p in contest.problems if p.code == problem_code), None)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found in contest")
    return problem


@router.post("/{code}/problem/{problem_code}/submit")
def post_contest_submit(
    session: SessionDep,
    code: str,
    problem_code: str,
    submit_form: SubmissionCreate,
    current_user: User = Depends(verify_auth),
):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    ensure_contest_running(contest)
    problem = next((p for p in contest.problems if p.code == problem_code), None)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found in contest")
    if submit_form.language not in ["cpp", "py", "text"]:
        raise HTTPException(status_code=400, detail="Invalid language")

    submission = Submission(user=current_user, problem=problem, contest=contest, **submit_form.model_dump())
    session.add(submission)
    session.commit()
    session.refresh(submission)
    return submission.id


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


@router.get("/{code}/rank", response_model=list[SubmissionPublic])
def get_contest_rank(session: SessionDep, code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    statement = (
        select(Submission)
        .where(Submission.contest_id == contest.id)
        .where(Submission.status == "D")
        .order_by(Submission.percentage.desc(), Submission.time_used.asc(), Submission.memory_used.asc())
        .limit(100)
    )
    return session.exec(statement).all()
