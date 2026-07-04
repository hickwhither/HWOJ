from typing import Annotated
from datetime import datetime, time

from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine

from pwdlib import PasswordHash

class User(SQLModel, table=True):
    username: str = Field(primary_key=True)
    password: str
    discord_id: int
    
    created_at: datetime = Field(default_factory=lambda: datetime.now())

    def __repr__(self):
        return f"User({self.id}, {self.username})"

class Problem(SQLModel, table=True):
    id: str = Field(primary_key=True, index=True)
    oj: str = Field(index=True)
    link: str
    updated_at: datetime = Field(default_factory=lambda: datetime.now())

    title: str = Field(default="No title", index=True)
    description: str = Field(default="")
    translated: str = Field(default="")

    timelimit: int = Field(default=0)
    memorylimit: int = Field(default=0)
    input: str = Field(default="")
    output: str = Field(default="")

    rating: int | None = Field(index=True)


class Submission(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    problem_id: str = Field(index=True, foreign_key="problem.id")
    language: str = Field(index=True)
    source_code: str
    status: str = Field(default="Pending", index=True)
    verdict: str | None = Field(default=None, index=True)
    score: float = Field(default=0)
    time_used: float = Field(default=0)
    memory_used: float = Field(default=0)
    judge_name: str | None = Field(default=None, index=True)
    result: str | None = Field(default=None)
    created_at: datetime = Field(default_factory=lambda: datetime.now(), index=True)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(), index=True)


sqlite_url = f"sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
