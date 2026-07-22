from fastapi import HTTPException, Request
from sqlmodel import select

from src.database import SessionDep
from src.models.user import User


def verify_auth(request: Request, session: SessionDep) -> User:
    auth_data = request.session.get("auth")
    if not auth_data or "username" not in auth_data:
        raise HTTPException(status_code=401, detail="Not authenticated")

    username = auth_data["username"]
    user = session.exec(select(User).where(User.username == username)).one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
