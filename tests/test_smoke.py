"""Smoke tests for project setup and configuration."""

import json

import pytest
from django.test import RequestFactory

from config.urls import healthcheck


class TestSystemCheck:
    """Verify that Django system checks pass."""

    def test_django_check(self):
        """Django system check framework should report no errors."""
        from django.core.management import call_command

        call_command("check", "--fail-level", "ERROR")

    def test_settings_module_loads(self):
        """Local settings should load without errors."""
        from django.conf import settings

        # Note: pytest-django sets DEBUG=False during tests (expected behavior)
        assert "apps.core" in settings.INSTALLED_APPS
        assert "apps.blog" in settings.INSTALLED_APPS
        assert "apps.dashboard" in settings.INSTALLED_APPS
        assert "apps.accounts" in settings.INSTALLED_APPS
        assert settings.LANGUAGE_CODE == "pt-br"
        assert settings.USE_I18N is True

    def test_admin_not_in_urls(self):
        """Django admin must NOT be exposed (SPEC requirement)."""
        from django.urls import NoReverseMatch, reverse

        try:
            reverse("admin:index")
        except NoReverseMatch:
            pass  # Expected — admin is not registered
        else:
            msg = "Django admin URL should not be registered"
            raise AssertionError(msg)


@pytest.mark.django_db
class TestHealthcheck:
    """Verify the /healthz endpoint."""

    def test_healthcheck_returns_200(self):
        """GET /healthz should return 200 with JSON body containing status ok."""
        factory = RequestFactory()
        request = factory.get("/healthz")
        response = healthcheck(request)
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "ok"
        assert "checks" in data
        assert response["Content-Type"] == "application/json"
