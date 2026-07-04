import os
from datetime import datetime

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import select

from .. import Problem, SessionDep, Submission

router = APIRouter(prefix="/api/judge", tags=["judge"])


class JudgeHandshake(BaseModel):
    key: str | None = None
    name: str


class JudgeResult(BaseModel):
    key: str | None = None
    name: str
    submission_id: int
    status: str = Field(default="Done")
    verdict: str
    score: float = 0
    time_used: float = 0
    memory_used: float = 0
    result: dict | list | str | None = None


def _configured_key() -> str | None:
    return os.getenv("JUDGE_KEY")


def _authorize(key: str | None, x_judge_key: str | None) -> None:
    expected = _configured_key()
    if not expected:
        return
    supplied = x_judge_key or key
    if supplied != expected:
        raise HTTPException(status_code=401, detail="Invalid judge key")


@router.post("/get-task")
def get_task(payload: JudgeHandshake, session: SessionDep, x_judge_key: str | None = Header(default=None)):
    """Give a judge one pending submission and atomically mark it as judging."""
    _authorize(payload.key, x_judge_key)

    submission = session.exec(
        select(Submission)
        .where(Submission.status == "Pending")
        .order_by(Submission.created_at, Submission.id)
    ).first()
    if not submission:
        return {"task": None}

    problem = session.get(Problem, submission.problem_id)
    submission.status = "Judging"
    submission.judge_name = payload.name
    submission.updated_at = datetime.now()
    session.add(submission)
    session.commit()
    session.refresh(submission)

    return {
        "task": {
            "submission_id": submission.id,
            "problem_id": submission.problem_id,
            "language": submission.language,
            "source_code": submission.source_code,
            "problem": {
                "id": problem.id if problem else submission.problem_id,
                "time_limit": problem.timelimit if problem else 0,
                "memory_limit": problem.memorylimit if problem else 0,
            },
        }
    }


@router.post("/update-result")
def update_result(payload: JudgeResult, session: SessionDep, x_judge_key: str | None = Header(default=None)):
    """Receive the final result for a judged submission."""
    _authorize(payload.key, x_judge_key)

    submission = session.get(Submission, payload.submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    submission.status = payload.status
    submission.verdict = payload.verdict
    submission.score = payload.score
    submission.time_used = payload.time_used
    submission.memory_used = payload.memory_used
    submission.judge_name = payload.name
    submission.result = payload.model_dump_json()
    submission.updated_at = datetime.now()
    session.add(submission)
    session.commit()
    session.refresh(submission)

    return {"success": True, "submission_id": submission.id, "status": submission.status}
