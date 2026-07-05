def include_router(app):
    from .problem import router as problem_router
    app.include_router(problem_router)