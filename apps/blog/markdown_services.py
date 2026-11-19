"""Markdown rendering and sanitization services."""

import re

import markdown
import nh3

ALLOWED_TAGS = set(nh3.ALLOWED_TAGS) | {
    "div",
    "span",
    "pre",
    "code",
    "table",
    "thead",
    "tbody",
    "tr",
    "th",
    "td",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "img",
    "hr",
    "del",
    "s",
    "sub",
    "sup",
}

ALLOWED_ATTRIBUTES = {
    "*": {"class", "id", "title"},
    "a": {"href", "title", "target"},
    "img": {"src", "alt", "title", "width", "height", "loading"},
}


def render_markdown(content_md: str) -> str:
    """Render Markdown content to sanitized HTML with Pygments code highlight.

    Extensions enabled per SPEC:
    - fenced_code
    - codehilite
    - tables
    - toc
    - attr_list
    """
    if not content_md:
        return ""

    raw_html = markdown.markdown(
        content_md,
        extensions=[
            "fenced_code",
            "codehilite",
            "tables",
            "toc",
            "attr_list",
        ],
    )

    return nh3.clean(
        raw_html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        link_rel="noopener noreferrer",
    )


def calculate_reading_time(content: str, words_per_minute: int = 200) -> int:
    """Calculate estimated reading time in minutes based on word count.

    Minimum result is 1 minute.
    """
    if not content:
        return 1

    words = re.findall(r"\w+", content)
    word_count = len(words)
    minutes = max(1, round(word_count / words_per_minute))
    return minutes
