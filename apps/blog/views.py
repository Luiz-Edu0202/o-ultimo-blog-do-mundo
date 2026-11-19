"""Views for the blog app."""

from django.db.models import Q
from django.http import Http404
from django.utils.translation import get_language
from django.views.generic import DetailView, ListView

from apps.blog.models import Post, Tag
from apps.core.models import SiteConfig


class PostListView(ListView):
    """Home view listing published posts in current language, paginated by 10."""

    model = Post
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        lang = get_language()
        lang_code = Post.LanguageChoices.EN if lang.startswith("en") else Post.LanguageChoices.PT_BR
        return (
            Post.objects.filter(
                status=Post.StatusChoices.PUBLISHED,
                language=lang_code,
            )
            .select_related("translation_of")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["site_config"] = SiteConfig.get_solo()
        context["all_tags"] = Tag.objects.filter(
            posts__status=Post.StatusChoices.PUBLISHED
        ).distinct()
        return context


class PostDetailView(DetailView):
    """Detail view for a single post."""

    model = Post
    template_name = "blog/post_detail.html"
    context_object_name = "post"

    def get_object(self, queryset=None):
        slug = self.kwargs.get("slug")
        lang = get_language()
        lang_code = Post.LanguageChoices.EN if lang.startswith("en") else Post.LanguageChoices.PT_BR

        # Try to find post in current language
        post = (
            Post.objects.filter(
                slug=slug,
                language=lang_code,
                status=Post.StatusChoices.PUBLISHED,
            )
            .select_related("translation_of")
            .prefetch_related("tags")
            .first()
        )

        if not post:
            # Check if it exists in another language to provide helpful 404 or redirect
            post = (
                Post.objects.filter(
                    slug=slug,
                    status=Post.StatusChoices.PUBLISHED,
                )
                .select_related("translation_of")
                .prefetch_related("tags")
                .first()
            )

        if not post:
            raise Http404("Post não encontrado.")

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object

        # Find translation if available
        translation = None
        if post.translation_of:
            translation = post.translation_of
        else:
            translation = post.translations.filter(status=Post.StatusChoices.PUBLISHED).first()

        context["translation"] = translation
        context["site_config"] = SiteConfig.get_solo()
        return context


class TagPostListView(ListView):
    """List published posts for a specific tag in current language, paginated by 10."""

    model = Post
    template_name = "blog/tag_post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        slug = self.kwargs.get("slug")
        lang = get_language()
        lang_code = Post.LanguageChoices.EN if lang.startswith("en") else Post.LanguageChoices.PT_BR
        return (
            Post.objects.filter(
                tags__slug=slug,
                status=Post.StatusChoices.PUBLISHED,
                language=lang_code,
            )
            .select_related("translation_of")
            .prefetch_related("tags")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        try:
            tag = Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            raise Http404("Tag não encontrada.") from None

        context["tag"] = tag
        context["site_config"] = SiteConfig.get_solo()
        return context


class PostSearchView(ListView):
    """Search published posts in title and content_md in current language."""

    model = Post
    template_name = "blog/post_search.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if not query:
            return Post.objects.none()

        lang = get_language()
        lang_code = Post.LanguageChoices.EN if lang.startswith("en") else Post.LanguageChoices.PT_BR
        return (
            Post.objects.filter(
                Q(title__icontains=query) | Q(content_md__icontains=query),
                status=Post.StatusChoices.PUBLISHED,
                language=lang_code,
            )
            .select_related("translation_of")
            .prefetch_related("tags")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        context["site_config"] = SiteConfig.get_solo()
        return context
