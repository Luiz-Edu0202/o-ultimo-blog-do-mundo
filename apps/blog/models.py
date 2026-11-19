"""Models for the blog app."""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from apps.blog.markdown_services import calculate_reading_time, render_markdown


class Tag(models.Model):
    """Tag for classifying posts."""

    name = models.CharField(max_length=50, unique=True, verbose_name="Nome")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="Slug")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        return reverse("blog:tag_posts", kwargs={"slug": self.slug})


class Post(models.Model):
    """Article post written in Markdown with HTML caching and i18n support."""

    class LanguageChoices(models.TextChoices):
        PT_BR = "pt-br", "Português"
        EN = "en", "English"

    class StatusChoices(models.TextChoices):
        DRAFT = "draft", "Rascunho"
        PUBLISHED = "published", "Publicado"

    title = models.CharField(max_length=200, verbose_name="Título")
    slug = models.SlugField(max_length=200, verbose_name="Slug")
    summary = models.TextField(blank=True, verbose_name="Resumo")
    content_md = models.TextField(verbose_name="Conteúdo Markdown")
    content_html = models.TextField(blank=True, verbose_name="Conteúdo HTML")
    cover_image = models.FileField(
        upload_to="covers/",
        blank=True,
        null=True,
        verbose_name="Imagem de Capa",
    )
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
        verbose_name="Tags",
    )
    language = models.CharField(
        max_length=10,
        choices=LanguageChoices.choices,
        default=LanguageChoices.PT_BR,
        verbose_name="Idioma",
    )
    translation_of = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="translations",
        verbose_name="Tradução de",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        verbose_name="Status",
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Publicado em",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name="Meta Description",
    )
    reading_time = models.PositiveIntegerField(
        default=1,
        verbose_name="Tempo de Leitura (minutos)",
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-published_at", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["slug", "language"],
                name="unique_post_slug_per_language",
            )
        ]

    def __str__(self) -> str:
        return f"{self.title} ({self.get_language_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)[:200]

        # Always re-generate HTML from markdown and update reading time
        self.content_html = render_markdown(self.content_md)
        self.reading_time = calculate_reading_time(self.content_md)

        # Auto-set published_at when published
        if self.status == self.StatusChoices.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        self.full_clean()
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        from django.utils.translation import override

        with override(self.language):
            return reverse("blog:post_detail", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()

        # SPEC: Tradução só aponta para post de outro idioma
        if self.translation_of:
            if self.translation_of_id == self.pk:
                msg = "Um post não pode ser tradução de si mesmo."
                raise ValidationError({"translation_of": msg})
            if self.translation_of.language == self.language:
                raise ValidationError(
                    {"translation_of": "A tradução deve apontar para um post em idioma diferente."}
                )

        # SPEC: Post publicado exige published_at
        if self.status == self.StatusChoices.PUBLISHED and not self.published_at:
            self.published_at = timezone.now()


class MediaAsset(models.Model):
    """Uploaded media file asset with mandatory alt text for accessibility."""

    file = models.FileField(upload_to="media_assets/", verbose_name="Arquivo")
    alt_text = models.CharField(max_length=255, verbose_name="Texto alternativo (alt)")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Enviado em")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Enviado por",
    )

    class Meta:
        verbose_name = "Mídia"
        verbose_name_plural = "Mídias"
        ordering = ["-uploaded_at"]

    def __str__(self) -> str:
        return self.alt_text or self.file.name
