from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select

from src.database import SessionDep
from src.models.contest import Contest
from src.models.links import ContestParticipantLink, ContestProblemLink
from src.models.user import User, verify_auth
from src.models.problem import Problem
from src.models import Submission
from src.models_public import SubmissionPublic

# CONFIGURATIONS
router = APIRouter(prefix="/submission", tags=["user.submission"], dependencies=[Depends(verify_auth)])


def get_contest_or_404(session: SessionDep, code: str) -> Contest:
    contest = session.exec(select(Contest).where(Contest.code == code)).one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest


def get_problem_or_404(session: SessionDep, code: str) -> Problem:
    problem = session.exec(select(Problem).where(Problem.code == code)).one_or_none()
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    return problem


def apply_contest_scope(
    session: SessionDep,
    statement,
    contest_code: str | None,
    problem: Problem | None,
    current_user: User,
):
    if not contest_code:
        return statement

    contest = get_contest_or_404(session, contest_code)
    if not session.get(ContestParticipantLink, (contest.id, current_user.username)):
        raise HTTPException(status_code=403, detail="You are not registered for this contest")
    if problem and not session.get(ContestProblemLink, (contest.id, problem.id)):
        raise HTTPException(status_code=404, detail="Problem not found in contest")
    return statement.where(Submission.contest_id == contest.id)


@router.get('/{id}', response_model=SubmissionPublic)
def get_submission(session: SessionDep, id: int, current_user: User = Depends(verify_auth)):
    submission = session.get(Submission, id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.contest_id:
        contest = session.get(Contest, submission.contest_id)
        if contest and not session.get(ContestParticipantLink, (contest.id, current_user.username)):
            raise HTTPException(status_code=403, detail="You are not registered for this contest")
    return submission


@router.get('/problem/{code}', response_model=list[SubmissionPublic])
def get_submission_list(
    session: SessionDep,
    code: str,
    current_user: User = Depends(verify_auth),
    username: str | None = Query(default=None, description="Filter by username"),
    contest: str | None = Query(default=None, description="Filter by contest code"),
):
    problem = get_problem_or_404(session, code)
    statement = select(Submission).where(Submission.problem_id == problem.id)
    statement = apply_contest_scope(session, statement, contest, problem, current_user)
    if username:
        statement = statement.where(Submission.user.has(User.username == username))
    statement = statement.order_by(Submission.id.desc())
    results = session.exec(statement).all()
    return results


@router.get('/rank/{code}', response_model=list[SubmissionPublic])
def get_best_submission_list(
    session: SessionDep,
    code: str,
    current_user: User = Depends(verify_auth),
    contest: str | None = Query(default=None, description="Filter by contest code"),
):
    problem = get_problem_or_404(session, code)
    statement = (
        select(Submission)
        .where(Submission.problem_id == problem.id)
        .where(Submission.status == "D") 
    )
    statement = apply_contest_scope(session, statement, contest, problem, current_user)
    statement = statement.order_by(
        Submission.percentage.desc(), Submission.time_used.asc(), Submission.memory_used.asc()
    ).limit(100)
    results = session.exec(statement).all()
    return results
