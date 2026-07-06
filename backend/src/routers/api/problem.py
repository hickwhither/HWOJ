from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from sqlalchemy import func, select
from pydantic import BaseModel

router = APIRouter(prefix="/problem", tags=["problem"])

# -- MODELS --
from src import SessionDep
from src import Problem, ProblemView, ProblemPublic

class ProblemList(BaseModel):
    list[ProblemPublic]

# -- ROUTERS --
@router.get("/", response_model=list[ProblemPublic])
def problem_list(session: SessionDep):
    # total = session.exec(select(func.count()).select_from(Problem)).one()
    # problems = session.exec(select(Problem).offset(20 * p).limit(20)).all()
    
    problems = session.exec(select(Problem)).all()
    return problems

@router.get("/{id}")
def get_problem(session: SessionDep, id: str):
    problem = session.get(Problem, id)
    if not problem:
        raise HTTPException(404, "Problem not found")
    return problem
