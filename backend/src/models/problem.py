from typing import TYPE_CHECKING, Optional, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, TEXT

if TYPE_CHECKING:
    from .user import User
    from .submission import Submission


class ProblemBase(SQLModel):
    id: Optional[int] = Field(primary_key=True)
    code: str = Field(unique=True, index=True)
    name: Optional[str] = Field(index=True)
    statement: Optional[str] = Field(sa_type=TEXT)
    is_public: bool = Field(default=False, index=True)    
    
    type: Optional[str] = Field()
    time_limit: float = Field(default=1)
    memory_limit: int = Field(default=32768)
    input: Optional[str] = Field()
    output: Optional[str] = Field()
    programs: Optional[dict[str, str]] = Field(default={}, sa_column=Column(JSON))
    subtasks: Optional[dict[str, dict[str, Any]]] = Field(default={}, sa_column=Column(JSON))
    


class Problem(ProblemBase, table=True):
    submissions: list["Submission"] = Relationship(back_populates="problem", cascade_delete=True)
    contest_code: Optional[str] = Field(foreign_key="contest.code", ondelete="SET NULL")

    def __repr__(self):
        return f"Problem({self.code} - {self.name})"

