"""Views for admin dashboard: posts, tags, media, and site configuration."""

from django.contrib import messages
from django.db.models import Count, Q
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
)

from apps.blog.markdown_services import render_markdown
from apps.blog.models import MediaAsset, Post, Tag
from apps.core.models import SiteConfig
from apps.dashboard.decorators import DashboardAuthMixin
from apps.dashboard.forms import (
    MediaUploadForm,
    PostForm,
    SiteConfigForm,
    TagForm,
)


class DashboardIndexView(DashboardAuthMixin, TemplateView):
    """Main dashboard overview with metrics and filterable posts table."""

    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Filters
        query = self.request.GET.get("q", "").strip()
        status_filter = self.request.GET.get("status", "")
        lang_filter = self.request.GET.get("lang", "")

        posts_qs = (
            Post.objects.all()
            .select_related("translation_of")
            .prefetch_related("tags")
            .order_by("-created_at")
        )

        if query:
            posts_qs = posts_qs.filter(Q(title__icontains=query) | Q(content_md__icontains=query))
        if status_filter in [Post.StatusChoices.PUBLISHED, Post.StatusChoices.DRAFT]:
            posts_qs = posts_qs.filter(status=status_filter)
        if lang_filter in [Post.LanguageChoices.PT_BR, Post.LanguageChoices.EN]:
            posts_qs = posts_qs.filter(language=lang_filter)

        context.update(
            {
                "posts": posts_qs[:50],  # Recent posts
                "total_posts": Post.objects.count(),
                "published_posts": Post.objects.filter(status=Post.StatusChoices.PUBLISHED).count(),
                "draft_posts": Post.objects.filter(status=Post.StatusChoices.DRAFT).count(),
                "total_tags": Tag.objects.count(),
                "total_media": MediaAsset.objects.count(),
                "q": query,
                "selected_status": status_filter,
                "selected_lang": lang_filter,
            }
        )
        return context


class PostCreateView(DashboardAuthMixin, CreateView):
    """Create a new blog post."""

    model = Post
    form_class = PostForm
    template_name = "dashboard/post_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form: PostForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Artigo "{self.object.title}" criado com sucesso!')
        return response


class PostUpdateView(DashboardAuthMixin, UpdateView):
    """Edit an existing blog post."""

    model = Post
    form_class = PostForm
    template_name = "dashboard/post_form.html"
    success_url = reverse_lazy("dashboard:index")

    def form_valid(self, form: PostForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Artigo "{self.object.title}" atualizado com sucesso!')
        return response


class PostDeleteView(DashboardAuthMixin, DeleteView):
    """Delete a blog post."""

    model = Post
    template_name = "dashboard/post_confirm_delete.html"
    success_url = reverse_lazy("dashboard:index")

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        post = self.get_object()
        title = post.title
        messages.success(request, f'Artigo "{title}" excluído com sucesso.')
        return super().delete(request, *args, **kwargs)


class PostToggleStatusView(DashboardAuthMixin, View):
    """Toggle post status between draft and published."""

    def post(self, request: HttpRequest, pk: int) -> HttpResponse:
        post = get_object_or_404(Post, pk=pk)
        if post.status == Post.StatusChoices.PUBLISHED:
            post.status = Post.StatusChoices.DRAFT
            msg = f'Artigo "{post.title}" movido para rascunho.'
        else:
            post.status = Post.StatusChoices.PUBLISHED
            if not post.published_at:
                post.published_at = timezone.now()
            msg = f'Artigo "{post.title}" publicado com sucesso!'

        post.save()
        messages.success(request, msg)
        return redirect("dashboard:index")


class PostPreviewApiView(DashboardAuthMixin, View):
    """API endpoint to render markdown preview dynamically."""

    def post(self, request: HttpRequest) -> JsonResponse:
        content_md = request.POST.get("content_md", "")
        html = render_markdown(content_md)
        return JsonResponse({"html": html})


class TagListView(DashboardAuthMixin, ListView):
    """List all tags with post counts."""

    model = Tag
    template_name = "dashboard/tag_list.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.annotate(posts_count=Count("posts")).order_by("name")


class TagCreateView(DashboardAuthMixin, CreateView):
    """Create a new tag."""

    model = Tag
    form_class = TagForm
    template_name = "dashboard/tag_form.html"
    success_url = reverse_lazy("dashboard:tag_list")

    def form_valid(self, form: TagForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Tag "#{self.object.name}" criada com sucesso!')
        return response


class TagUpdateView(DashboardAuthMixin, UpdateView):
    """Edit an existing tag."""

    model = Tag
    form_class = TagForm
    template_name = "dashboard/tag_form.html"
    success_url = reverse_lazy("dashboard:tag_list")

    def form_valid(self, form: TagForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, f'Tag "#{self.object.name}" atualizada com sucesso!')
        return response


class TagDeleteView(DashboardAuthMixin, DeleteView):
    """Delete a tag."""

    model = Tag
    template_name = "dashboard/tag_confirm_delete.html"
    success_url = reverse_lazy("dashboard:tag_list")

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        tag = self.get_object()
        name = tag.name
        messages.success(request, f'Tag "#{name}" excluída com sucesso.')
        return super().delete(request, *args, **kwargs)


class MediaListView(DashboardAuthMixin, ListView):
    """Media library listing uploaded assets."""

    model = MediaAsset
    template_name = "dashboard/media_list.html"
    context_object_name = "media_assets"
    paginate_by = 24

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["upload_form"] = MediaUploadForm()
        return context


class MediaUploadView(DashboardAuthMixin, CreateView):
    """Upload a new media asset."""

    model = MediaAsset
    form_class = MediaUploadForm
    template_name = "dashboard/media_list.html"
    success_url = reverse_lazy("dashboard:media_list")

    def form_valid(self, form: MediaUploadForm) -> HttpResponse:
        form.instance.uploaded_by = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, "Arquivo de mídia enviado com sucesso!")
        return response

    def form_invalid(self, form: MediaUploadForm) -> HttpResponse:
        messages.error(self.request, "Erro ao enviar arquivo. Verifique os campos.")
        return redirect("dashboard:media_list")


class MediaDeleteView(DashboardAuthMixin, DeleteView):
    """Delete a media asset."""

    model = MediaAsset
    template_name = "dashboard/media_confirm_delete.html"
    success_url = reverse_lazy("dashboard:media_list")

    def delete(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        asset = self.get_object()
        asset.file.delete(save=False)  # Remove file from storage
        messages.success(request, "Arquivo de mídia excluído com sucesso.")
        return super().delete(request, *args, **kwargs)


class SiteConfigUpdateView(DashboardAuthMixin, UpdateView):
    """Edit SiteConfig singleton."""

    model = SiteConfig
    form_class = SiteConfigForm
    template_name = "dashboard/site_config_form.html"
    success_url = reverse_lazy("dashboard:site_config")

    def get_object(self, queryset=None):
        return SiteConfig.get_solo()

    def form_valid(self, form: SiteConfigForm) -> HttpResponse:
        response = super().form_valid(form)
        messages.success(self.request, "Configurações do site salvas com sucesso!")
        return response
