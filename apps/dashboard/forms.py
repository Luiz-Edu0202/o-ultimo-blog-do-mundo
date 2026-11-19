"""Forms for dashboard authentication, 2FA, posts, tags, media, and site configuration."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from apps.blog.models import MediaAsset, Post, Tag
from apps.core.models import SiteConfig


class DashboardLoginForm(AuthenticationForm):
    """Custom styled login form for the dashboard."""

    username = forms.CharField(
        label="Usuário",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nome de usuário",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Senha",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Sua senha",
            }
        ),
    )


class TwoFactorVerifyForm(forms.Form):
    """Form to submit 6-digit TOTP token."""

    token = forms.CharField(
        label="Código de Autenticação (6 dígitos)",
        max_length=6,
        min_length=6,
        widget=forms.TextInput(
            attrs={
                "class": "form-control form-control-lg text-center letter-spacing-2",
                "placeholder": "123456",
                "autocomplete": "one-time-code",
                "inputmode": "numeric",
                "pattern": "[0-9]{6}",
                "autofocus": True,
            }
        ),
    )

    def clean_token(self):
        token = self.cleaned_data.get("token", "").strip()
        if not token.isdigit():
            raise ValidationError("O código deve conter apenas dígitos numéricos.")
        return token


class PostForm(forms.ModelForm):
    """Form for creating and editing blog posts."""

    class Meta:
        model = Post
        fields = [
            "title",
            "slug",
            "summary",
            "content_md",
            "cover_image",
            "tags",
            "language",
            "translation_of",
            "status",
            "meta_description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Título do artigo"}
            ),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "slug-do-artigo (deixe em branco para gerar do título)",
                }
            ),
            "summary": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3,
                    "placeholder": "Resumo curto para listagens e SEO",
                }
            ),
            "content_md": forms.Textarea(
                attrs={
                    "class": "form-control font-monospace",
                    "rows": 18,
                    "id": "content_md_editor",
                    "placeholder": "# Escreva seu artigo em Markdown aqui...",
                }
            ),
            "cover_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "tags": forms.SelectMultiple(attrs={"class": "form-select", "size": "5"}),
            "language": forms.Select(attrs={"class": "form-select"}),
            "translation_of": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "meta_description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Meta descrição para motores de busca (máx 160 caracteres)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filter translation_of queryset to other posts
        if self.instance and self.instance.pk:
            self.fields["translation_of"].queryset = Post.objects.exclude(pk=self.instance.pk)
        self.fields["slug"].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        title = self.cleaned_data.get("title", "")
        if not slug and title:
            slug = slugify(title)[:200]
        return slug


class TagForm(forms.ModelForm):
    """Form for creating and editing tags."""

    class Meta:
        model = Tag
        fields = ["name", "slug"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da tag"}),
            "slug": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "slug-da-tag (deixe em branco para gerar do nome)",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["slug"].required = False

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        name = self.cleaned_data.get("name", "")
        if not slug and name:
            slug = slugify(name)[:50]
        return slug


class MediaUploadForm(forms.ModelForm):
    """Form for uploading media assets."""

    class Meta:
        model = MediaAsset
        fields = ["file", "alt_text"]
        widgets = {
            "file": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "alt_text": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Descrição da imagem para acessibilidade",
                }
            ),
        }


class SiteConfigForm(forms.ModelForm):
    """Form for editing site configuration in PT and EN."""

    class Meta:
        model = SiteConfig
        fields = [
            "site_title_pt",
            "site_title_en",
            "tagline_pt",
            "tagline_en",
            "about_pt",
            "about_en",
            "email",
            "github_url",
            "linkedin_url",
            "portfolio_url",
            "default_og_image",
        ]
        widgets = {
            "site_title_pt": forms.TextInput(attrs={"class": "form-control"}),
            "site_title_en": forms.TextInput(attrs={"class": "form-control"}),
            "tagline_pt": forms.TextInput(attrs={"class": "form-control"}),
            "tagline_en": forms.TextInput(attrs={"class": "form-control"}),
            "about_pt": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "about_en": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "github_url": forms.URLInput(attrs={"class": "form-control"}),
            "linkedin_url": forms.URLInput(attrs={"class": "form-control"}),
            "portfolio_url": forms.URLInput(attrs={"class": "form-control"}),
            "default_og_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }


class DashboardPasswordChangeForm(PasswordChangeForm):
    """Custom styled password change form."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"
