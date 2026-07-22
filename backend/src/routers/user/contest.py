from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import func, select

from src.database import SessionDep
from src.models.contest import Contest
from src.models.links import ContestParticipantLink
from src.models.user import User
from src.models_public import ContestPublic, ContestView
from .dependencies import verify_auth

router = APIRouter(prefix="/contest", tags=["contest"], dependencies=[Depends(verify_auth)])


class ContestPageResponse(BaseModel):
    contests: list[ContestPublic]
    total: int
    total_pages: int


class ContestRegisterRequest(BaseModel):
    password: Optional[str] = None


def get_contest_or_404(session: SessionDep, code: str) -> Contest:
    contest = session.exec(select(Contest).where(Contest.code == code)).one_or_none()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return contest


def is_contest_participant(session: SessionDep, contest: Contest, user: User) -> bool:
    return bool(session.get(ContestParticipantLink, (contest.id, user.username)))


def ensure_can_view_contest(contest: Contest, user: User, session: SessionDep) -> None:
    if contest.is_public or is_contest_participant(session, contest, user):
        return
    raise HTTPException(status_code=403, detail="You are not registered for this contest")


@router.get("", response_model=ContestPageResponse)
def get_contest_list(
    session: SessionDep,
    current_user: User = Depends(verify_auth),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    code: Optional[str] = Query(None),
    title: Optional[str] = Query(None),
):
    query = select(Contest)
    if code:
        query = query.where(Contest.code.icontains(code))
    if title:
        query = query.where(Contest.title.icontains(title))
    if not current_user.superuser:
        query = query.where(Contest.is_public == True)

    total = session.exec(select(func.count()).select_from(query.subquery())).one()
    total_pages = max(1, (total + limit - 1) // limit)
    contests = session.exec(
        query.order_by(Contest.start_time.desc()).offset((page - 1) * limit).limit(limit)
    ).all()
    return {"contests": contests, "total": total, "total_pages": total_pages}


@router.get("/{code}", response_model=ContestView)
def get_contest(session: SessionDep, code: str, current_user: User = Depends(verify_auth)):
    contest = get_contest_or_404(session, code)
    ensure_can_view_contest(contest, current_user, session)
    return contest


@router.post("/{code}/register")
def register_contest(
    session: SessionDep,
    code: str,
    payload: ContestRegisterRequest,
    current_user: User = Depends(verify_auth),
):
    contest = get_contest_or_404(session, code)
    now = datetime.now()
    if contest.registration_start and now < contest.registration_start:
        raise HTTPException(status_code=403, detail="Registration has not started")
    if contest.registration_end and now > contest.registration_end:
        raise HTTPException(status_code=403, detail="Registration has ended")
    if contest.password and payload.password != contest.password:
        raise HTTPException(status_code=403, detail="Incorrect contest password")
    if not is_contest_participant(session, contest, current_user):
        session.add(ContestParticipantLink(contest_id=contest.id, user_username=current_user.username))
        session.commit()
    return {"message": "Registered successfully"}
