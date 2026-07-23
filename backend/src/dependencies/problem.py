from fastapi import HTTPException, Request
from sqlmodel import select

from src.database import SessionDep
from src.models import Problem

def get_problem_or_404(session: SessionDep, code: str) -> Problem | None:
    statement = select(Problem).where(Problem.code == code)
    results = session.exec(statement)
    problem = results.one_or_none()
    if not problem:
        raise HTTPException(404, "contest.notfound")
    return problem