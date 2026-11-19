"""Views for the core app."""

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import get_language
from django.views.generic import TemplateView

from apps.core.models import SiteConfig


class AboutView(TemplateView):
    """About page displaying content from SiteConfig in the current language."""

    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        site_config = SiteConfig.get_solo()
        current_lang = get_language()

        if current_lang.startswith("en"):
            about_content = site_config.about_en or site_config.about_pt
            tagline = site_config.tagline_en or site_config.tagline_pt
        else:
            about_content = site_config.about_pt or site_config.about_en
            tagline = site_config.tagline_pt or site_config.tagline_en

        if current_lang.startswith("en"):
            page_title = site_config.site_title_en
        else:
            page_title = site_config.site_title_pt
        context.update(
            {
                "site_config": site_config,
                "about_content": about_content,
                "tagline": tagline,
                "page_title": page_title,
            }
        )
        return context


def robots_txt(request):
    """Generate robots.txt directing search engines to sitemap and blocking admin."""
    admin_path = getattr(settings, "ADMIN_PATH", "gestao")
    lines = [
        "User-agent: *",
        f"Disallow: /{admin_path}/",
        f"Sitemap: {request.build_absolute_uri('/sitemap.xml')}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def custom_404(request, exception=None):
    """Custom 404 Not Found error view."""
    return render(request, "404.html", status=404)


def custom_500(request):
    """Custom 500 Server Error view."""
    return render(request, "500.html", status=500)
