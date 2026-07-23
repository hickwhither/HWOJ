from pydantic import BaseModel
from datetime import datetime
from typing import Any


# User
class UserPublic(BaseModel):
    username: str
    nickname: str | None
    avatar_url: str | None
    rating: int | None
    elo: int | None
    rank: str | None
    badges: list[str]


class UserView(UserPublic):
    bio: str | None


# Problem
class ProblemPublic(BaseModel):
    code: str
    name: str | None
 

class ProblemView(ProblemPublic):
    statement: str | None
    time_limit: float
    memory_limit: int
    input: str | None
    output: str | None


# Contest
class ContestPublic(BaseModel):
    code: str
    title: str | None
    description: str | None
    registration_start: datetime | None
    registration_end: datetime | None
    start_time: datetime
    end_time: datetime
    is_public: bool


class ContestView(ContestPublic):
    problems: list[ProblemPublic] = []


#Submission
class SubmissionPublic(BaseModel):
    id: int
    
    # Cell 1
    percentage: float | None
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
    test_cases: list[dict[str, Any]] | None


class SubmissionView(SubmissionPublic):
    source: str
