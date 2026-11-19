"""Sitemaps for public blog pages."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.blog.models import Post, Tag


class PostSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Post.objects.filter(status=Post.StatusChoices.PUBLISHED)

    def lastmod(self, obj: Post):
        return obj.updated_at


class TagSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Tag.objects.filter(posts__status=Post.StatusChoices.PUBLISHED).distinct()


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "monthly"

    def items(self):
        return ["blog:home", "core:about"]

    def location(self, item):
        return reverse(item)
