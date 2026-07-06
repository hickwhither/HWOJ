from sqlmodel import Field, SQLModel

class ProblemAuthorLinks(SQLModel, table=True):
    user_username: int = Field(foreign_key="user.username", primary_key=True)
    problem_code: int = Field(foreign_key="problem.code", primary_key=True)