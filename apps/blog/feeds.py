"""RSS Syndication Feed for published blog posts."""

from django.contrib.syndication.views import Feed
from django.utils.translation import get_language

from apps.blog.models import Post
from apps.core.models import SiteConfig


class LatestPostsFeed(Feed):
    """RSS feed for latest 20 published posts in current language."""

    def title(self):
        site_config = SiteConfig.get_solo()
        lang = get_language()
        return site_config.site_title_en if lang.startswith("en") else site_config.site_title_pt

    def link(self):
        return "/"

    def description(self):
        site_config = SiteConfig.get_solo()
        lang = get_language()
        return site_config.tagline_en if lang.startswith("en") else site_config.tagline_pt

    def items(self):
        lang = get_language()
        lang_code = Post.LanguageChoices.EN if lang.startswith("en") else Post.LanguageChoices.PT_BR
        return Post.objects.filter(
            status=Post.StatusChoices.PUBLISHED,
            language=lang_code,
        ).order_by("-published_at")[:20]

    def item_title(self, item: Post) -> str:
        return item.title

    def item_description(self, item: Post) -> str:
        return item.summary or item.content_md[:200]

    def item_pubdate(self, item: Post):
        return item.published_at
