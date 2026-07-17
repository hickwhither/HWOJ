import os, jwt
from datetime import *
from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel, EmailStr

from pwdlib import PasswordHash
pwd = PasswordHash.recommended()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# -- MODELS --
from src import SessionDep, User
from src.database_public import UserPublic, UserView
from sqlmodel import select, func

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class VerifyCreateRequest(BaseModel):   
    discord_id: int

# -- ROUTERS --
router = APIRouter(
    prefix="/discord", 
    tags=["discord"],
)

@router.get("/user")
def is_user_exists(session: SessionDep, discord_id:int):
    user = session.exec(select(User).where(User.discord_id == discord_id)).first()
    print(user)
    return True if user else False

@router.post("/create")
def create_verify(data: VerifyCreateRequest):
    expire = datetime.now(timezone.utc) + timedelta(minutes=5)
    payload = {
        "discord_id": data.discord_id,
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

