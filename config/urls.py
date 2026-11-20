"""URL configuration for O Último Blog do Mundo."""

from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap
from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.urls import include, path

from apps.blog.sitemaps import PostSitemap, StaticViewSitemap, TagSitemap
from apps.core.views import robots_txt

sitemaps = {
    "posts": PostSitemap,
    "tags": TagSitemap,
    "static": StaticViewSitemap,
}


def healthcheck(request):
    """Healthcheck endpoint that validates DB and cache connectivity.

    Returns 200 with JSON body {"status": "ok"} when everything is healthy.
    Returns 503 with JSON body {"status": "error", "details": {...}} on failure.
    """
    checks = {}

    # --- Database check ---
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        checks["db"] = "ok"
    except Exception as exc:
        checks["db"] = f"error: {exc}"

    # --- Cache / Redis check ---
    try:
        cache.set("healthcheck", "ok", timeout=5)
        value = cache.get("healthcheck")
        checks["cache"] = "ok" if value == "ok" else "error: unexpected value"
    except Exception as exc:
        checks["cache"] = f"error: {exc}"

    all_ok = all(v == "ok" for v in checks.values())
    status_code = 200 if all_ok else 503
    payload = {"status": "ok" if all_ok else "error", "checks": checks}
    return JsonResponse(payload, status=status_code)


admin_path = getattr(settings, "ADMIN_PATH", "gestao").strip("/")

# URLs that should NOT have language prefixes
urlpatterns = [
    path(f"{admin_path}/", include("apps.dashboard.urls", namespace="dashboard")),
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
