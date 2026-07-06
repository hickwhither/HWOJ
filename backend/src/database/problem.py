from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel, Column, JSON

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import User, UserProfile, Submission

class Batches(BaseModel):
    score: int
    tests: list[str|list]

class ProblemConfig(BaseModel):
    time_limit: int = 1000 # ms
    memory_limit: int = 131072 # KB
    answer: str | None
    checker: str | None
    validator: str | None
    batches: list[Batches]

class Problem(SQLModel, table=True):
    code: str = Field(primary_key=True, index=True)
    name: str = Field(default="No name", index=True)
    is_public: bool = Field(default=False, index=True)
    
    statement: str = Field(default="No statement")
    config: ProblemConfig = Field(default=ProblemConfig(), sa_column=Column(JSON))
    
    authors: list["User"] = Relationship(back_populates="problem")
    submissions: list["Submission"] = Relationship(back_populates="problem")

class ProblemShort(BaseModel):
    code: str
    name: str
    is_public: bool
    authors: list["UserProfile"]