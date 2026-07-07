import os
import mimetypes
import shutil

from fastapi import APIRouter, Request, HTTPException, UploadFile
from pydantic import BaseModel
from sqlmodel import select

router = APIRouter(prefix="/admin/problem", tags=["admin", "problem"])

from src import PROBLEMS_DIR
os.makedirs(PROBLEMS_DIR, exist_ok=True)

# -- MODELS --
from src import Problem, SessionDep
from src import Problem, ProblemPublic, ProblemCreate, ProblemAdmin

# -- ROUTERS --
@router.post("/create", response_model=ProblemPublic)
def create_problem(problem: ProblemCreate, session: SessionDep):
    os.makedirs(os.path.join(PROBLEMS_DIR, problem.code), exist_ok=True)
    problem_data = problem.model_dump()
    db_problem = Problem.model_validate(problem_data)
    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)
    return db_problem

@router.get("/{problem_code}", response_model=ProblemAdmin)
def problem(problem_code:str, session: SessionDep):
    db_problem = session.get(Problem, problem_code)
    if not db_problem: raise HTTPException(404, "Problem not exists.")
    return db_problem

@router.post("/{problem_code}", response_model=ProblemAdmin)
def problem_edit(problem_code:str, problem_edit: ProblemAdmin, session: SessionDep):
    db_problem = session.get(Problem, problem_code)
    if not db_problem: raise HTTPException(404, "Problem not exists.")
    problem_data = problem_edit.model_dump()
    db_problem.model_validate(problem_data)
    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)
    return db_problem

@router.get("/explorer/{problem_code}/{path}")
def problem_explorer(problem_code:str, path:str):
    path = os.path.join(PROBLEMS_DIR, problem_code, path)
    if not os.path.exists(path): raise HTTPException(404, "Path not exists.")
    if os.path.isdir(path): return os.listdir(path)
    mime = mimetypes.guess_type(path)
    if "text" in mime: return open(path, 'r').read(1024)

@router.post("/explorer/{problem_code}/{path}")
def problem_upload(problem_code:str, path:str, upload: UploadFile):
    path = os.path.join(PROBLEMS_DIR, problem_code, path)
    if not os.path.exists(path): raise HTTPException(404, "Path not exists.")
    destination = os.path.join(path, upload.filename)
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

@router.delete("/explorer/{problem_code}/{path}")
def problem_deletefile(problem_code:str, path:str):
    path = os.path.join(PROBLEMS_DIR, problem_code, path)
    if not os.path.exists(path): raise HTTPException(404, "Path not exists.")
    shutil.rmtree(path)
