"""URL configuration for O Último Blog do Mundo."""

from django.http import HttpResponse
from django.urls import path


def healthcheck(request):
    """Minimal health check endpoint.

    In M1 returns a simple 200 OK. DB and cache checks will be added
    when those services are configured in later milestones.
    """
    return HttpResponse("ok", content_type="text/plain")


urlpatterns = [
    path("healthz", healthcheck, name="healthcheck"),
]
