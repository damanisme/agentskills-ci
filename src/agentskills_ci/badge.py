from __future__ import annotations

from urllib.parse import quote

# Score -> shields.io color, high to low.
_COLOR_THRESHOLDS = (
    (90, "brightgreen"),
    (80, "green"),
    (60, "yellow"),
    (40, "orange"),
    (0, "red"),
)


def badge_color(score: int) -> str:
    """Return the shields.io color for a score using fixed quality bands."""
    for threshold, color in _COLOR_THRESHOLDS:
        if score >= threshold:
            return color
    return "red"


def build_endpoint(score: int, label: str = "skill score") -> dict:
    """Build a shields.io endpoint payload (schemaVersion 1) for a dynamic badge."""
    return {
        "schemaVersion": 1,
        "label": label,
        "message": str(score),
        "color": badge_color(score),
    }


def build_url(score: int, label: str = "skill score") -> str:
    """Build a static shields.io badge image URL."""
    segment = f"{quote(label)}-{score}-{badge_color(score)}"
    return f"https://img.shields.io/badge/{segment}"


def build_markdown(score: int, label: str = "skill score", repo: str | None = None) -> str:
    """Build a Markdown badge snippet, linking back to the repo when provided."""
    image = f"![{label}]({build_url(score, label)})"
    if repo:
        return f"[{image}]({repo})"
    return image
