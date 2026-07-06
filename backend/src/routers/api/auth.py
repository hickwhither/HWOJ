from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
pwd = PasswordHash.recommended()

router = APIRouter(prefix="/auth", tags=["auth"])

# -- MODELS --
from src import SessionDep
from src import User, UserCreate, UserPublic, UserView
from sqlmodel import select, func
class PasswordForm(BaseModel):
    username: str
    password: str

# -- ROUTERS --
@router.post("/signup")
@router.post("/register")
def create_account(request: Request, new_user: UserCreate, session: SessionDep):
    if session.get(User, new_user.username):
        raise HTTPException(400, "User exists.")
    if session.exec(select(User).where(User.email == new_user.email)).first():
        raise HTTPException(400, "Email exists.")

"""
login và logout sau này sẽ thay thế bằng auth key
"""

@router.post("/signin")
@router.post("/login")
def login(request: Request, PasswordForm: PasswordForm, session: SessionDep):
    user = session.get(User, PasswordForm.username)
    if not user or not pwd.verify(PasswordForm.password, user.password):
        raise HTTPException(400, detail="Incorrect username or password")

    request.session['auth'] = {"username": user.username}
    return {"detail": f"Logged in as {user.username}"}

@router.post('/logout')
def logout(request: Request):
    request.session.pop('auth', None)
    return {"detail": "success"}


@router.get("/profile", response_model=UserView)
@router.get("/profile/{username}", response_model=UserView)
def profile(request: Request, username:str, session: SessionDep):
    if not username:
        auth:dict = request.session.get('auth')
        if not auth:
            raise HTTPException(404, detail="User not found")
        username = auth.get('username')
    user = session.get(User, username)
    if not user:
        raise HTTPException(404, detail="User not found")
    return user
