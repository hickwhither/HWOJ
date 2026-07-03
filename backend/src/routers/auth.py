from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
pwd = PasswordHash.recommended()

from .. import SessionDep, User

router = APIRouter(prefix="/auth", tags=["frontend"])

class LoginForm(BaseModel):
    username: str
    password: str

@router.post("/signin")
def login(request: Request, form: LoginForm, session: SessionDep):
    user = session.get(User, form.username)
    if not user or not pwd.verify(form.password, user.password):
        raise HTTPException(400, detail="Incorrect username or password")

    request.session['auth'] = {"user": user.username}
    return {"detail": f"Logged in as {user.username}"}

@router.post('/logout')
def logout(request: Request):
    request.session.pop('auth', None)
    return {"detail": "success"}


@router.get("/profile")
def profile(request: Request, session: SessionDep):
    auth:dict = request.session.get('auth')
    if not auth:
        raise HTTPException(404, detail="User not found")
    user = session.get(User, auth.get('user'))
    if not user:
        raise HTTPException(404, detail="User not found")

    return {
        'id': user.username,
        'name': user.username,
        'nickname': getattr(user, 'nickname', ''),
        'avatar': '',
        'rating': 0
    }
    
    