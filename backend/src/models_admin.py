from pydantic import BaseModel
from datetime import datetime
from typing import Any


# User
class UserPublic(BaseModel):
    username: str
    nickname: str | None
    avatar_url: str | None
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


class SubmissionView(SubmissionPublic):
    test_cases: list[dict[str, Any]] | None
    source: str