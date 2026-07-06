from datetime import datetime
from sqlmodel import Field, SQLModel, Column, JSON
import secrets, string

def random_key():
    return ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*(-_=+)") for _ in range(256))

class Judger(SQLModel, table=True):
    # Cell 1
    id: int = Field(primary_key=True)
    key: str = Field(default_factory=random_key) # click top copy
    blocked: bool = Field(default=False)
    
    # Cell 2
    name: str | None = Field(default=None)
    languages: list[str] | None = Field(default=None, sa_column=Column(JSON))
    description: str | None = Field(default=None)

    # Cell 3
    start_time: datetime | None = Field(default=None) # Uptime seconds
    last_seen: datetime | None = Field(default=None)
    last_ip: str | None = Field(default=None)
