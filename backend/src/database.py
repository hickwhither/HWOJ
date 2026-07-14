from fastapi import *
from sqlmodel import *
from typing import *
from datetime import datetime
import string, secrets, json



# Links
class ProblemAuthorLinks(SQLModel, table=True):
    user_username: int = Field(foreign_key="user.username", primary_key=True)
    problem_code: int = Field(foreign_key="problem.code", primary_key=True)


# User
class UserBase(SQLModel):
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
    superuser: bool = Field(default=False)
    permissions: list[str] = Field(default_factory=list, sa_column=Column(JSON))

    # Timestamps
    last_login: datetime | None = Field(default=None, index=True)
    date_joined: datetime = Field(default_factory=datetime.now, index=True)

class User(UserBase, table=True):
    problems: list["Problem"] = Relationship(back_populates="authors", link_model=ProblemAuthorLinks)
    submissions: list["Submission"] = Relationship(back_populates="user")

    def __repr__(self):
        return f"User({self.username} {self.email})"


# Problem
class ProblemBase(SQLModel):
    code: str = Field(primary_key=True, index=True)
    name: str = Field(default="No name", index=True)
    is_public: bool = Field(default=False, index=True)    
    statement: str = Field(default="No statement")

class Problem(ProblemBase, table=True):
    authors: list["User"] = Relationship(back_populates="problems", link_model=ProblemAuthorLinks)
    submissions: list["Submission"] = Relationship(back_populates="problem")

    def __repr__(self):
        return f"Problem({self.code} - {self.name})"


# Submissions
class SUBMISSION_STATUS(str, Enum):
    QUEUED = "QW"
    PROCESSING = "P"
    GRADING = "G"
    DONE = "D"

class SUBMISSION_VERDICT(str, Enum):
    ACCEPTED = "OK"
    PARTIALLY_ACCEPTED = "PAC"
    WRONG_ANSWER = "WA"
    TIME_LIMIT_EXCEEDED = "TLE"
    MEMORY_LIMIT_EXCEEDED = "MLE"
    OUTPUT_LIMIT_EXCEEDED = "OLE"
    INVALID_RETURN = "IR"
    RUNTIME_ERROR = "RTE"
    COMPILE_ERROR = "CE"
    INTERNAL_ERROR = "IE"
    SHORT_CIRCUITED = "SC"
    ABORTED = "AB"

class Submission(SQLModel, table=True):
    id: int = Field(primary_key=True)
    user_username: int = Field(foreign_key="user.username")
    user: "User" = Relationship(back_populates="submissions")
    problem_code: str = Field(foreign_key="problem.code")
    problem: "Problem" = Relationship(back_populates="submissions")

    date_created: datetime = Field(default_factory=datetime.now, index=True)
    
    # judger_id: str | None = Field(default=None, foreign_key="judger.id")
    # judger: "Judger" = Relationship()\
    judger_name: str | None = Field(default = None)
    judged_date: datetime | None = Field(default=None)

    # Results
    status: str = Field(default=SUBMISSION_STATUS.QUEUED, index=True)
    time_used: float | None = Field()
    memory_used: float | None = Field()
    percentage: float | None = Field()
    error: str | None = Field()
    test_cases: list[dict[str, Any]] | None = Field(default=None, sa_column=Column(JSON))
    """
    id: int
    batch: int
    verdict: str
    time_used: float
    memory_used: float
    input_data: str
    expected_output: str
    actual_output: str
    error: str
    """

    # Payload
    language: str = Field(index=True)
    source: str = Field()


# -- init --
from pwdlib import PasswordHash
pwd = PasswordHash.recommended()

sqlite_url = f"sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def get_session():
    with Session(engine) as session:
        yield session
    
def init_db():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        if not session.get(User, "admin"):
            admin_user = User(username="admin", password=pwd.hash("admin"), email="admin@example.com")
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
        else:
            admin_user = session.get(User, 'admin')
        if not session.get(Problem, "aplusb"):
            config = json.load(open("example/aplusb/.json", "r"))
            aplusb = Problem(
                code="aplusb", name="A plus B", is_public=True,
                statement=open("example/aplusb.md", "r").read(),
                authors = [admin_user],
                **config
            )
            session.add(aplusb)
            session.commit()
            session.refresh(aplusb)

SessionDep = Annotated[Session, Depends(get_session)]
