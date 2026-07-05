from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
pwd = PasswordHash.recommended()

router = APIRouter(prefix="/admin/auth", tags=["user", "auth"])

# -- MODELS --
from database import SessionDep, User, UserProfile
class PasswordForm(BaseModel):
    username: str
    password: str

# -- ROUTERS --
@router.post("/signin")
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


@router.get("/profile", response_model=UserProfile)
@router.get("/profile/{username}", response_model=UserProfile)
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
