from datetime import datetime
from typing import Any
from fastapi import APIRouter, Request, HTTPException, Header, Depends
from pydantic import BaseModel
from sqlmodel import select

from src import SessionDep, Submission, Judger, SUBMISSION_STATUS

router = APIRouter(prefix="/judger", tags=["judger"])

# Không cần JudgerHandshake nữa!
class JudgerPing(BaseModel):
    name: str | None = None
    description: str | None = None
    languages: list[str]
    start_time: datetime

class SubmissionUpdateResult(BaseModel):
    submission_id: int
    status: str
    time_used: float | None = None
    memory_used: float | None = None
    error: str | None = None
    test_cases: list[dict[str, Any]]

# -- DEPENDENCIES / HELPERS --
def verify_judge_key(
    request: Request, 
    session: SessionDep, 
    x_judge_key: str = Header(..., description="API Key của máy chấm")
) -> Judger:
    db_judger = session.get(Judger, x_judge_key)

    if not db_judger:
        raise HTTPException(status_code=401, detail="Invalid Judge Key")
    if db_judger.blocked:
        raise HTTPException(status_code=403, detail="Judger is blocked")

    # db_judger will be saved by those endpoints below
    db_judger.last_seen = datetime.now()
    db_judger.last_ip = request.client.host
    return db_judger

ActiveJudge = Depends(verify_judge_key)

# -- ROUTES --

@router.post("/ping")
def info(payload: JudgerPing, session: SessionDep, db_judger: Judger = ActiveJudge):
    update_data = payload.model_dump(exclude_unset=True)
    db_judger.sqlmodel_update(update_data)
    session.add(db_judger)
    session.commit()
    session.refresh(db_judger)
    return db_judger


@router.post("/get-task")
def get_task(session: SessionDep, db_judger: Judger = ActiveJudge):
    submission = session.exec(
        select(Submission)
        .where(Submission.status == SUBMISSION_STATUS.QUEUED)
        .order_by(Submission.date_created, Submission.id)
        .with_for_update(skip_locked=True)
    ).first()
    
    if not submission:
        session.commit() # Vẫn commit để cập nhật last_seen từ dependency
        return {"task": None}

    submission.status = SUBMISSION_STATUS.PROCESSING
    submission.judger = db_judger
    submission.judged_date = datetime.now()
    
    session.add(submission)
    session.commit()
    session.refresh(submission)

    return {
        "task": {
            "id": submission.id,
            "problem_code": submission.problem_code,
            "language": submission.language,
            "source_code": submission.source_code
        }
    }


@router.post("/update-result")
def update_result(payload: SubmissionUpdateResult, session: SessionDep, db_judger: Judger = ActiveJudge):
    submission = session.get(Submission, payload.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    update_data = payload.model_dump(exclude={"submission_id"}, exclude_unset=True)
    
    submission.sqlmodel_update(update_data)
    session.add(submission)
    session.commit()
    return {"message": "Success"}