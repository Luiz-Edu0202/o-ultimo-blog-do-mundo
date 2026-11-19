"""Decorators and mixins for dashboard authorization and 2FA verification."""

from collections.abc import Callable
from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django_otp.plugins.otp_totp.models import TOTPDevice


def is_dashboard_verified(request: HttpRequest) -> bool:
    """Check if the user is authenticated, has staff status, and is 2FA verified."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return False
    # Check if request.user is verified via OTPMiddleware
    is_verified_fn = getattr(request.user, "is_verified", None)
    if callable(is_verified_fn):
        return is_verified_fn()
    return False


def get_dashboard_redirect(request: HttpRequest) -> HttpResponse:
    """Determine the appropriate redirect for an unverified or unauthenticated user."""
    if not request.user.is_authenticated or not request.user.is_staff:
        login_url = reverse("dashboard:login")
        if request.path:
            return redirect(f"{login_url}?next={request.path}")
        return redirect(login_url)

    # User is logged in and staff, but not 2FA verified
    has_confirmed_device = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
    if has_confirmed_device:
        verify_url = reverse("dashboard:2fa_verify")
        if request.path and request.path not in [verify_url, reverse("dashboard:2fa_setup")]:
            return redirect(f"{verify_url}?next={request.path}")
        return redirect(verify_url)

    # No confirmed device -> must setup 2FA
    return redirect("dashboard:2fa_setup")


def dashboard_auth_required(view_func: Callable) -> Callable:
    """View decorator enforcing staff login and verified 2FA session."""

    @wraps(view_func)
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if not is_dashboard_verified(request):
            return get_dashboard_redirect(request)
        return view_func(request, *args, **kwargs)

    return _wrapped_view


class DashboardAuthMixin(AccessMixin):
    """Mixin for class-based views enforcing staff login and verified 2FA session."""

    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not is_dashboard_verified(request):
            return get_dashboard_redirect(request)
        return super().dispatch(request, *args, **kwargs)
