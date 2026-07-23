from fastapi import HTTPException, Request
from sqlmodel import select
from datetime import datetime

from src.database import SessionDep
from src.models import User
from src.models import Contest, ContestRegistration


def get_contest_or_404(session: SessionDep, code: str) -> Contest:
    contest = session.exec(select(Contest).where(Contest.code == code)).one_or_none()
    if not contest:
        raise HTTPException(404, "contest.notfound")
    return contest


def ensure_contest_running(contest: Contest) -> None:
    now = datetime.now()
    if now < contest.start_time:
        raise HTTPException(403, "contest.upcoming")
    if now > contest.end_time:
        raise HTTPException(403, "contest.ended")


def ensure_registration_running(contest: Contest) -> None:
    now = datetime.now()
    if now < contest.registration_start:
        raise HTTPException(403, "contest.registration_upcoming")
    if now > contest.registration_end:
        raise HTTPException(403, "contest.registration_ended")


def is_contest_participant(session: SessionDep, contest: Contest, user: User) -> bool:
    return bool(session.get(ContestRegistration, (contest.id, user.id)))


def ensure_can_view_contest(contest: Contest, user: User, session: SessionDep) -> None:
    if is_contest_participant(session, contest, user):
        return
    raise HTTPException(403, "contest.not_registered")