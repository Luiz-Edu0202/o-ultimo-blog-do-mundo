"""Tests for public views, SEO, i18n, search, feeds, and sitemaps."""

import pytest
from django.template import Context, Template
from django.test import RequestFactory
from django.urls import reverse
from django.utils import timezone

from apps.blog.models import Post, Tag
from apps.core.models import SiteConfig


@pytest.fixture
def site_config():
    """Ensure site config exists."""
    return SiteConfig.objects.create(
        site_title_pt="O Último Blog do Mundo",
        site_title_en="The Last Blog in the World",
        tagline_pt="Blog sobre DevOps e Cloud",
        tagline_en="Blog about DevOps and Cloud",
        about_pt="Sobre o autor em português.",
        about_en="About author in English.",
    )


@pytest.fixture
def sample_tag():
    return Tag.objects.create(name="Kubernetes")


@pytest.fixture
def sample_posts(sample_tag):
    """Create sample published and draft posts in PT and EN."""
    now = timezone.now()

    # Published PT post
    post_pt = Post.objects.create(
        title="Deploy no Render com Docker",
        slug="deploy-render-docker",
        summary="Aprenda a fazer deploy no Render.",
        content_md="# Deploy no Render\n\nArtigo completo com código.",
        language=Post.LanguageChoices.PT_BR,
        status=Post.StatusChoices.PUBLISHED,
        published_at=now,
    )
    post_pt.tags.add(sample_tag)

    # Published EN post (translation of PT post)
    post_en = Post.objects.create(
        title="Deploy on Render with Docker",
        slug="deploy-render-docker",
        summary="Learn how to deploy on Render.",
        content_md="# Deploy on Render\n\nFull article with code.",
        language=Post.LanguageChoices.EN,
        status=Post.StatusChoices.PUBLISHED,
        published_at=now,
        translation_of=post_pt,
    )
    post_en.tags.add(sample_tag)

    # Draft post (should NOT appear on public views)
    draft_post = Post.objects.create(
        title="Post em Rascunho",
        slug="post-em-rascunho",
        content_md="Ainda não publicado.",
        language=Post.LanguageChoices.PT_BR,
        status=Post.StatusChoices.DRAFT,
    )

    return {
        "post_pt": post_pt,
        "post_en": post_en,
        "draft_post": draft_post,
    }


@pytest.mark.django_db
class TestPublicHomeView:
    """Tests for Home view / post list."""

    def test_home_pt_displays_only_published_pt_posts(self, client, sample_posts, site_config):
        url = reverse("blog:home")
        response = client.get(url)
        assert response.status_code == 200
        assert "Deploy no Render com Docker" in response.content.decode("utf-8")
        assert "Deploy on Render with Docker" not in response.content.decode("utf-8")
        assert "Post em Rascunho" not in response.content.decode("utf-8")

    def test_home_en_displays_only_published_en_posts(self, client, sample_posts, site_config):
        response = client.get("/en/")
        assert response.status_code == 200
        assert "Deploy on Render with Docker" in response.content.decode("utf-8")
        assert "Deploy no Render com Docker" not in response.content.decode("utf-8")
        assert "Post em Rascunho" not in response.content.decode("utf-8")

    def test_home_pagination(self, client, site_config):
        # Create 15 published posts
        for i in range(15):
            Post.objects.create(
                title=f"Post número {i:02d}",
                content_md=f"Conteúdo do post {i}",
                status=Post.StatusChoices.PUBLISHED,
            )
        response = client.get(reverse("blog:home"))
        assert response.status_code == 200
        assert len(response.context["posts"]) == 10
        assert response.context["is_paginated"] is True

        page2_response = client.get(reverse("blog:home") + "?page=2")
        assert page2_response.status_code == 200
        assert len(page2_response.context["posts"]) == 5


@pytest.mark.django_db
class TestPostDetailView:
    """Tests for individual post detail view."""

    def test_post_detail_success_pt(self, client, sample_posts, site_config):
        post = sample_posts["post_pt"]
        url = post.get_absolute_url()
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert post.title in content
        assert "schema.org" in content
        assert "og:title" in content
        assert "twitter:card" in content
        assert "deploy-render-docker" in content

    def test_post_detail_displays_translation_link(self, client, sample_posts, site_config):
        post = sample_posts["post_pt"]
        response = client.get(post.get_absolute_url())
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "English" in content
        assert "/en/posts/deploy-render-docker/" in content

    def test_draft_post_returns_404(self, client, sample_posts):
        draft = sample_posts["draft_post"]
        response = client.get(f"/posts/{draft.slug}/")
        assert response.status_code == 404

    def test_nonexistent_post_returns_404(self, client):
        response = client.get("/posts/post-inexistente-12345/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestTagPostListView:
    """Tests for tag post list view."""

    def test_tag_list_displays_associated_published_posts(self, client, sample_posts, sample_tag):
        url = sample_tag.get_absolute_url()
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Kubernetes" in content
        assert "Deploy no Render com Docker" in content

    def test_nonexistent_tag_returns_404(self, client):
        response = client.get("/tags/tag-fantasma/")
        assert response.status_code == 404


@pytest.mark.django_db
class TestPostSearchView:
    """Tests for post search view."""

    def test_search_by_title_and_content(self, client, sample_posts):
        # Search for "Render" in PT
        url = reverse("blog:post_search") + "?q=Render"
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Deploy no Render com Docker" in content
        assert "Post em Rascunho" not in content

    def test_empty_search_returns_empty_results(self, client):
        url = reverse("blog:post_search")
        response = client.get(url)
        assert response.status_code == 200
        assert len(response.context["posts"]) == 0


@pytest.mark.django_db
class TestAboutView:
    """Tests for About view."""

    def test_about_page_pt(self, client, site_config):
        url = reverse("core:about")
        response = client.get(url)
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "Sobre o autor em português." in content

    def test_about_page_en(self, client, site_config):
        response = client.get("/en/sobre/")
        assert response.status_code == 200
        content = response.content.decode("utf-8")
        assert "About author in English." in content


@pytest.mark.django_db
class TestFeedsAndSitemaps:
    """Tests for RSS feed, Sitemap, and robots.txt."""

    def test_rss_feed_pt(self, client, sample_posts, site_config):
        url = reverse("blog:post_feed")
        response = client.get(url)
        assert response.status_code == 200
        assert "application/rss+xml" in response["Content-Type"]
        content = response.content.decode("utf-8")
        assert "Deploy no Render com Docker" in content

    def test_sitemap_xml(self, client, sample_posts):
        response = client.get("/sitemap.xml")
        assert response.status_code == 200
        content_type = response["Content-Type"]
        assert "application/xml" in content_type or "text/xml" in content_type
        content = response.content.decode("utf-8")
        assert "/posts/deploy-render-docker/" in content

    def test_robots_txt(self, client):
        response = client.get("/robots.txt")
        assert response.status_code == 200
        assert response["Content-Type"] == "text/plain"
        content = response.content.decode("utf-8")
        assert "User-agent: *" in content
        assert "Disallow: /gestao/" in content
        assert "Sitemap:" in content
        assert "/sitemap.xml" in content


class TestErrorViews:
    """Tests for custom 404 and 500 error views."""

    def test_custom_404_view(self, client):
        response = client.get("/rota-inexistente-totalmente-aleatoria/")
        assert response.status_code == 404
        content = response.content.decode("utf-8")
        assert "404" in content
        assert "Página não encontrada" in content

    def test_custom_500_handler(self, client):
        from apps.core.views import custom_500

        factory = RequestFactory()
        request = factory.get("/")
        response = custom_500(request)
        assert response.status_code == 500
        content = response.content.decode("utf-8")
        assert "500" in content
        assert "Erro interno do servidor" in content


@pytest.mark.django_db
class TestChangeLangTag:
    """Tests for change_lang template tag."""

    def test_change_lang_simple_page(self):
        factory = RequestFactory()
        request = factory.get("/sobre/")
        template = Template("{% load core_tags %}{% change_lang 'en' %}")
        context = Context({"request": request})
        rendered = template.render(context)
        assert "/en/" in rendered
