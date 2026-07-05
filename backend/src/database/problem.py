from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from . import User, Submission

class Problem(SQLModel, table=True):
    code: str = Field(primary_key=True, index=True)
    name: str = Field(default="No name", index=True)
    is_public: bool = Field(default=False, index=True)
    
    authors: list["User"] = Relationship(back_populates="problem")
    submissions: list["Submission"] = Relationship(back_populates="problem")

class ProblemShort(BaseModel):
    code: str
    name: str
    is_public: bool
    authors: list["User"]