SERVER_URL = "http://127.0.0.1:8000"
POLL_INTERVAL = 3
BOX_ID = 0
USE_CGROUPS = True
COMPILE_TIME_LIMIT = 20

try:
    from .local_settings import *
except ImportError:
    pass
