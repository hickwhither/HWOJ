from fastapi import APIRouter, Query, HTTPException
from sqlmodel import func, select, or_
from pydantic import BaseModel
from typing import Optional

router = APIRouter(prefix="/problem", tags=["problem"])

# -- MODELS --
from src import SessionDep
from src import Problem, ProblemView, ProblemPublic

# Khai báo model trả về cho phân trang
class ProblemPageResponse(BaseModel):
    problems: list[ProblemPublic]
    total: int
    total_pages: int

# -- ROUTERS --
@router.get("/", response_model=ProblemPageResponse)
def problem_list(
    session: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    code: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
    authors: Optional[str] = Query(None)
):
    query = select(Problem)

    if code:
        query = query.where(Problem.code.icontains(code))
    if name:
        query = query.where(Problem.name.icontains(name))
    if authors:
        query = query.where(Problem.authors.icontains(authors))

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

@router.get("/{id}", response_model=ProblemView)
def get_problem(session: SessionDep, id: str):
    problem = session.get(Problem, id)
    if not problem:
        raise HTTPException(404, "Problem not found")
    return problem
