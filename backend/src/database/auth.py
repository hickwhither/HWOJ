from datetime import datetime
from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src import Problem, Submission

from .link import ProblemAuthorLinks

class User(SQLModel, table=True):
    # Auth
    username: str = Field(primary_key=True, index=True)
    password: str = Field(nullable=False)
    email: str = Field(unique=True, index=True)

    # Profiles
    nickname: str | None = Field(default=None)
    avatar_url: str | None = Field(default=None)
    bio: str = Field(default="")

    # Permissions
    active: bool = Field(default=True, index=True)
    staff: bool = Field(default=False)
    superuser: bool = Field(default=False)

    # Timestamps
    last_login: datetime | None = Field(default=None, index=True)
    date_joined: datetime = Field(default_factory=datetime.now, index=True)

    problems: list["Problem"] = Relationship(back_populates="authors", link_model=ProblemAuthorLinks)
    submissions: list["Submission"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"User({self.username})"

class UserCreate(SQLModel):
    username: str
    password: str
    email: str

class UserPublic(SQLModel):
    username: str
    nickname: str | None
    avatar_url: str | None

class UserView(UserPublic):
    bio: str | None
