"""
Tests for production settings validation.

Validates that config/settings/production.py defines the expected
security-critical settings by loading it in an isolated subprocess,
avoiding side-effects on the running Django process and avoiding
unnecessary database driver initialization.
"""

import json
import subprocess
import sys

import pytest


def _production_env():
    """Return a minimal set of env vars required by production.py."""
    return {
        "SECRET_KEY": "test-secret-key-for-ci-only",
        "DEBUG": "False",
        "ALLOWED_HOSTS": "example.com,www.example.com",
        "DATABASE_URL": "postgres://user:pass@localhost:5432/blog",
        "REDIS_URL": "redis://localhost:6379/0",
        "SUPABASE_S3_ENDPOINT": "https://test.supabase.co/storage/v1/s3",
        "SUPABASE_S3_ACCESS_KEY": "test-access-key",
        "SUPABASE_S3_SECRET_KEY": "test-secret-key",
        "SUPABASE_STORAGE_BUCKET": "media",
        "ADMIN_PATH": "gestao",
        "SITE_NAME": "Test Blog",
    }


@pytest.fixture(scope="module")
def prod_settings():
    """Load production settings in a subprocess and return parsed dict."""
    env = _production_env()
    script = f"""
import json, os, runpy
os.environ.update({json.dumps(env)})
mod = runpy.run_module("config.settings.production", run_name="config.settings.production")
db_opts = mod["DATABASES"]["default"]
data = {{
    "DEBUG": mod["DEBUG"],
    "SECRET_KEY": mod["SECRET_KEY"],
    "ALLOWED_HOSTS": mod["ALLOWED_HOSTS"],
    "SECURE_SSL_REDIRECT": mod["SECURE_SSL_REDIRECT"],
    "SECURE_HSTS_SECONDS": mod["SECURE_HSTS_SECONDS"],
    "SESSION_COOKIE_SECURE": mod["SESSION_COOKIE_SECURE"],
    "CSRF_COOKIE_SECURE": mod["CSRF_COOKIE_SECURE"],
    "CSRF_TRUSTED_ORIGINS": mod["CSRF_TRUSTED_ORIGINS"],
    "PASSWORD_HASHERS": mod["PASSWORD_HASHERS"],
    "DB_ENGINE": db_opts["ENGINE"],
    "DISABLE_SERVER_SIDE_CURSORS": db_opts.get("DISABLE_SERVER_SIDE_CURSORS", False),
    "CONN_MAX_AGE": db_opts.get("CONN_MAX_AGE", 0),
    "CACHE_BACKEND": mod["CACHES"]["default"]["BACKEND"],
    "SESSION_ENGINE": mod["SESSION_ENGINE"],
    "MIDDLEWARE": mod["MIDDLEWARE"],
    "STORAGES": mod["STORAGES"],
}}
print(json.dumps(data))
"""
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent),
    )
    if result.returncode != 0:
        pytest.fail(f"Failed to load production settings:\n{result.stderr}")
    return json.loads(result.stdout)


class TestProductionSettings:
    """Verify critical production configuration."""

    def test_debug_is_false(self, prod_settings):
        assert prod_settings["DEBUG"] is False

    def test_secret_key_is_set(self, prod_settings):
        assert prod_settings["SECRET_KEY"]
        assert prod_settings["SECRET_KEY"] != ""

    def test_allowed_hosts_not_empty(self, prod_settings):
        assert len(prod_settings["ALLOWED_HOSTS"]) > 0

    def test_ssl_redirect_enabled(self, prod_settings):
        assert prod_settings["SECURE_SSL_REDIRECT"] is True

    def test_hsts_enabled(self, prod_settings):
        assert prod_settings["SECURE_HSTS_SECONDS"] >= 31536000

    def test_secure_cookies(self, prod_settings):
        assert prod_settings["SESSION_COOKIE_SECURE"] is True
        assert prod_settings["CSRF_COOKIE_SECURE"] is True

    def test_csrf_trusted_origins_includes_https(self, prod_settings):
        origins = prod_settings["CSRF_TRUSTED_ORIGINS"]
        assert "https://example.com" in origins

    def test_argon2_is_primary_hasher(self, prod_settings):
        assert "Argon2" in prod_settings["PASSWORD_HASHERS"][0]

    def test_database_has_postgresql(self, prod_settings):
        engine = prod_settings["DB_ENGINE"]
        assert "postgresql" in engine or "postgres" in engine

    def test_database_disables_server_side_cursors(self, prod_settings):
        assert prod_settings["DISABLE_SERVER_SIDE_CURSORS"] is True

    def test_database_conn_max_age_set(self, prod_settings):
        assert prod_settings["CONN_MAX_AGE"] > 0

    def test_cache_uses_redis(self, prod_settings):
        assert "Redis" in prod_settings["CACHE_BACKEND"]

    def test_session_engine_is_cache(self, prod_settings):
        assert prod_settings["SESSION_ENGINE"] == "django.contrib.sessions.backends.cache"

    def test_whitenoise_in_middleware(self, prod_settings):
        assert any("whitenoise" in m.lower() for m in prod_settings["MIDDLEWARE"])

    def test_static_storage_is_whitenoise(self, prod_settings):
        static_backend = prod_settings["STORAGES"]["staticfiles"]["BACKEND"]
        assert "whitenoise" in static_backend.lower()

    def test_default_storage_is_s3(self, prod_settings):
        default_backend = prod_settings["STORAGES"]["default"]["BACKEND"]
        assert "S3Boto3Storage" in default_backend


class TestProductionMissingVars:
    """Ensure production settings fail loudly when required vars are missing."""

    def _load_production_without(self, missing_key):
        """Try loading production settings without a required env var in a clean environment."""
        env = _production_env()
        del env[missing_key]
        script = f"""
import json, os, runpy
from unittest.mock import patch
os.environ.clear()
os.environ.update({json.dumps(env)})
with patch("pathlib.Path.is_file", return_value=False):
    runpy.run_module("config.settings.production", run_name="config.settings.production")
"""
        result = subprocess.run(  # noqa: S603
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            cwd=str(__import__("pathlib").Path(__file__).resolve().parent.parent),
        )
        return result

    def test_missing_secret_key_raises(self):
        result = self._load_production_without("SECRET_KEY")
        assert result.returncode != 0, "Expected failure when SECRET_KEY is missing"

    def test_missing_database_url_raises(self):
        result = self._load_production_without("DATABASE_URL")
        assert result.returncode != 0, "Expected failure when DATABASE_URL is missing"

    def test_missing_redis_url_raises(self):
        result = self._load_production_without("REDIS_URL")
        assert result.returncode != 0, "Expected failure when REDIS_URL is missing"
