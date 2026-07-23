from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON
import random

if TYPE_CHECKING:
    from .problem import Problem
    from .submission import Submission

DEFAULT_AVATARS = [
    "dolly.webp",
    "ei_snailchan.webp",
    "ei_snailien.webp",
    "nanahira.webp",
    "seal.webp",
    "sheep.webp",
    "Telu.webp",
    "xchara.webp",
]

class UserBase(SQLModel):
    # Auth
    id: Optional[int] = Field(primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str = Field()
    email: str = Field(unique=True, index=True)
    discord_id: Optional[str] = Field(index=True)

    # Profiles
    nickname: Optional[str] = Field()
    avatar_url: Optional[str] = Field(default_factory=lambda: "/default-avatars/"+random.choice(DEFAULT_AVATARS))
    bio: Optional[str] = Field()
    rating: Optional[int] = Field(index=True)
    elo: Optional[int] = Field(index=True)
    rank: Optional[str] = Field(index=True)
    badges: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Permissions
    active: bool = Field(default=True, index=True)
    superuser: bool = Field(default=False, index=True)
    permissions: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Timestamps
    last_login: Optional[datetime] = Field(index=True)
    date_joined: datetime = Field(default_factory=datetime.now, index=True)


class User(UserBase, table=True):
    submissions: list["Submission"] = Relationship(back_populates="user", cascade_delete=True)
    contest_id: Optional[str] = Field(foreign_key="contest.id", ondelete="SET NULL")

    def __repr__(self):
        return f"User({self.username} {self.email})"

