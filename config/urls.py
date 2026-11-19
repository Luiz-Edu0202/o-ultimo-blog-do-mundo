"""URL configuration for O Último Blog do Mundo."""

from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.http import HttpResponse
from django.urls import include, path

from apps.blog.sitemaps import PostSitemap, StaticViewSitemap, TagSitemap
from apps.core.views import robots_txt

sitemaps = {
    "posts": PostSitemap,
    "tags": TagSitemap,
    "static": StaticViewSitemap,
}


def healthcheck(request):
    """Healthcheck endpoint responding 200 OK."""
    return HttpResponse("ok", content_type="text/plain")


# URLs that should NOT have language prefixes
urlpatterns = [
    path("healthz", healthcheck, name="healthcheck"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]

# URLs with language prefix support (/en/ for English, / for default pt-br)
urlpatterns += i18n_patterns(
    path("", include("apps.blog.urls", namespace="blog")),
    path("", include("apps.core.urls", namespace="core")),
    prefix_default_language=False,
)

# Custom error handlers
handler404 = "apps.core.views.custom_404"
handler500 = "apps.core.views.custom_500"
