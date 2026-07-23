import argparse
import sys

from sqlmodel import Session, select

from src.database import engine, init_db
from src.models import User

def set_superuser(username: str) -> bool:
    init_db()
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == username)).first()
        if user is None:
            return False
        user.superuser = True
        session.add(user)
        session.commit()
        return True


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="hwoj", description="HWOJ backend management commands")
    subparsers = parser.add_subparsers(dest="command", required=True)

    superuser_parser = subparsers.add_parser(
        "set-superuser",
        help="Grant superuser access to an existing username",
    )
    superuser_parser.add_argument("username", help="Existing username to promote")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "set-superuser":
        if set_superuser(args.username):
            print(f"User '{args.username}' is now a superuser.")
            return 0
        print(f"User '{args.username}' was not found.", file=sys.stderr)
        return 1

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
