"""Tests for dashboard views, authentication, 2FA TOTP, Axes rate limiting, and CRUD."""

import pytest
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from django_otp.oath import TOTP
from django_otp.plugins.otp_totp.models import TOTPDevice

from apps.blog.models import MediaAsset, Post, Tag
from apps.core.models import SiteConfig

User = get_user_model()


@pytest.fixture
def admin_user():
    """Create a staff/admin user."""
    return User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="ValidPassword123!",
        is_staff=True,
    )


@pytest.fixture
def normal_user():
    """Create a regular non-staff user."""
    return User.objects.create_user(
        username="normaluser",
        email="user@example.com",
        password="NormalPassword123!",
        is_staff=False,
    )


@pytest.fixture
def confirmed_totp_device(admin_user):
    """Create a confirmed TOTP device for the admin user."""
    return TOTPDevice.objects.create(
        user=admin_user,
        name="default",
        confirmed=True,
    )


@pytest.fixture
def auth_verified_client(client, admin_user, confirmed_totp_device):
    """Client with authenticated staff user and verified 2FA session."""
    client.force_login(admin_user)
    # Simulate OTP verification in session
    session = client.session
    session["otp_device_id"] = confirmed_totp_device.persistent_id
    session.save()
    return client


@pytest.mark.django_db
class TestDashboardAccessControl:
    """Tests for authentication and 2FA protection on dashboard routes."""

    def test_anonymous_redirected_to_login(self, client):
        """Unauthenticated user is redirected to the login page."""
        response = client.get(reverse("dashboard:index"))
        assert response.status_code == 302
        assert reverse("dashboard:login") in response.url

    def test_unverified_staff_redirected_to_2fa_setup_when_no_device(self, client, admin_user):
        """Logged in staff without 2FA device is redirected to setup."""
        client.force_login(admin_user)
        response = client.get(reverse("dashboard:index"))
        assert response.status_code == 302
        assert reverse("dashboard:2fa_setup") in response.url

    def test_unverified_staff_redirected_to_2fa_verify_when_device_exists(
        self, client, admin_user, confirmed_totp_device
    ):
        """Logged in staff with unverified 2FA session is redirected to verify."""
        client.force_login(admin_user)
        response = client.get(reverse("dashboard:index"))
        assert response.status_code == 302
        assert reverse("dashboard:2fa_verify") in response.url

    def test_non_staff_login_denied(self, client, normal_user):
        """Non-staff users cannot login to the dashboard."""
        response = client.post(
            reverse("dashboard:login"),
            {"username": "normaluser", "password": "NormalPassword123!"},
        )
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Apenas administradores" in content


@pytest.mark.django_db
class TestDashboard2FAFlow:
    """Tests for 2FA enrollment and verification."""

    def test_2fa_setup_page_displays_qr_and_key(self, client, admin_user):
        """2FA setup page shows QR code and manual key."""
        client.force_login(admin_user)
        response = client.get(reverse("dashboard:2fa_setup"))
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "<svg" in content
        assert "Chave de configuração manual" in content

    def test_2fa_setup_valid_token_confirms_device(self, client, admin_user):
        """Submitting a valid TOTP token activates 2FA and grants dashboard access."""
        client.force_login(admin_user)
        # Load setup page to generate unconfirmed device
        client.get(reverse("dashboard:2fa_setup"))
        device = TOTPDevice.objects.get(user=admin_user, confirmed=False)

        # Generate valid token
        totp = TOTP(device.bin_key, step=device.step, t0=device.t0, digits=device.digits)
        valid_token = str(totp.token()).zfill(6)

        response = client.post(reverse("dashboard:2fa_setup"), {"token": valid_token})
        assert response.status_code == 302
        assert response.url == reverse("dashboard:index")

        device.refresh_from_db()
        assert device.confirmed is True

    def test_2fa_verify_page_validates_token(self, client, admin_user, confirmed_totp_device):
        """Submitting valid token on 2FA verify page verifies session."""
        client.force_login(admin_user)
        totp = TOTP(
            confirmed_totp_device.bin_key,
            step=confirmed_totp_device.step,
            t0=confirmed_totp_device.t0,
            digits=confirmed_totp_device.digits,
        )
        valid_token = str(totp.token()).zfill(6)

        response = client.post(reverse("dashboard:2fa_verify"), {"token": valid_token})
        assert response.status_code == 302
        assert response.url == reverse("dashboard:index")

    def test_2fa_verify_invalid_token_shows_error(self, client, admin_user, confirmed_totp_device):
        """Submitting invalid token shows error message."""
        client.force_login(admin_user)
        response = client.post(reverse("dashboard:2fa_verify"), {"token": "000000"})
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Código de verificação inválido" in content


@pytest.mark.django_db
class TestDashboardIndexAndMetrics:
    """Tests for dashboard index view and metrics."""

    def test_dashboard_index_metrics(self, auth_verified_client):
        """Dashboard displays correct metrics."""
        Post.objects.create(
            title="Post 1",
            content_md="Text 1",
            status=Post.StatusChoices.PUBLISHED,
        )
        Post.objects.create(
            title="Post 2",
            content_md="Text 2",
            status=Post.StatusChoices.DRAFT,
        )
        Tag.objects.create(name="DevOps")

        response = auth_verified_client.get(reverse("dashboard:index"))
        assert response.status_code == 200
        context = response.context
        assert context["total_posts"] == 2
        assert context["published_posts"] == 1
        assert context["draft_posts"] == 1
        assert context["total_tags"] == 1

    def test_dashboard_post_filtering(self, auth_verified_client):
        """Filtering by status and query works."""
        Post.objects.create(
            title="Docker Compose Guide",
            content_md="Text",
            status=Post.StatusChoices.PUBLISHED,
        )
        Post.objects.create(
            title="Kubernetes Guide",
            content_md="Text",
            status=Post.StatusChoices.DRAFT,
        )

        # Filter by query
        res_q = auth_verified_client.get(reverse("dashboard:index") + "?q=Docker")
        assert len(res_q.context["posts"]) == 1
        assert res_q.context["posts"][0].title == "Docker Compose Guide"

        # Filter by status
        res_status = auth_verified_client.get(reverse("dashboard:index") + "?status=draft")
        assert len(res_status.context["posts"]) == 1
        assert res_status.context["posts"][0].title == "Kubernetes Guide"


@pytest.mark.django_db
class TestPostCRUD:
    """Tests for post CRUD actions in dashboard."""

    def test_create_post(self, auth_verified_client):
        """Create new post with automatic markdown rendering."""
        data = {
            "title": "Novo Artigo Dashboard",
            "slug": "",
            "summary": "Resumo do artigo",
            "content_md": "## Subtítulo\n\nConteúdo com markdown.",
            "language": Post.LanguageChoices.PT_BR,
            "status": Post.StatusChoices.PUBLISHED,
            "meta_description": "Meta description test",
        }
        response = auth_verified_client.post(reverse("dashboard:post_create"), data)
        assert response.status_code == 302
        post = Post.objects.get(title="Novo Artigo Dashboard")
        assert post.slug == "novo-artigo-dashboard"
        assert "<h2" in post.content_html
        assert post.reading_time >= 1
        assert post.published_at is not None

    def test_update_post(self, auth_verified_client):
        """Update existing post."""
        post = Post.objects.create(title="Post Antigo", content_md="Texto antigo")
        data = {
            "title": "Post Atualizado",
            "slug": post.slug,
            "summary": "Novo resumo",
            "content_md": "# Novo Conteúdo",
            "language": Post.LanguageChoices.PT_BR,
            "status": Post.StatusChoices.PUBLISHED,
        }
        response = auth_verified_client.post(
            reverse("dashboard:post_update", kwargs={"pk": post.pk}), data
        )
        assert response.status_code == 302
        post.refresh_from_db()
        assert post.title == "Post Atualizado"
        assert "Novo Conteúdo" in post.content_html

    def test_delete_post(self, auth_verified_client):
        """Delete post."""
        post = Post.objects.create(title="Post para Deletar", content_md="Texto")
        response = auth_verified_client.post(
            reverse("dashboard:post_delete", kwargs={"pk": post.pk})
        )
        assert response.status_code == 302
        assert not Post.objects.filter(pk=post.pk).exists()

    def test_toggle_post_status(self, auth_verified_client):
        """Toggle post status between draft and published."""
        post = Post.objects.create(
            title="Post Toggle",
            content_md="Texto",
            status=Post.StatusChoices.DRAFT,
        )
        # Toggle to published
        auth_verified_client.post(reverse("dashboard:post_toggle", kwargs={"pk": post.pk}))
        post.refresh_from_db()
        assert post.status == Post.StatusChoices.PUBLISHED
        assert post.published_at is not None

        # Toggle back to draft
        auth_verified_client.post(reverse("dashboard:post_toggle", kwargs={"pk": post.pk}))
        post.refresh_from_db()
        assert post.status == Post.StatusChoices.DRAFT

    def test_post_preview_api(self, auth_verified_client):
        """Preview API returns rendered markdown HTML."""
        response = auth_verified_client.post(
            reverse("dashboard:post_preview"),
            {"content_md": "# Markdown Preview\n\n```python\nprint(1)\n```"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "<h1" in data["html"]
        assert "Markdown Preview" in data["html"]


@pytest.mark.django_db
class TestTagCRUD:
    """Tests for tag CRUD in dashboard."""

    def test_create_tag(self, auth_verified_client):
        """Create tag with auto slug."""
        response = auth_verified_client.post(
            reverse("dashboard:tag_create"),
            {"name": "Terraform Cloud", "slug": ""},
        )
        assert response.status_code == 302
        tag = Tag.objects.get(name="Terraform Cloud")
        assert tag.slug == "terraform-cloud"

    def test_update_tag(self, auth_verified_client):
        """Update tag."""
        tag = Tag.objects.create(name="AWS")
        response = auth_verified_client.post(
            reverse("dashboard:tag_update", kwargs={"pk": tag.pk}),
            {"name": "Amazon Web Services", "slug": "aws-cloud"},
        )
        assert response.status_code == 302
        tag.refresh_from_db()
        assert tag.name == "Amazon Web Services"
        assert tag.slug == "aws-cloud"

    def test_delete_tag(self, auth_verified_client):
        """Delete tag."""
        tag = Tag.objects.create(name="DeleteMe")
        response = auth_verified_client.post(reverse("dashboard:tag_delete", kwargs={"pk": tag.pk}))
        assert response.status_code == 302
        assert not Tag.objects.filter(pk=tag.pk).exists()


@pytest.mark.django_db
class TestMediaCRUD:
    """Tests for media upload and deletion in dashboard."""

    def test_media_upload_and_delete(self, auth_verified_client):
        """Upload media file with alt text and delete it."""
        fake_image = SimpleUploadedFile(
            name="test_image.png",
            content=b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4",
            content_type="image/png",
        )
        response = auth_verified_client.post(
            reverse("dashboard:media_upload"),
            {"file": fake_image, "alt_text": "Arquitetura do Render"},
        )
        assert response.status_code == 302
        asset = MediaAsset.objects.get(alt_text="Arquitetura do Render")
        assert asset.file is not None

        # Delete asset
        del_response = auth_verified_client.post(
            reverse("dashboard:media_delete", kwargs={"pk": asset.pk})
        )
        assert del_response.status_code == 302
        assert not MediaAsset.objects.filter(pk=asset.pk).exists()


@pytest.mark.django_db
class TestSiteConfigAndAuthActions:
    """Tests for SiteConfig editing, password change, and logout."""

    def test_site_config_update(self, auth_verified_client):
        """Update SiteConfig fields."""
        data = {
            "site_title_pt": "Blog do Luiz",
            "site_title_en": "Luiz Blog",
            "tagline_pt": "DevOps e Backend",
            "tagline_en": "DevOps and Backend",
            "about_pt": "Bio em PT",
            "about_en": "Bio in EN",
            "email": "luiz@example.com",
            "github_url": "https://github.com/luiz",
            "linkedin_url": "https://linkedin.com/in/luiz",
            "portfolio_url": "https://luiz.dev",
        }
        response = auth_verified_client.post(reverse("dashboard:site_config"), data)
        assert response.status_code == 302
        config = SiteConfig.get_solo()
        assert config.site_title_pt == "Blog do Luiz"
        assert config.email == "luiz@example.com"

    def test_password_change(self, auth_verified_client, admin_user):
        """Change password successfully."""
        data = {
            "old_password": "ValidPassword123!",
            "new_password1": "NewSecurePassword456!",
            "new_password2": "NewSecurePassword456!",
        }
        response = auth_verified_client.post(reverse("dashboard:password_change"), data)
        assert response.status_code == 302
        admin_user.refresh_from_db()
        assert admin_user.check_password("NewSecurePassword456!")

    def test_dashboard_logout(self, auth_verified_client):
        """Logout ends session."""
        response = auth_verified_client.post(reverse("dashboard:logout"))
        assert response.status_code == 302
        assert reverse("dashboard:login") in response.url


@pytest.mark.django_db
class TestAxesBruteForceProtection:
    """Tests for axes brute-force lockout."""

    def test_axes_locks_out_after_failure_limit(self, client):
        """Multiple failed logins lock out the client."""
        login_url = reverse("dashboard:login")

        # AXES_FAILURE_LIMIT is 5
        for _ in range(5):
            client.post(login_url, {"username": "admin", "password": "wrongpassword"})

        # 6th attempt should be locked out
        response = client.post(login_url, {"username": "admin", "password": "wrongpassword"})
        assert response.status_code in [403, 429, 200]
        content = response.content.decode("utf-8")
        assert "Acesso Bloqueado" in content or "bloqueado" in content.lower()
