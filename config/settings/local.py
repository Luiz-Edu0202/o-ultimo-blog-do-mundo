"""
Local development settings.

Uses SQLite by default, DEBUG=True, email to console.
"""

import sys

from .base import *
from .base import env

# ---------------------------------------------------------------------------
# Debug
# ---------------------------------------------------------------------------
DEBUG = True
ALLOWED_HOSTS = env.list(
    "ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1", "0.0.0.0", "testserver"],  # noqa: S104
)

# ---------------------------------------------------------------------------
# Secret key — only for local dev
# ---------------------------------------------------------------------------
SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-local-dev-key-do-not-use-in-production",
)

# ---------------------------------------------------------------------------
# Database — SQLite for local without Docker
# ---------------------------------------------------------------------------
if "pytest" in sys.modules or "test" in sys.argv:
    _test_db = env("TEST_DATABASE_URL", default="sqlite:///:memory:")
    DATABASES = {
        "default": env.db_url_config(_test_db),
    }
else:
    DATABASES = {
        "default": env.db(
            "DATABASE_URL",
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
        ),
    }

# ---------------------------------------------------------------------------
# Email — console backend
# ---------------------------------------------------------------------------
MAILERS = {
    "default": {
        "BACKEND": "django.core.mail.backends.console.EmailBackend",
    },
}

# ---------------------------------------------------------------------------
# Static / Media
# ---------------------------------------------------------------------------
# Use default filesystem storage in development
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
