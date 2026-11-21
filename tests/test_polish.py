from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.test import Client, TestCase

from apps.blog.models import Post, Tag
from apps.core.models import SiteConfig


class TestPolishAndAccessibility(TestCase):
    """Test accessibility features, seed_demo command, and final security rules."""

    def setUp(self):
        self.client = Client()

    def test_seed_demo_command(self):
        """seed_demo should create realistic articles, tags and configure site."""
        call_command("seed_demo")

        self.assertGreaterEqual(Post.objects.count(), 3)
        self.assertGreaterEqual(Tag.objects.count(), 5)

        site_config = SiteConfig.get_solo()
        self.assertEqual(site_config.site_title_pt, "O Último Blog do Mundo")
        self.assertTrue(site_config.about_pt)
        self.assertTrue(site_config.about_en)

    def test_css_reduced_motion_support(self):
        """base.css must contain prefers-reduced-motion support (WCAG AA)."""
        base_css = Path(settings.BASE_DIR) / "static" / "css" / "base.css"
        content = base_css.read_text(encoding="utf-8")
        self.assertIn("@media (prefers-reduced-motion: reduce)", content)
        self.assertIn("animation-duration", content)

    def test_css_focus_visible_styling(self):
        """base.css must provide visible outline on :focus-visible."""
        base_css = Path(settings.BASE_DIR) / "static" / "css" / "base.css"
        content = base_css.read_text(encoding="utf-8")
        self.assertIn(":focus-visible", content)
        self.assertIn("outline:", content)

    def test_django_admin_url_is_strictly_not_found(self):
        """Standard Django admin route /admin/ must return 404 (not mapped)."""
        response = self.client.get("/admin/")
        self.assertEqual(response.status_code, 404)

        response_login = self.client.get("/admin/login/")
        self.assertEqual(response_login.status_code, 404)

    def test_semantic_landmarks_rendered(self):
        """Home page must contain standard HTML5 semantic landmarks and skip link."""
        call_command("seed_demo")
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn('<header class="site-header">', content)
        self.assertIn('<main id="main-content"', content)
        self.assertIn('<footer class="site-footer">', content)
        self.assertIn('class="skip-link"', content)
        self.assertIn('<article class="post-card">', content)
        self.assertIn('<aside class="col-lg-4', content)
