from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field, Relationship, Enum, SQLModel, Column, JSON

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import Problem

class SUBMISSION_STATUS(str, Enum):
    QUEUED = "QW"
    PROCESSING = "P"
    GRADING = "G"
    DONE = "D"
    
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

# Dùng BaseModel (Pydantic) cho test case vì nó thường lưu dưới dạng JSON trong DB
class SubmissionTestCase(BaseModel):
    id: int
    batch: int | None = None
    status: SUBMISSION_STATUS | None = None
    time_used: float | None = None
    memory_used: float | None = None
    input_data: str
    expected_output: str
    actual_output: str | None = None
    error: str | None = None

class Submission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    user: "Problem" = Relationship(back_populates="submissions")
    problem_code: str | None = Field(default=None, foreign_key="problem.code")
    problem: "Problem" = Relationship(back_populates="submissions")

    date_created: datetime = Field(default_factory=datetime.now, index=True)
    
    judged_on: str | None = Field(default=None) # Tên Judger
    judged_date: datetime | None = Field(default=None)

    # Results
    status: SUBMISSION_STATUS = Field(default=SUBMISSION_STATUS.QUEUED, index=True)
    time_used: float | None = Field()
    memory_used: float | None = Field()
    total_points: float | None = Field()
    error: str | None = Field()
    test_cases: list["SubmissionTestCase"] | None = Field(default=None, sa_column=Column(JSON))

    # Payload
    language: str = Field(index = True)
    source: str = Field()

# Use-case: xem danh sách submission ngắn gọn
class SubmissionShort(BaseModel):
    id: int
    total_points: float
    status: SUBMISSION_STATUS
    language: str
    problem: "Problem"
    date_created: datetime
    time_used: float
    memory_used: float

# Use-case: xem thông tin testcase của bài
class SubmissionTestCaseView(BaseModel):
    id: int
    status: SUBMISSION_STATUS
    test_cases: list[SubmissionTestCase] | None

