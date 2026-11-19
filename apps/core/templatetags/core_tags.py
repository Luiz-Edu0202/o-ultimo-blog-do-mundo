"""Custom template tags for core and blog."""

from django import template
from django.urls import translate_url

register = template.Library()


@register.simple_tag(takes_context=True)
def change_lang(context, lang_code: str) -> str:
    """Generate the URL for the current page in the target language.

    If a post detail page has an explicit translation post, links directly to it.
    Otherwise, uses Django's translate_url.
    """
    request = context.get("request")
    if not request:
        return "/"

    # If on a post detail page and translation object is in context
    translation = context.get("translation")
    post = context.get("post")
    if translation and post:
        if translation.language == lang_code:
            return translation.get_absolute_url()
        if post.language == lang_code:
            return post.get_absolute_url()

    return translate_url(request.path, lang_code)
