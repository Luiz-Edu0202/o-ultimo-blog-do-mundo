"""URL patterns for the administration dashboard."""

from django.urls import path

from apps.dashboard import auth_views, views

app_name = "dashboard"

urlpatterns = [
    # Authentication & 2FA
    path("login/", auth_views.DashboardLoginView.as_view(), name="login"),
    path("logout/", auth_views.DashboardLogoutView.as_view(), name="logout"),
    path("2fa/setup/", auth_views.Dashboard2FASetupView.as_view(), name="2fa_setup"),
    path("2fa/verify/", auth_views.Dashboard2FAVerifyView.as_view(), name="2fa_verify"),
    path(
        "password/",
        auth_views.DashboardPasswordChangeView.as_view(),
        name="password_change",
    ),
    # Dashboard home & posts
    path("", views.DashboardIndexView.as_view(), name="index"),
    path("posts/new/", views.PostCreateView.as_view(), name="post_create"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post_update"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post_delete"),
    path(
        "posts/<int:pk>/toggle/",
        views.PostToggleStatusView.as_view(),
        name="post_toggle",
    ),
    path("preview/", views.PostPreviewApiView.as_view(), name="post_preview"),
    # Tags
    path("tags/", views.TagListView.as_view(), name="tag_list"),
    path("tags/new/", views.TagCreateView.as_view(), name="tag_create"),
    path("tags/<int:pk>/edit/", views.TagUpdateView.as_view(), name="tag_update"),
    path("tags/<int:pk>/delete/", views.TagDeleteView.as_view(), name="tag_delete"),
    # Media
    path("media/", views.MediaListView.as_view(), name="media_list"),
    path("media/upload/", views.MediaUploadView.as_view(), name="media_upload"),
    path("media/<int:pk>/delete/", views.MediaDeleteView.as_view(), name="media_delete"),
    # Site Configuration
    path("config/", views.SiteConfigUpdateView.as_view(), name="site_config"),
]
