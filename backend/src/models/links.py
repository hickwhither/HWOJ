from sqlmodel import SQLModel, Field
from datetime import datetime


class ContestProblemLink(SQLModel, table=True):
    contest_id: int = Field(foreign_key="contest.id", primary_key=True, ondelete="CASCADE")
    problem_id: str = Field(foreign_key="problem.id", primary_key=True, ondelete="CASCADE")
    
    display_order: int = Field(default=0)
    max_score: float = Field(default=100.0)


class ContestParticipantLink(SQLModel, table=True):
    contest_id: int = Field(foreign_key="contest.id", primary_key=True, ondelete="CASCADE")
    user_username: str = Field(foreign_key="user.username", primary_key=True, ondelete="CASCADE")

    registered_at: datetime = Field(default_factory=datetime.now)
    total_score: float = Field(default=0.0)
    penalty: float = Field(default=0.0)

