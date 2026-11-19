"""Tests for core and blog models."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone

from apps.blog.markdown_services import calculate_reading_time, render_markdown
from apps.blog.models import MediaAsset, Post, Tag
from apps.core.models import SiteConfig


@pytest.mark.django_db
class TestSiteConfigModel:
    """Tests for SiteConfig singleton model."""

    def test_singleton_always_pk_1(self):
        config1 = SiteConfig.objects.create(site_title_pt="Blog 1")
        assert config1.pk == 1

        config2 = SiteConfig.objects.create(site_title_pt="Blog 2")
        assert config2.pk == 1
        assert SiteConfig.objects.count() == 1
        assert SiteConfig.objects.get(pk=1).site_title_pt == "Blog 2"

    def test_get_solo_returns_existing_or_creates_default(self):
        SiteConfig.objects.all().delete()
        solo = SiteConfig.get_solo()
        assert solo.pk == 1
        assert solo.site_title_pt == "O Último Blog do Mundo"

        # Calling again returns same instance
        solo2 = SiteConfig.get_solo()
        assert solo2.pk == solo.pk
        assert str(solo2) == "O Último Blog do Mundo"


class TestMarkdownServices:
    """Tests for markdown rendering, sanitization, and reading time."""

    def test_render_markdown_basic_and_highlight(self):
        md = "## Subtitle\n\n```python\nprint('hello')\n```"
        html = render_markdown(md)
        assert "<h2" in html
        assert "Subtitle" in html
        assert '<div class="codehilite">' in html or "<pre><span></span><code>" in html

    def test_render_markdown_sanitization(self):
        md = "Hello <script>alert('xss')</script> world <iframe src='evil.com'></iframe>"
        html = render_markdown(md)
        assert "<script>" not in html
        assert "alert(" not in html
        assert "<iframe" not in html
        assert "Hello" in html
        assert "world" in html

    def test_calculate_reading_time(self):
        empty_time = calculate_reading_time("")
        assert empty_time == 1

        # 400 words = ~2 minutes
        text = "word " * 400
        assert calculate_reading_time(text) == 2


@pytest.mark.django_db
class TestTagModel:
    """Tests for blog.Tag model."""

    def test_tag_creation_and_auto_slug(self):
        tag = Tag.objects.create(name="DevOps & Cloud")
        assert tag.slug == "devops-cloud"
        assert str(tag) == "DevOps & Cloud"
        assert tag.get_absolute_url() == "/tags/devops-cloud/"


@pytest.mark.django_db
class TestPostModel:
    """Tests for blog.Post model."""

    def test_post_creation_auto_slug_and_html(self):
        post = Post.objects.create(
            title="Primeiro Post Técnico",
            content_md="# Olá Mundo\n\nEste é o primeiro artigo do blog.",
            language=Post.LanguageChoices.PT_BR,
        )
        assert post.slug == "primeiro-post-tecnico"
        assert '<h1 id="ola-mundo">Olá Mundo</h1>' in post.content_html
        assert post.reading_time >= 1
        assert post.status == Post.StatusChoices.DRAFT
        assert post.published_at is None
        assert str(post) == "Primeiro Post Técnico (Português)"
        assert post.get_absolute_url() == "/posts/primeiro-post-tecnico/"

    def test_published_post_sets_published_at_automatically(self):
        post = Post.objects.create(
            title="Post Publicado",
            content_md="Conteúdo publicado.",
            status=Post.StatusChoices.PUBLISHED,
        )
        assert post.published_at is not None
        assert post.published_at <= timezone.now()

    def test_translation_cannot_target_self(self):
        post = Post.objects.create(
            title="Post Auto Referente",
            content_md="Texto",
        )
        post.translation_of = post
        with pytest.raises(ValidationError) as exc_info:
            post.clean()
        assert "translation_of" in exc_info.value.message_dict

    def test_translation_must_target_different_language(self):
        post_pt = Post.objects.create(
            title="Post em Português",
            content_md="Texto",
            language=Post.LanguageChoices.PT_BR,
        )
        post_pt_2 = Post.objects.create(
            title="Outro em Português",
            content_md="Texto 2",
            language=Post.LanguageChoices.PT_BR,
        )
        post_pt_2.translation_of = post_pt
        with pytest.raises(ValidationError) as exc_info:
            post_pt_2.clean()
        assert "translation_of" in exc_info.value.message_dict

    def test_valid_translation_cross_language(self):
        post_pt = Post.objects.create(
            title="Arquitetura de Nuvem",
            content_md="Texto em PT",
            language=Post.LanguageChoices.PT_BR,
        )
        post_en = Post.objects.create(
            title="Cloud Architecture",
            content_md="Text in EN",
            language=Post.LanguageChoices.EN,
            translation_of=post_pt,
        )
        assert post_en.translation_of == post_pt

    def test_unique_slug_per_language(self):
        Post.objects.create(
            title="Django no Render",
            slug="django-render",
            content_md="Texto PT",
            language=Post.LanguageChoices.PT_BR,
        )
        # Same slug in different language is allowed
        post_en = Post.objects.create(
            title="Django on Render",
            slug="django-render",
            content_md="Text EN",
            language=Post.LanguageChoices.EN,
        )
        assert post_en.slug == "django-render"

        # Same slug in same language raises error
        with pytest.raises((IntegrityError, ValidationError)):
            Post.objects.create(
                title="Django no Render 2",
                slug="django-render",
                content_md="Texto PT 2",
                language=Post.LanguageChoices.PT_BR,
            )


@pytest.mark.django_db
class TestMediaAssetModel:
    """Tests for blog.MediaAsset model."""

    def test_media_asset_str(self):
        asset = MediaAsset(alt_text="Diagrama de Arquitetura")
        assert str(asset) == "Diagrama de Arquitetura"
