from datetime import datetime
from sqlmodel import Field, SQLModel, Column, JSON

class Judger(SQLModel, table=True):
    name: str = Field(primary_key=True)
    key: str | None = Field(default=None)
    blocked: bool = Field(default=False)
    
    description: str | None = Field(default=None)
    languages: list[str] | None = Field(default=None, sa_column=Column(JSON))
    start_time: datetime | None = None
    
    last_seen: datetime | None = Field(default_factory=datetime.now)
    last_ip: str | None = None
