APP_NAME = "HWOJ"
ALLOWED_ORIGINS = ["*"]
PROBLEMS_DIR = "/tmp/problems"

SECRET_KEY="CHANGE THIS"

try:
    from .local_settings import *
except ImportError:
    pass

import os
JUGER_SECRET_KEY = open(os.path.join(PROBLEMS_DIR, "key"), "r").read()