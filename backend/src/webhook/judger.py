from datetime import datetime
from typing import Any
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlmodel import select

from src import SessionDep
from src import Submission, SUBMISSION_STATUS

class SubmissionUpdateResult(BaseModel):
    id: int
    status: str
    time_used: float | None = None
    memory_used: float | None = None
    error: str | None = None
    test_cases: list[dict[str, Any]] | None = None

class SubmissionJudge(BaseModel):
    id: int
    language: str
    source: str
    problem_code: str

active_judgers = {}    

# -- DEPENDENCIES / HELPERS --
from src import JUGER_SECRET_KEY
def verify_judge_key(
    request: Request, 
    session: SessionDep, 
    name: str = Header(..., description="Your name"),
    authentication: str = Header(..., description="Your Key"),
    message: str | None = Header(None, description="whatever you say bro")
) -> str:
    if authentication != JUGER_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid Judge Key")
    active_judgers[name] = {
        "message": message,
        "last_seen": datetime.now()
    }
    return name

ActiveJudge = Depends(verify_judge_key)

# -- ROUTES --
router = APIRouter(prefix="/judger", tags=["judger"])


@router.post("/get-task", response_model=SubmissionJudge|None)
def get_task(session: SessionDep, judger_name: str = ActiveJudge):
    submission = session.exec(
        select(Submission)
        .where(Submission.status == SUBMISSION_STATUS.QUEUED)
        .order_by(Submission.date_created, Submission.id)
        .with_for_update(skip_locked=True)
    ).first()
    
    if not submission:
        session.commit() # commit to update last_seen
        return

    submission.status = SUBMISSION_STATUS.PROCESSING
    submission.judger_name = judger_name
    submission.judged_date = datetime.now()
    
    session.add(submission)
    session.commit()
    session.refresh(submission)

    return submission


@router.post("/update-result")
def update_result(payload: SubmissionUpdateResult, session: SessionDep, judger_name: str = ActiveJudge):
    submission = session.get(Submission, payload.id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    update_data = payload.model_dump(exclude={"id"}, exclude_unset=True)
    
    submission.sqlmodel_update(update_data)
    session.add(submission)
    session.commit()
    return {"message": "Success"}