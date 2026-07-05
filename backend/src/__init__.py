import os, importlib, secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from .settings import APP_NAME, ALLOWED_ORIGINS
from dotenv import load_dotenv
load_dotenv()

from database import init_db

def create_app():
    app = FastAPI(title=APP_NAME, description=f"{APP_NAME} backend")
    init_db()
    
    allow_origins = ALLOWED_ORIGINS or ["localhost", "127.0.0.1"]
    print("ALLOWED ORIGINS", allow_origins)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        SessionMiddleware,
        secret_key=secrets.token_hex(32),
        session_cookie="session",
        max_age=60 * 60 * 24 * 7, # 7 days
    )

    from fastapi.responses import FileResponse
    @app.get('/favicon.ico', include_in_schema=False)
    async def favicon():
        return FileResponse("./sigma.jpg")

    from .routers.auth import router as auth_router
    from .routers.api import router as api_router
    from .routers.judge import router as judge_router
    app.include_router(auth_router)
    app.include_router(api_router)
    app.include_router(judge_router)

    return app