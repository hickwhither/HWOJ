from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
import math
from sqlalchemy import func


router = APIRouter(prefix="/api/p", tags=["user", "problem"])

# -- MODELS --
from .. import SessionDep, Problem


# -- ROUTERS --
@router.get("/")
def problem_list(session: SessionDep):
    # total = session.exec(select(func.count()).select_from(Problem)).one()
    # problems = session.exec(select(Problem).offset(20 * p).limit(20)).all()
    
    problems = session.exec(select(Problem)).all()

    problem_json = [
        {
            "oj": prob.oj,
            "id": prob.id,
            "link": prob.link,
            "updated_at": prob.updated_at,
            "title": prob.title,
            "rating": prob.rating,
        }
        for prob in problems
    ]

    return problem_json

@router.get("/problem/{id}")
def get_problem(session: SessionDep, id: str):
    problem = session.get(Problem, id)
    if not problem:
        raise HTTPException(404, "Problem not found")
    return problem
