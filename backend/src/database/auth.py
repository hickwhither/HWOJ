from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .judger import Problem, Submission

class User(SQLModel, table=True):
    # Auth
    username: str = Field(primary_key=True, index=True)
    password: str = Field(nullable=False)
    email: str = Field(unique=True, index=True)

    # Profiles
    nickname: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None)
    bio: str | None = Field(default=None)

    # Permissions
    active: bool = Field(default=True, index=True)
    staff: bool = Field(default=False)
    superuser: bool = Field(default=False)

    # Timestamps
    last_login: datetime | None = Field(default=None, index=True)
    date_joined: datetime = Field(default_factory=datetime.now, index=True)

    problem_code: int | None = Field(default=None, foreign_key="problem.code")
    submissions: list["Submission"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"User({self.id}, {self.username})"

class UserProfile(BaseModel):
    username: str
    nickname: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None)
    bio: str | None = Field(default=None)
