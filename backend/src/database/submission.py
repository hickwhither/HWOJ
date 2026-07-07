from datetime import datetime
from typing import Any
from sqlmodel import Field, Relationship, Enum, SQLModel, Column, JSON

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src import Problem, ProblemPublic
    from src import User, UserPublic
    from src import Judger

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
    id: int | None = Field(default=None, primary_key=True)
    user_username: int | None = Field(default=None, foreign_key="user.username")
    user: "User" = Relationship(back_populates="submissions")
    problem_code: str | None = Field(default=None, foreign_key="problem.code")
    problem: "Problem" = Relationship(back_populates="submissions")

    date_created: datetime = Field(default_factory=datetime.now, index=True)
    
    judger_id: str | None = Field(default=None, foreign_key="judger.id")
    judger: "Judger" = Relationship()
    judged_date: datetime | None = Field(default=None)

    # Results
    status: str = Field(default=SUBMISSION_STATUS.QUEUED, index=True)
    time_used: float | None = Field()
    memory_used: float | None = Field()
    total_points: float | None = Field()
    error: str | None = Field()
    test_cases: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    """
    id: int
    batch: int
    verdict: str
    time_used: float
    memory_used: float
    input_data: str
    expected_output: str
    actual_output: str
    error: str
    """

    # Payload
    language: str = Field(index = True)
    source: str = Field()

class SubmissionPublic(SQLModel):
    id: int
    
    # Cell 1
    total_points: float
    status: str
    language: str

    # Cell 2
    problem: "ProblemPublic"
    user: "UserPublic"
    date_created: datetime
    # + Admin buttons

    # Cell 3
    time_used: float
    memory_used: float

class SubmissionView(SubmissionPublic):
    test_cases: list[dict[str, Any]]
