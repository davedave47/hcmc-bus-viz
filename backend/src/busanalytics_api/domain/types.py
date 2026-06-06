"""Internal domain types."""
from __future__ import annotations

from enum import Enum


class Theme(str, Enum):
    """The analytical themes the API serves charts for."""

    schools = "schools"
    spatial = "spatial"
    health = "health"


# A chart is addressed by its theme + catalogue slug (e.g. (Theme.health, "5.1")).
ChartKey = tuple[Theme, str]
