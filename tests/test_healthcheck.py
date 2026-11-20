"""Tests for the /healthz endpoint — validates DB and cache connectivity."""

import pytest
from django.core.cache import cache
from django.db import connection
from django.test import Client


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
class TestHealthcheckEndpoint:
    """Test suite for the /healthz health check endpoint."""

    def test_healthcheck_returns_200(self, client):
        """Healthcheck should return HTTP 200 when all systems are healthy."""
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_healthcheck_returns_json(self, client):
        """Healthcheck should return a JSON response."""
        response = client.get("/healthz")
        data = response.json()
        assert isinstance(data, dict)

    def test_healthcheck_status_ok(self, client):
        """Healthcheck payload should have status 'ok' in a healthy environment."""
        response = client.get("/healthz")
        data = response.json()
        assert data["status"] == "ok"

    def test_healthcheck_checks_key_present(self, client):
        """Healthcheck payload should include a 'checks' dictionary."""
        response = client.get("/healthz")
        data = response.json()
        assert "checks" in data
        assert isinstance(data["checks"], dict)

    def test_healthcheck_db_check_ok(self, client):
        """Healthcheck should report db as 'ok' when the database is reachable."""
        response = client.get("/healthz")
        data = response.json()
        assert data["checks"].get("db") == "ok"

    def test_healthcheck_cache_check_ok(self, client):
        """Healthcheck should report cache as 'ok' when cache is reachable."""
        response = client.get("/healthz")
        data = response.json()
        assert data["checks"].get("cache") == "ok"

    def test_healthcheck_db_failure_returns_503(self, client, monkeypatch):
        """Healthcheck should return 503 when the database is unavailable."""
        import django.db

        def broken_cursor():
            raise django.db.OperationalError("DB connection refused")

        monkeypatch.setattr(connection, "cursor", broken_cursor)
        response = client.get("/healthz")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert "db" in data["checks"]
        assert data["checks"]["db"].startswith("error:")

    def test_healthcheck_cache_failure_returns_503(self, client, monkeypatch):
        """Healthcheck should return 503 when the cache is unavailable."""

        def broken_set(key, value, timeout=None):
            raise Exception("Cache connection refused")

        monkeypatch.setattr(cache, "set", broken_set)
        response = client.get("/healthz")
        assert response.status_code == 503
        data = response.json()
        assert data["status"] == "error"
        assert "cache" in data["checks"]
        assert data["checks"]["cache"].startswith("error:")

    def test_healthcheck_no_authentication_required(self, client):
        """Healthcheck must be publicly accessible without authentication."""
        # No login — should still return 200
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_healthcheck_get_method_allowed(self, client):
        """Healthcheck should respond to GET requests."""
        response = client.get("/healthz")
        assert response.status_code in (200, 503)  # any valid health response


@pytest.mark.django_db
class TestConnectivityDirect:
    """Direct connectivity tests for DB and cache."""

    def test_database_connectivity(self):
        """Direct DB connectivity test — executes a trivial query."""
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        assert result == (1,)

    def test_cache_set_and_get(self):
        """Direct cache connectivity test — set/get a value."""
        cache.set("test_key", "test_value", timeout=5)
        assert cache.get("test_key") == "test_value"
        cache.delete("test_key")
