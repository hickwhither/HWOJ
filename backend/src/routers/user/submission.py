from fastapi import APIRouter, Query, HTTPException, Depends
from sqlmodel import select

from src.database import SessionDep
from src.models.contest import Contest
from src.models.links import ContestRegistration, ContestTask
from src.models.user import User, verify_auth
from src.models.problem import Problem, get_problem_by_code
from src.models import Submission
from src.models_public import SubmissionPublic

# CONFIGURATIONS
router = APIRouter(prefix="/submission", tags=["user.submission"], dependencies=[Depends(verify_auth)])

@router.get('/{id}', response_model=SubmissionPublic)
def get_submission(session: SessionDep, id: int, current_user: User = Depends(verify_auth)):
    submission = session.get(Submission, id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    if submission.contest_id:
        contest = session.get(Contest, submission.contest_id)
        if contest and not session.get(ContestRegistration, (contest.id, current_user.username)):
            raise HTTPException(status_code=403, detail="You are not registered for this contest")
    return submission


@router.get('/problem/{code}', response_model=list[SubmissionPublic])
def get_submission_list(
    session: SessionDep,
    code: str,
    username: str | None = Query(default=None, description="Filter by username"),
):
    problem = get_problem_by_code(session, code)
    statement = select(Submission).where(Submission.problem_id == problem.id)
    if username:
        statement = statement.where(Submission.user.has(User.username == username))
    statement = statement.order_by(Submission.id.desc())
    results = session.exec(statement).all()
    return results


@router.get('/rank/{code}', response_model=list[SubmissionPublic])
def get_best_submission_list(session: SessionDep, code: str):
    problem = get_problem_by_code(session, code)
    statement = (
        select(Submission)
        .where(Submission.problem_id == problem.id)
        .where(Submission.status == "D") 
    )
    statement = statement.order_by(
        Submission.percentage.desc(), Submission.time_used.asc(), Submission.memory_used.asc()
    ).limit(100)
    results = session.exec(statement).all()
    return results
