from datetime import datetime

from fastapi import APIRouter, Request, HTTPException, Header
from pydantic import BaseModel, Field
from sqlmodel import select

router = APIRouter(prefix="/judge", tags=["judge"])

# -- MODELS --
from database import SessionDep
from database import Submission, SubmissionTestCase
from database import Judger
from database import SUBMISSION_STATUS

class JudgerHandshake(BaseModel):
    name: str
    key: str

class JudgerPing(JudgerHandshake):
    description: str
    languages: list[str]
    start_time: datetime

class SubmissionUpdateResult(JudgerHandshake):
    submission_id: int
    status: SUBMISSION_STATUS
    time_used: float | None = None
    memory_used: float | None = None
    error: str | None = None
    test_cases: list["SubmissionTestCase"]

# -- DEPENDENCIES / HELPERS --
def verify_judge_key(base: JudgerHandshake, request: Request, session: SessionDep) -> Judger:
    db_judger: Judger = session.get(Judger, base.name)
    if not db_judger or not db_judger.key or db_judger.key != base.key:
        raise HTTPException(status_code=401, detail="Unauthorized: Judger not found or invalid key")
    db_judger.last_seen = datetime.now()
    db_judger.last_ip = request.client.host
    return db_judger


# -- ROUTES --
@router.post("/ping")
def info(payload: JudgerPing, request: Request, session: SessionDep):
    db_judger = verify_judge_key(payload, request, session)
    
    # Kết hợp dữ liệu từ payload và dữ liệu sinh tự động
    update_data = payload.model_dump(exclude_unset=True)
    update_data.update({
        "last_seen": datetime.now(),
        "last_ip": request.client.host
    })
    
    db_judger.sqlmodel_update(update_data)
    session.add(db_judger)
    session.commit()
    session.refresh(db_judger)
    
    return db_judger


@router.post("/get-task")
def get_task(payload: JudgerHandshake, request: Request, session: SessionDep):
    """Give a judge one QUEUED submission and atomically mark it as PROCESSING."""
    db_judger = verify_judge_key(payload, request, session)

    submission = session.exec(
        select(Submission)
        .where(Submission.status == SUBMISSION_STATUS.QUEUED)
        .order_by(Submission.date_created, Submission.id)
        .with_for_update(skip_locked=True) # avoid race condition
    ).first()
    if not submission:
        return

    submission.status = SUBMISSION_STATUS.PROCESSING
    submission.judged_on = db_judger.name
    submission.judged_date = datetime.now()
    
    session.add(submission)
    session.commit()
    session.refresh(submission)

    return {
        "task":{
            "id": submission.id,
            "problem_code": submission.problem_code,
            "config": submission.problem.config,
            "language": submission.language,
            "source_code": submission.source_code
        }
    }


@router.post("/update-result")
def update_result(payload: SubmissionUpdateResult, request: Request, session: SessionDep):
    """Receive the final result for a judged submission."""
    db_judger = verify_judge_key(payload, request, session)

    submission = session.get(Submission, payload.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    payload = SubmissionUpdateResult.model_dump()
    if SubmissionUpdateResult.status == SUBMISSION_STATUS.GRADING:
        ...
    submission.sqlmodel_update(SubmissionUpdateResult)
    session.add(submission)
    session.commit()
    session.refresh(submission)
