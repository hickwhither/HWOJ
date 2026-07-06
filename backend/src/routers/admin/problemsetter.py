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
from src import Problem, ProblemPublic, ProblemAdmin

class ProblemCreate(BaseModel):
    code: str
    name: str
    is_public: str
    authors: list[str]

# -- ROUTERS --
@router.post("/create", response_model=ProblemPublic)
def create_problem(request: Request, problem: ProblemCreate, session: SessionDep):
    os.makedirs(os.path.join(PROBLEMS_DIR, problem.code), exist_ok=True)
    problem = problem.model_dump()
    db_problem = Problem.model_validate(problem)
    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)
    return db_problem

@router.post("/edit/{problem_code}")
def problem_explorer(request: Request, problem_code:str, problem_config: ProblemAdmin, statement:str, session: SessionDep):
    db_problem = session.get(Problem, problem_code)
    if not db_problem: raise HTTPException(404, "Problem not exists.")
    if problem_config: db_problem.config = problem_config
    if statement: db_problem.statement = statement
    session.add(db_problem)
    session.commit()
    session.refresh(db_problem)

@router.get("/explorer/{problem_code}/{path}")
def problem_explorer(request: Request, problem_code:str, path:str):
    path = os.path.join(PROBLEMS_DIR, problem_code, path)
    if not os.path.exists(path): raise HTTPException(404, "Path not exists.")
    if os.path.isdir(path): return os.listdir(path)
    mime = mimetypes.guess_type(path)
    if "text" in mime: return open(path, 'r').read(1024)

@router.post("/explorer/{problem_code}/{path}")
def problem_upload(request: Request, problem_code:str, path:str, upload: UploadFile):
    path = os.path.join(PROBLEMS_DIR, problem_code, path)
    if not os.path.exists(path): raise HTTPException(404, "Path not exists.")
    destination = os.path.join(path, upload.filename)
    with destination.open("wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

@router.delete("/explorer/{problem_code}/{path}")
def problem_explorer(request: Request, problem_code:str, path:str):
    path = os.path.join(PROBLEMS_DIR, problem_code, path)
    if not os.path.exists(path): raise HTTPException(404, "Path not exists.")
    shutil.rmtree(path)
