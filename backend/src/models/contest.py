from typing import TYPE_CHECKING, Optional, Any
from sqlmodel import SQLModel, Field, Relationship, Column, JSON, TEXT
from datetime import datetime

from .links import ContestProblemLink, ContestParticipantLink

if TYPE_CHECKING:
    from .user import User
    from .problem import Problem
    from .submission import Submission

class ContestBase(SQLModel):
    id: Optional[int] = Field(primary_key=True)
    code: str = Field(unique=True, index=True)
    title: Optional[str] = Field(index=True)
    description: Optional[str] = Field(sa_type=TEXT)
    
    registration_start: Optional[datetime] = Field(index=True)
    registration_end: Optional[datetime] = Field(index=True)
    start_time: datetime = Field(index=True)
    end_time: datetime = Field(index=True)
    
    is_public: bool = Field(default=True, index=True)
    password: Optional[str] = Field()

class Contest(ContestBase, table=True):
    problems: list["Problem"] = Relationship(link_model=ContestProblemLink)
    participants: list["User"] = Relationship(link_model=ContestParticipantLink)
    submissions: list["Submission"] = Relationship(back_populates="contest")