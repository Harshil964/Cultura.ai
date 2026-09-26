"""Pydantic contract for a single extracted scene.

This is the shape the extraction LLM call must return for each scene.
Keep it strict (extra="forbid") so a malformed LLM response fails fast
in extraction_service instead of silently corrupting the DB.
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class SceneSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_number: int = Field(..., description="1-indexed order the scene appears in the source screenplay")
    scene_id: str = Field(..., description="Stable id, e.g. SC01")
    heading: str = Field(..., description="Slugline as written in the source, e.g. 'INT. COURTYARD - MORNING'")
    location_name: str = Field(..., description="Human-readable location, e.g. 'Courtyard'")
    time_of_day: Literal["MORNING", "AFTERNOON", "EVENING", "NIGHT", "UNKNOWN"] = "UNKNOWN"
    interior_exterior: Literal["INT", "EXT", "INT/EXT", "UNKNOWN"] = "UNKNOWN"
    character_names: list[str] = Field(default_factory=list, description="Characters present, as named in this scene")
    prop_names: list[str] = Field(default_factory=list, description="Props explicitly mentioned or implied")
    costume_notes: list[str] = Field(default_factory=list, description="Any wardrobe detail mentioned in action lines")
    summary: str = Field(..., description="1-2 sentence plain-language summary of what happens")
    raw_text: str = Field(..., description="The original scene text, verbatim, for traceability")
