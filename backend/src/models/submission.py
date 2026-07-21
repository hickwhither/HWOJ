from typing import TYPE_CHECKING, Optional, Any
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, TEXT
from sqlalchemy import Index


if TYPE_CHECKING:
    from .user import User
    from .problem import Problem
    from .contest import Contest


class SUBMISSION_STATUS(str, Enum):
    QUEUED = "QW"
    PROCESSING = "P"
    GRADING = "G"
    DONE = "D"


class SUBMISSION_VERDICT(str, Enum):
    ACCEPTED = "OK"
    PARTIALLY_ACCEPTED = "PAC"
    WRONG_ANSWER = "WA"
    TIME_LIMIT_EXCEEDED = "TLE"
    MEMORY_LIMIT_EXCEEDED = "MLE"
    OUTPUT_LIMIT_EXCEEDED = "OLE"
    INVALID_RETURN = "IR"
    RUNTIME_ERROR = "RTE"
    COMPILE_ERROR = "CE"
    INTERNAL_ERROR = "IE"
    SHORT_CIRCUITED = "SC"
    ABORTED = "AB"


class Submission(SQLModel, table=True):
    __table_args__ = (
        Index("idx_user_problem", "user_id", "problem_id"),
    )
    
    id: Optional[int] = Field(primary_key=True)
    user_id: str = Field(foreign_key="user.id", ondelete="CASCADE")
    problem_id: str = Field(foreign_key="problem.id", ondelete="CASCADE")
    contest_id: str | None = Field(foreign_key="contest.id", ondelete="SET NULL")
    
    contest: Optional["Contest"] = Relationship(back_populates="submissions")
    user: Optional["User"] = Relationship(back_populates="submissions")
    problem: Optional["Problem"] = Relationship(back_populates="submissions")

    date_created: datetime = Field(default_factory=datetime.now, index=True)
    judger_name: Optional[str] = Field(index=True)
    judged_date: Optional[datetime] = Field()

    # Results
    status: str = Field(default=SUBMISSION_STATUS.QUEUED, index=True)
    time_used: Optional[float] = Field()
    memory_used: Optional[float] = Field()
    percentage: Optional[float] = Field()
    error: Optional[str] = Field()
    test_cases: Optional[list[dict[str, Any]]] = Field(sa_column=Column(JSON))

    # Payload
    language: str = Field(index=True)
    source: str = Field(sa_type=TEXT)

