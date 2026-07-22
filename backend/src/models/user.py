from typing import TYPE_CHECKING, Optional
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship, Column, JSON

if TYPE_CHECKING:
    from .problem import Problem
    from .submission import Submission


# MODELS
class UserBase(SQLModel):
    # Auth
    id: Optional[int] = Field(primary_key=True)
    username: str = Field(unique=True, index=True)
    password: str = Field()
    email: str = Field(unique=True, index=True)
    discord_id: Optional[str] = Field(index=True)

    # Profiles
    nickname: Optional[str] = Field()
    avatar_url: Optional[str] = Field()
    bio: Optional[str] = Field()
    
    rank: Optional[str] = Field(index=True)
    badges: list[str] = Field(default=[], sa_column=Column(JSON))

    # Permissions
    active: bool = Field(default=True, index=True)
    superuser: bool = Field(default=False, index=True)
    permissions: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Timestamps
    last_login: Optional[datetime] = Field(index=True)
    date_joined: datetime = Field(default_factory=datetime.now, index=True)


class User(UserBase, table=True):
    submissions: list["Submission"] = Relationship(back_populates="user", cascade_delete=True)
    contest_id: str | None = Field(foreign_key="contest.id", ondelete="SET NULL")

    def __repr__(self):
        return f"User({self.username} {self.email})"


# DEPENDENCIES
from fastapi import HTTPException, Request
from sqlmodel import select
from src.database import SessionDep

def create_auth(request: Request, user: User): request.session['id'] = user.id

def delete_auth(request: Request): request.session.pop('auth', None)


def verify_auth(request: Request, session: SessionDep) -> User:
    id = request.session.get("id")
    if not id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    user = session.get(User, id)
    return user


def get_user_by_username(session: SessionDep, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    results = session.exec(statement)
    user = results.one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found or deleted")
    return user


def verify_permissions(request: Request, session: SessionDep) -> User:
    user = verify_auth(request, session)
    

