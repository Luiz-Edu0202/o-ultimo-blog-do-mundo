"""Authentication and 2FA views for the admin dashboard."""

import base64
import io

import qrcode
import qrcode.image.svg
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import update_session_auth_hash
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import FormView
from django_otp import login as otp_login
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.dashboard.decorators import DashboardAuthMixin, is_dashboard_verified
from apps.dashboard.forms import (
    DashboardLoginForm,
    DashboardPasswordChangeForm,
    TwoFactorVerifyForm,
)


class DashboardLoginView(FormView):
    """Staff login view with brute-force protection via django-axes."""

    template_name = "dashboard/login.html"
    form_class = DashboardLoginForm

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if is_dashboard_verified(request):
            return redirect("dashboard:index")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["request"] = self.request
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next_url"] = self.request.GET.get("next") or self.request.POST.get("next") or ""
        return context

    def form_valid(self, form: DashboardLoginForm) -> HttpResponse:
        user = form.get_user()
        if not user.is_staff:
            messages.error(
                self.request,
                "Acesso não autorizado. Apenas administradores podem acessar esta área.",
            )
            return self.form_invalid(form)

        auth_login(self.request, user)

        # Check if user has an existing confirmed 2FA device
        has_2fa = TOTPDevice.objects.filter(user=user, confirmed=True).exists()
        next_url = self.request.GET.get("next") or self.request.POST.get("next")

        if has_2fa:
            redirect_url = reverse("dashboard:2fa_verify")
            if next_url:
                redirect_url = f"{redirect_url}?next={next_url}"
            return redirect(redirect_url)

        # Force initial 2FA setup
        return redirect("dashboard:2fa_setup")


class Dashboard2FASetupView(View):
    """View to set up 2FA TOTP device with QR code and manual key."""

    template_name = "dashboard/2fa_setup.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("dashboard:login")
        # If user already verified 2FA, prevent re-setup unless requested
        if is_dashboard_verified(request) and not request.GET.get("reconfigure"):
            return redirect("dashboard:index")
        return super().dispatch(request, *args, **kwargs)

    def _get_or_create_unconfirmed_device(self, user) -> TOTPDevice:
        device = TOTPDevice.objects.filter(user=user, confirmed=False).first()
        if not device:
            device = TOTPDevice.objects.create(
                user=user,
                name="default",
                confirmed=False,
            )
        return device

    def _generate_qr_svg(self, config_url: str) -> str:
        qr = qrcode.QRCode(box_size=6, border=2)
        qr.add_data(config_url)
        qr.make(fit=True)
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        stream = io.BytesIO()
        img.save(stream)
        return stream.getvalue().decode("utf-8")

    def get(self, request: HttpRequest) -> HttpResponse:
        device = self._get_or_create_unconfirmed_device(request.user)
        qr_svg = self._generate_qr_svg(device.config_url)
        manual_key = base64.b32encode(device.bin_key).decode("utf-8")
        form = TwoFactorVerifyForm()

        return render(
            request,
            self.template_name,
            {
                "qr_svg": qr_svg,
                "manual_key": manual_key,
                "form": form,
            },
        )

    def post(self, request: HttpRequest) -> HttpResponse:
        device = self._get_or_create_unconfirmed_device(request.user)
        form = TwoFactorVerifyForm(request.POST)

        if form.is_valid():
            token = form.cleaned_data["token"]
            if device.verify_token(token):
                # Clean up any other devices and confirm this one
                TOTPDevice.objects.filter(user=request.user).exclude(pk=device.pk).delete()
                device.confirmed = True
                device.save()
                otp_login(request, device)
                messages.success(
                    request,
                    "Autenticação em dois fatores (2FA) ativada com sucesso!",
                )
                return redirect("dashboard:index")
            form.add_error("token", "Código inválido. Verifique o relógio do seu dispositivo.")

        qr_svg = self._generate_qr_svg(device.config_url)
        manual_key = base64.b32encode(device.bin_key).decode("utf-8")
        return render(
            request,
            self.template_name,
            {
                "qr_svg": qr_svg,
                "manual_key": manual_key,
                "form": form,
            },
        )


class Dashboard2FAVerifyView(View):
    """View to verify TOTP token on subsequent logins."""

    template_name = "dashboard/2fa_verify.html"

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.user.is_authenticated or not request.user.is_staff:
            return redirect("dashboard:login")
        if is_dashboard_verified(request):
            return redirect("dashboard:index")
        return super().dispatch(request, *args, **kwargs)

    def get(self, request: HttpRequest) -> HttpResponse:
        has_device = TOTPDevice.objects.filter(user=request.user, confirmed=True).exists()
        if not has_device:
            return redirect("dashboard:2fa_setup")
        form = TwoFactorVerifyForm()
        next_url = request.GET.get("next") or request.POST.get("next") or ""
        return render(request, self.template_name, {"form": form, "next_url": next_url})

    def post(self, request: HttpRequest) -> HttpResponse:
        device = TOTPDevice.objects.filter(user=request.user, confirmed=True).first()
        if not device:
            return redirect("dashboard:2fa_setup")

        form = TwoFactorVerifyForm(request.POST)
        next_url = request.GET.get("next") or request.POST.get("next") or ""
        if form.is_valid():
            token = form.cleaned_data["token"]
            if device.verify_token(token):
                otp_login(request, device)
                redirect_url = next_url or reverse("dashboard:index")
                return redirect(redirect_url)
            form.add_error("token", "Código de verificação inválido ou expirado.")

        return render(request, self.template_name, {"form": form, "next_url": next_url})


class DashboardLogoutView(View):
    """Log out from dashboard and redirect to login."""

    def post(self, request: HttpRequest) -> HttpResponse:
        auth_logout(request)
        messages.info(request, "Sessão encerrada com sucesso.")
        return redirect("dashboard:login")

    def get(self, request: HttpRequest) -> HttpResponse:
        return self.post(request)


class DashboardPasswordChangeView(DashboardAuthMixin, FormView):
    """Change password for the logged-in admin user."""

    template_name = "dashboard/password_change.html"
    form_class = DashboardPasswordChangeForm
    success_url = reverse_lazy("dashboard:password_change")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form: DashboardPasswordChangeForm) -> HttpResponse:
        form.save()
        update_session_auth_hash(self.request, form.user)
        messages.success(self.request, "Sua senha foi alterada com sucesso!")
        return super().form_valid(form)
