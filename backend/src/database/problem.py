from sqlmodel import Field, Relationship, SQLModel, Column, JSON

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src import User, UserPublic
    from src import Submission

from .link import ProblemAuthorLinks

class Problem(SQLModel, table=True):
    code: str = Field(primary_key=True, index=True)
    name: str = Field(default="No name", index=True)
    is_public: bool = Field(default=False, index=True)
    
    statement: str = Field(default="No statement")

    time_limit: int = Field(default=1000)
    memory_limit: int = Field(default=131072) # KB
    input: str | None = Field(default=None)
    output: str | None = Field(default=None)
    answer: str | None = Field(default=None)
    checker: str | None = Field(default=None)
    validator: str | None = Field(default=None)
    batches: list[dict[str, str|list]] = Field(default = [], sa_column=Column(JSON))
    
    authors: list["User"] = Relationship(back_populates="problems", link_model=ProblemAuthorLinks)
    submissions: list["Submission"] = Relationship(back_populates="problem")

class ProblemPublic(SQLModel):
    code: str
    name: str
    is_public: bool

class ProblemView(ProblemPublic):
    statement: str
    time_limit: int
    memory_limit: int
    input: str
    output: str
    authors: list

class ProblemAdmin(ProblemView):
    answer: str
    checker: str
    validator: str
    batches: list[dict[str, str|list]]
