"""Root conftest for pytest."""

import django
import pytest
from django.conf import settings
from django.utils import translation


def pytest_configure():
    """Ensure Django settings are configured before tests run."""
    settings.DJANGO_SETTINGS_MODULE = "config.settings.local"
    django.setup()


@pytest.fixture(autouse=True)
def reset_language():
    """Reset active language to default pt-br before and after each test."""
    translation.activate("pt-br")
    yield
    translation.deactivate()
