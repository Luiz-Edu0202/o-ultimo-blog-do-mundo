"""URLs for core app."""

from django.urls import path

from apps.core.views import AboutView

app_name = "core"

urlpatterns = [
    path("sobre/", AboutView.as_view(), name="about"),
]
