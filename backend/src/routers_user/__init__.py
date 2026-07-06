def include_router(app):
    from .auth import router as auth_router
    from .problem import router as problem_router
    app.include_router(auth_router)
    app.include_router(problem_router)