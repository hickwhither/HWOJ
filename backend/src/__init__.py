import os, importlib, secrets
from contextlib import asynccontextmanager
from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv
load_dotenv()
from .database import *

def create_app():
    app = FastAPI(title=os.getenv('APP_NAME'), description=f"{os.getenv('APP_NAME')} backend")
    init_db()
    
    allow_origins = [os.getenv("ALLOWED_ORIGINS").split()] + ["localhost:5173", "127.0.0.1:5173"]
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
        secret_key=os.getenv("SECRET_KEY"),
        session_cookie="session",
        max_age=60 * 60 * 24 * 7, # 7 days
        same_site="none", # Cookie from other domains
        https_only=True,
    )

    from fastapi.responses import FileResponse
    @app.get('/favicon.ico', include_in_schema=False)
    async def favicon():
        return FileResponse("./sigma.jpg")

    from .routers.admin import router as admin_router
    from .routers.user import router as api_router
    from .routers.webhook import router as judger_router
    app.include_router(admin_router)
    app.include_router(api_router)
    app.include_router(judger_router)

    return app