"""Models for core app."""

from django.db import models


class SiteConfig(models.Model):
    """Singleton model for site configuration and metadata."""

    site_title_pt = models.CharField(
        max_length=200,
        default="O Último Blog do Mundo",
        verbose_name="Título do Site (PT)",
    )
    site_title_en = models.CharField(
        max_length=200,
        default="The Last Blog in the World",
        verbose_name="Site Title (EN)",
    )
    tagline_pt = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Subtítulo / Tagline (PT)",
    )
    tagline_en = models.CharField(
        max_length=255,
        blank=True,
        verbose_name="Subtítulo / Tagline (EN)",
    )
    about_pt = models.TextField(
        blank=True,
        verbose_name="Sobre (PT)",
    )
    about_en = models.TextField(
        blank=True,
        verbose_name="About (EN)",
    )
    email = models.EmailField(blank=True, verbose_name="E-mail")
    github_url = models.URLField(blank=True, verbose_name="GitHub URL")
    linkedin_url = models.URLField(blank=True, verbose_name="LinkedIn URL")
    portfolio_url = models.URLField(blank=True, verbose_name="Portfolio URL")
    default_og_image = models.FileField(
        upload_to="site/",
        blank=True,
        null=True,
        verbose_name="Imagem OpenGraph padrão",
    )

    class Meta:
        verbose_name = "Configuração do Site"
        verbose_name_plural = "Configurações do Site"

    def __str__(self) -> str:
        return self.site_title_pt

    def save(self, *args, **kwargs):
        """Enforce singleton: always save as primary key 1."""
        self.pk = 1
        kwargs.pop("force_insert", None)
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls) -> "SiteConfig":
        """Get or create the singleton instance."""
        obj, _ = cls.objects.get_or_create(
            pk=1,
            defaults={
                "site_title_pt": "O Último Blog do Mundo",
                "site_title_en": "The Last Blog in the World",
            },
        )
        return obj
