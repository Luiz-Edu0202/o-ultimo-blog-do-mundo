"""URLs for blog app."""

from django.urls import path

from apps.blog.feeds import LatestPostsFeed
from apps.blog.views import PostDetailView, PostListView, PostSearchView, TagPostListView

app_name = "blog"

urlpatterns = [
    path("", PostListView.as_view(), name="home"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("tags/<slug:slug>/", TagPostListView.as_view(), name="tag_posts"),
    path("busca/", PostSearchView.as_view(), name="post_search"),
    path("feed/", LatestPostsFeed(), name="post_feed"),
]
