from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from sqlmodel import Session
from pwdlib import PasswordHash
pwd = PasswordHash.recommended()

from .. import SessionDep, User

router = APIRouter(prefix="/verify", tags=["verify-bot"])

class UserCreate(BaseModel):
    discord_id: int
    username: str
    password: str

@router.post("/create")
def create(user:UserCreate, session: SessionDep):
    db_user = User(**user.model_dump())
    db_user.password = pwd.hash(db_user.password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user
