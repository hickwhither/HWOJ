from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import func, select

from src.database import SessionDep
from src.models.contest import Contest
from src.models.links import ContestRegistration, ContestTask
from src.models.user import User, verify_auth
from src.models.problem import Problem, get_problem_or_404
from src.models.submission import Submission
from src.models_public import ProblemView, ProblemPublic

# CONFIGURATION
router = APIRouter(prefix="/problem", tags=["user.problem"], dependencies=[Depends(verify_auth)])


# SCHEMAS
class SubmissionCreate(BaseModel):
    language: str
    source: str


class ProblemPageResponse(BaseModel):
    problems: list[ProblemPublic]
    total: int
    total_pages: int



# ROUTERS
@router.get("", response_model=ProblemPageResponse)
def get_problem_list(
    session: SessionDep,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    code: Optional[str] = Query(None),
    name: Optional[str] = Query(None),
):
    query = select(Problem).where(Problem.is_public == True)
    if code:
        query = query.where(Problem.code.icontains(code))
    if name:
        query = query.where(Problem.name.icontains(name))

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


@router.get("/{code}", response_model=ProblemView)
def get_problem(
    session: SessionDep,
    code: str
):
    problem = get_problem_or_404(session, code)
    return problem


@router.post("/{code}/submit")
def post_submit(
    session: SessionDep,
    code: str,
    submit_form: SubmissionCreate,
    current_user: User = Depends(verify_auth),
):
    problem = get_problem_or_404(session, code)
    if submit_form.language not in ["cpp", "py", "text"]:
        raise HTTPException(status_code=400, detail="Invalid language")
    
    submit_data = submit_form.model_dump()
    new_submission = Submission(user=current_user, problem=problem, **submit_data)
    session.add(new_submission)
    session.commit()
    session.refresh(new_submission)
    return new_submission.id
