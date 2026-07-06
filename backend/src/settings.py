APP_NAME = "TBCOJ"
ALLOWED_ORIGINS = ["*"]

PROBLEMS_DIR = "/tmp/problems"

try:
    from .local_settings import *
except ImportError:
    pass
