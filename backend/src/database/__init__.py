from typing import Annotated

from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

from .auth import *
from .judger import *
from .problem import *
from .submission import *

sqlite_url = f"sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]
