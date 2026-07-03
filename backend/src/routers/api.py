from fastapi import APIRouter, Request, HTTPException, BackgroundTasks
from pydantic import BaseModel
import math
from sqlalchemy import func

from .. import SessionDep, Problem
from sqlmodel import select

router = APIRouter(prefix="/api", tags=["frontend"])

@router.get("/problems")
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

@router.post("/problem/{id}/update")
def update_problem(request: Request, session: SessionDep, background_tasks: BackgroundTasks, id: str):
    problem = session.get(Problem, id)
    if not problem:
        raise HTTPException(404, "Problem not found")
    
    oj = id.split('_')[0]
    background_tasks.add_task(request.app.bots[oj].fetch, problemid=id)
    
    return {"success": f"{id} has been queued to update"}
