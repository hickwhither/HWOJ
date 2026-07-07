SECRET_KEY="CHANGE THIS"
APP_NAME = "EPenguinOJ"
ALLOWED_ORIGINS = ["*"]

PROBLEMS_DIR = "/tmp/problems"

try:
    from .local_settings import *
except ImportError:
    pass
