"""Chart response DTO.

One shape for every chart endpoint: a computed action ``title`` + ``subtitle``
(the A2 invariant — derived from the warehouse, never hard-coded), the row
``series`` the frontend renders, ``encoding`` hints, and chart-specific ``meta``
(annotations, notes). The frontend builds the Plotly figure from this.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ChartResponse(BaseModel):
    theme: str
    slug: str
    title: str
    subtitle: str
    series: list[dict[str, Any]]
    encoding: dict[str, Any] = Field(default_factory=dict)
    meta: dict[str, Any] = Field(default_factory=dict)
