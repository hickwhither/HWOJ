import os
import jwt
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from sqlmodel import select

from src.database import SessionDep
from src.models.user import User, create_auth, delete_auth, verify_auth, get_user_by_username
from src.models_public import UserView

# CONFIGURATIONS
pwd = PasswordHash.recommended()
router = APIRouter(prefix="/auth", tags=["user.auth"])


# SCHEMAS
# class CreateAccount(BaseConfirmRequest):
#     username: str
#     email: EmailStr
#     password: str


class PasswordForm(BaseModel):
    username: str
    password: str


# ROUTERS
# @router.post("/signup", response_model=UserView)
# def signup(request: Request, new_user: CreateAccount, session: SessionDep):
#     if session.get(User, new_user.username):
#         raise HTTPException(400, "User exists.")
#     if session.exec(select(User).where(User.email == new_user.email)).first():
#         raise HTTPException(400, "Email exists.")
#     user_data = new_user.model_dump()
#     user = User.model_validate(user_data)
#     session.add(user)
#     session.commit()
#     session.refresh(user)
#     request.session['auth'] = {"username": user.username}
#     return user


@router.post("/signin", response_model=UserView)
def signin(request: Request, session: SessionDep, payload: PasswordForm):
    user = get_user_by_username(session, payload.username)
    if not user or not pwd.verify(payload.password, user.password):
        raise HTTPException(400, "Incorrect username or password")
    create_auth(request, user)
    return user

@router.post('/signout')
def signout(request: Request):
    delete_auth(request)
    return

@router.get("/profile", response_model=UserView)
@router.get("/profile/{username}", response_model=UserView)
def profile(request: Request, session: SessionDep, username:str|None=None):
    if not username:
        return verify_auth(request, session)
    return session.get(User, username)

