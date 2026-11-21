from pathlib import Path

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from apps.blog.models import Post, Tag
from apps.core.models import SiteConfig


class TestVisualIdentityStaticAssets(TestCase):
    """Test locally-hosted fonts and CSS stylesheets."""

    def test_local_fonts_exist_and_non_empty(self):
        static_dir = Path(settings.BASE_DIR) / "static"
        expected_fonts = [
            "fonts/space-grotesk/SpaceGrotesk-Medium.woff2",
            "fonts/space-grotesk/SpaceGrotesk-Bold.woff2",
            "fonts/inter/Inter-Regular.woff2",
            "fonts/inter/Inter-Medium.woff2",
            "fonts/inter/Inter-SemiBold.woff2",
            "fonts/jetbrains-mono/JetBrainsMono-Light.woff2",
            "fonts/jetbrains-mono/JetBrainsMono-Regular.woff2",
        ]
        for font_rel_path in expected_fonts:
            font_path = static_dir / font_rel_path
            self.assertTrue(font_path.exists(), f"Font file missing: {font_rel_path}")
            self.assertGreater(
                font_path.stat().st_size, 1000, f"Font file empty/truncated: {font_rel_path}"
            )

    def test_css_modular_stylesheets_exist(self):
        static_dir = Path(settings.BASE_DIR) / "static" / "css"
        expected_css = [
            "custom.css",
            "tokens.css",
            "fonts.css",
            "base.css",
            "pygments.css",
            "responsive.css",
            "components/navbar.css",
            "components/cards.css",
            "components/post.css",
            "components/sidebar.css",
            "components/footer.css",
            "components/pages.css",
            "components/dashboard.css",
        ]
        for css_file in expected_css:
            path = static_dir / css_file
            self.assertTrue(path.exists(), f"CSS file missing: {css_file}")
            self.assertGreater(path.stat().st_size, 50, f"CSS file too small: {css_file}")

    def test_design_tokens_content(self):
        tokens_path = Path(settings.BASE_DIR) / "static" / "css" / "tokens.css"
        content = tokens_path.read_text(encoding="utf-8")
        self.assertIn("--bg-void", content)
        self.assertIn("--bg-surface", content)
        self.assertIn("--accent", content)
        self.assertIn("Space Grotesk", content)
        self.assertIn("JetBrains Mono", content)
        self.assertIn("Inter", content)
        self.assertIn('[data-bs-theme="dark"]', content)
        self.assertIn('[data-bs-theme="light"]', content)


class TestVisualIdentityTemplates(TestCase):
    """Test rendered templates contain retro-terminal and responsive elements."""

    def setUp(self):
        self.client = Client()
        self.site_config = SiteConfig.get_solo()
        self.site_config.site_title_pt = "O Último Blog do Mundo"
        self.site_config.site_title_en = "The Last Blog in the World"
        self.site_config.tagline_pt = "Transmissões do fim dos tempos"
        self.site_config.save()

        self.tag = Tag.objects.create(name="DevOps")
        self.post = Post.objects.create(
            title="Transmissão Inicial",
            content_md="# Olá Mundo\n\n```python\nprint('hello')\n```",
            status="published",
            language="pt-br",
        )
        self.post.tags.add(self.tag)

    def test_home_page_has_terminal_elements(self):
        response = self.client.get(reverse("blog:home"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        # Navbar and branding
        self.assertIn("site-header", content)
        self.assertIn("site-brand", content)
        self.assertIn("brand-version", content)
        self.assertIn("cursor-blink", content)

        # Offcanvas mobile menu
        self.assertIn("navbarOffcanvas", content)
        self.assertIn("offcanvas-nav", content)

        # Theme toggle buttons (desktop + mobile)
        self.assertIn('id="theme-toggle"', content)
        self.assertIn('id="theme-toggle-mobile"', content)

        # Post card and terminal badges
        self.assertIn("post-card", content)
        self.assertIn("tag-badge", content)
        self.assertIn("post-meta", content)

        # Footer terminal prompt
        self.assertIn("site-footer", content)
        self.assertIn("footer-prompt", content)
        self.assertIn("prompt-user", content)

    def test_post_detail_has_typography_and_code_styles(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn("post-header", content)
        self.assertIn("post-content", content)
        self.assertIn("codehilite", content)
        self.assertIn("post-article-footer", content)

    def test_search_page_has_terminal_form(self):
        response = self.client.get(reverse("blog:post_search") + "?q=Transmissão")
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn("search-form", content)
        self.assertIn("btn-search", content)
        self.assertIn("highlight", content)

    def test_about_page_has_terminal_sections(self):
        response = self.client.get(reverse("core:about"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn("about-section", content)
        self.assertIn("about-tagline", content)
        self.assertIn("connect-title", content)

    def test_404_page_has_ascii_art(self):
        response = self.client.get("/pagina-inexistente-404-teste/")
        self.assertEqual(response.status_code, 404)
        content = response.content.decode("utf-8")

        self.assertIn("error-page", content)
        self.assertIn("error-ascii", content)
        self.assertIn("error-code", content)
        self.assertIn("404", content)

    def test_dashboard_login_page_has_cyber_theme(self):
        response = self.client.get(reverse("dashboard:login"))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode("utf-8")

        self.assertIn("login-page", content)
        self.assertIn("login-card", content)
        self.assertIn("btn-login", content)
        self.assertIn("AUTENTICACAO_ADMIN", content)
