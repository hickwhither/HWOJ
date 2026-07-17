from sqlmodel import SQLModel
from typing import Any
from datetime import datetime

# User
class UserPublic(SQLModel):
    username: str
    nickname: str | None
    avatar_url: str | None
    rank: str | None
    badges: list[str]

class UserView(UserPublic):
    bio: str | None


# Problem
class ProblemPublic(SQLModel):
    code: str   
    name: str
    is_public: bool
    authors: list["UserPublic"]

class ProblemView(ProblemPublic):
    statement: str

class ProblemCreate(SQLModel):
    code: str
    name: str
    statement: str


# Submission
class SubmissionCreate(SQLModel):
    language: str
    source: str

class SubmissionPublic(SQLModel):
    id: int
    
    # Cell 1
    total_points: float | None
    status: str
    language: str

    # Cell 2
    problem: "ProblemPublic"
    user: "UserPublic"
    date_created: datetime
    # + Admin buttons

    # Cell 3
    time_used: float | None
    memory_used: float | None

class SubmissionView(SubmissionPublic):
    test_cases: list[dict[str, Any]] | None
