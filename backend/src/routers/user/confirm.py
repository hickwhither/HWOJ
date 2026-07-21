import os
import jwt
from fastapi import APIRouter, Request, HTTPException, status
from pydantic import BaseModel, EmailStr
from pwdlib import PasswordHash
from sqlmodel import select

from src.database import SessionDep
from src.models.user import User

# CONFIGURATION
pwd = PasswordHash.recommended()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

router = APIRouter(prefix="/confirm", tags=["confirm"])


# SCHEMAS
class BaseConfirmRequest(BaseModel):
    secret: str


class ConfirmCreateAccountRequest(BaseConfirmRequest):
    username: str
    email: EmailStr
    password: str


class ConfirmChangePasswordRequest(BaseConfirmRequest):
    password: str


class PasswordForm(BaseModel):
    username: str
    password: str


# FUNCTIONS
def decode_discord_token(secret: str) -> str:
    """Decodes the JWT token and extracts the discord_id."""
    try:
        payload = jwt.decode(secret, SECRET_KEY, algorithms=[ALGORITHM])
        discord_id = payload.get("discord_id")
        if not discord_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token payload is missing discord_id"
            )
        return discord_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ROUTERS
@router.post("/check")
def check_token(data: BaseConfirmRequest):
    """Validates the secret token."""
    decode_discord_token(data.secret)
    return {"message": "Token is valid"}


@router.post("/create-account", status_code=status.HTTP_201_CREATED)
def confirm_create_account(
    request: Request,
    data: ConfirmCreateAccountRequest,
    session: SessionDep
):
    """Creates a new user account linked with a Discord ID."""
    discord_id = decode_discord_token(data.secret)

    # Check for existing records
    if session.get(User, data.username):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Username already exists")
    if session.exec(select(User).where(User.email == data.email)).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email is already in use")
    if session.exec(select(User).where(User.discord_id == discord_id)).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Discord ID is already registered")

    new_user = User(
        username=data.username,
        email=data.email,
        password=pwd.hash(data.password),
        discord_id=discord_id
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    request.session["auth"] = {"username": new_user.username}
    return {"message": "Account created successfully", "username": new_user.username}


@router.post("/reset-password")
def confirm_reset_password(
    request: Request,
    data: ConfirmChangePasswordRequest,
    session: SessionDep
):
    """Resets the password for an existing account linked to the verified Discord ID."""
    discord_id = decode_discord_token(data.secret)

    user = session.exec(select(User).where(User.discord_id == discord_id)).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No account associated with this Discord ID")

    user.password = pwd.hash(data.password)
    session.add(user)
    session.commit()

    request.session["auth"] = {"username": user.username}
    return {"message": "Password updated successfully"}


@router.post("/quick-login")
def confirm_quick_login(
    request: Request,
    data: BaseConfirmRequest,
    session: SessionDep
):
    """Logs in the user directly using a valid Discord confirmation token."""
    discord_id = decode_discord_token(data.secret)

    user = session.exec(select(User).where(User.discord_id == discord_id)).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No account associated with this Discord ID")

    request.session["auth"] = {"username": user.username}
    return {"message": "Login successful", "username": user.username}

