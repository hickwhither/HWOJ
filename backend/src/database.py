import os
import json
from typing import Annotated
from fastapi import Depends
from sqlmodel import SQLModel, create_engine, Session, select

from .models import *

def get_database_url():
    return os.getenv('DATABASE_URL') or "sqlite:///database.db"


def get_engine_kwargs(database_url: str):
    if database_url.startswith("sqlite"):
        return {"connect_args": {"check_same_thread": False}}
    return {}


engine = create_engine(get_database_url(), **get_engine_kwargs(get_database_url()))


def get_session():
    with Session(engine) as session:
        yield session


def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        statement = select(Problem).where(Problem.code=="aplusb")
        results = session.exec(statement)
        if results.one_or_none() == None:  # Import meta problem
            programs = {}
            if os.path.exists("example/aplusb"):
                for root, dirs, files in os.walk("example/aplusb"):
                    for file in files:
                        if file.endswith(".cpp"):
                            cpp_file_path = os.path.join(root, file)
                            with open(cpp_file_path, "r", encoding="utf-8") as f:
                                source = f.read()

                config = json.load(open("example/aplusb/config.json", "r", encoding="utf-8"))
                statement_content = open("example/aplusb/statement.md", "r", encoding="utf-8").read()

                aplusb = Problem(
                    code="aplusb",
                    name="A plus B",
                    is_public=True,
                    statement=statement_content,
                    programs=programs,
                    **config
                )
                session.add(aplusb)
                session.commit()
                session.refresh(aplusb)


SessionDep = Annotated[Session, Depends(get_session)]