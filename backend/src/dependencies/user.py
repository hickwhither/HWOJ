from fastapi import HTTPException, Request
from sqlmodel import select

from src.database import SessionDep
from src.models import User

def create_auth(request: Request, user: User): request.session['id'] = user.id

def delete_auth(request: Request): request.session.pop('auth', None)


def verify_auth(request: Request, session: SessionDep) -> User:
    id = request.session.get("id")
    if not id:
        raise HTTPException(401, "user.not_authenticated")
    user = session.get(User, id)
    return user


def get_user_or_404(session: SessionDep, username: str) -> User | None:
    statement = select(User).where(User.username == username)
    results = session.exec(statement)
    user = results.one_or_none()
    if not user:
        raise HTTPException(404, "user.notfound")
    return user


def verify_permissions(request: Request, session: SessionDep) -> User:
    user = verify_auth(request, session)
