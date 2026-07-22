from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship

from .links import ContestTask, ContestRegistration

if TYPE_CHECKING:
    from .user import User
    from .problem import Problem
    from .submission import Submission


# Models
class ContestBase(SQLModel):
    id: Optional[int] = Field(primary_key=True)
    code: str = Field(unique=True, index=True)
    title: Optional[str] = Field(index=True)
    description: Optional[str] = Field(sa_type=TEXT)
    
    registration_start: Optional[datetime] = Field(index=True)
    registration_end: Optional[datetime] = Field(index=True)
    start_time: datetime = Field(index=True)
    end_time: datetime = Field(index=True)
    
    is_public: bool = Field(default=True, index=True)
    password: Optional[str] = Field()


class Contest(ContestBase, table=True):
    problems: list["Problem"] = Relationship(link_model=ContestTask)
    participants: list["User"] = Relationship(link_model=ContestRegistration)
    submissions: list["Submission"] = Relationship(back_populates="contest")


# DEPENDENCIES
from fastapi import HTTPException, Request
from sqlmodel import select
from src.database import SessionDep


def get_contest_or_404(session: SessionDep, code: str) -> Contest:
    contest = session.exec(select(Contest).where(Contest.code == code)).one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest


def ensure_contest_running(contest: Contest) -> None:
    now = datetime.now()
    if now < contest.start_time:
        raise HTTPException(status_code=403, detail="Contest has not started")
    if now > contest.end_time:
        raise HTTPException(status_code=403, detail="Contest has ended")


def is_contest_participant(session: SessionDep, contest: Contest, user: User) -> bool:
    return bool(session.get(ContestRegistration, (contest.id, user.id)))


def ensure_can_view_contest(contest: Contest, user: User, session: SessionDep) -> None:
    if contest.is_public or is_contest_participant(session, contest, user):
        return
    raise HTTPException(status_code=403, detail="You are not registered for this contest")


