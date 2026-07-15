APP_NAME = "EPenguinOJ"
ALLOWED_ORIGINS = ["*"]
PROBLEMS_DIR = "/tmp/problems"

SECRET_KEY="CHANGE THIS"
import os
JUGER_SECRET_KEY = open(os.path.join(PROBLEMS_DIR, "key"), "r").read()

try:
    from .local_settings import *
except ImportError:
    pass
