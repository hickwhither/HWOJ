from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel, EmailStr

import os, jwt
from pwdlib import PasswordHash
pwd = PasswordHash.recommended()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter(prefix="/auth", tags=["auth"])

# -- MODELS --
from src import SessionDep, User
from src.database_public import UserPublic, UserView
from sqlmodel import select, func

# class UserCreate(BaseModel):
#     username: str
#     email: EmailStr
#     password: str
class ConfirmActionRequest(BaseModel):
    secret: str
    action: str
    username: str | None = None
    email: EmailStr | None = None
    password: str | None = None

class PasswordForm(BaseModel):
    username: str
    password: str

# -- ROUTERS --
# @router.post("/signup", response_model=UserView) # Commented for "confirm-action" (read below)
# def signup(request: Request, new_user: UserCreate, session: SessionDep):
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

@router.post("/confirm-action")
def confirm_action(request: Request, data: ConfirmActionRequest, session: SessionDep):
    try:
        payload = jwt.decode(data.secret, SECRET_KEY, algorithms=[ALGORITHM])
        discord_id = payload.get("discord_id")
    except jwt.ExpiredSignatureError:
        raise HTTPException(408, "Expired token")
    except jwt.InvalidTokenError:
        raise HTTPException(408, "Invalid Token")

    if data.action == "check": return
    elif data.action == "create_account":
        if not data.username or not data.email:
            raise HTTPException(400, "Username và Email là bắt buộc để tạo tài khoản.")
            
        if session.get(User, data.username):
            raise HTTPException(400, "Tên đăng nhập đã tồn tại.")
        if session.exec(select(User).where(User.email == data.email)).first():
            raise HTTPException(400, "Email đã được sử dụng.")
        if session.exec(select(User).where(User.discord_id == discord_id)).first():
            raise HTTPException(400, "Discord ID exists.")
        
        new_user = User(
            username=data.username,
            email=data.email,
            password=pwd.hash(data.password)
        )
        new_user.discord_id = discord_id
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        request.session['auth'] = {"username": new_user.username}
        return
    elif data.action in ["change_password", "forgot_password"]:
        user = session.exec(select(User).where(User.discord_id == discord_id)).first()
        if not user:
            raise HTTPException(404, "No user with matching Discord ID.")
        user.password = pwd.hash(data.password)
        session.add(user)
        session.commit()
        request.session['auth'] = {"username": user.username}
        return
    elif data.action == "quick_login":
        request.session['auth'] = {"username": user.username}
        return

    else:
        raise HTTPException(400, "Hành động không hợp lệ.")

@router.post("/signin", response_model=UserView)
def signin(request: Request, PasswordForm: PasswordForm, session: SessionDep):
    user = session.get(User, PasswordForm.username)
    if not user or not pwd.verify(PasswordForm.password, user.password):
        raise HTTPException(400, "Incorrect username or password")

    request.session['auth'] = {"username": user.username}
    return user

@router.post('/signout')
def signout(request: Request):
    request.session.pop('auth', None)
    return


@router.get("/profile", response_model=UserView)
@router.get("/profile/{username}", response_model=UserView)
def profile(request: Request, session: SessionDep, username:str|None=None):
    if not username:
        auth:dict = request.session.get('auth')
        if not auth:
            raise HTTPException(404, "User not found")
        username = auth.get('username')
    user = session.get(User, username)
    if not user:
        raise HTTPException(404, "User not found")
    return user

