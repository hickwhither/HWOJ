def include_router(app):
    from .judge import router as judge_router
    from .problem import router as problem_router
    app.include_router(judge_router)
    app.include_router(problem_router)