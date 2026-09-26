"""Schemas that don't warrant their own file yet: locations, costumes, props,
and the top-level envelope the extraction agent must return.

Named adaptation.py to match the assignment's existing `schemas/adaptation.py`
slot; cultural-adaptation-specific schemas get added here in a later milestone.
"""
from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict

from schemas.scene import SceneSchema
from schemas.character import CharacterSchema


class LocationSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location_id: str
    name: str
    scene_ids: list[str] = Field(default_factory=list)


class CostumeSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    costume_id: str
    description: str
    character_id: str | None = None
    scene_ids: list[str] = Field(default_factory=list)


class PropSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prop_id: str
    name: str
    scene_ids: list[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """Top-level contract the extraction agent must return for one screenplay."""

    model_config = ConfigDict(extra="forbid")

    scenes: list[SceneSchema]
    characters: list[CharacterSchema]
    locations: list[LocationSchema]
    costumes: list[CostumeSchema] = Field(default_factory=list)
    props: list[PropSchema] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list, description="Anything the model was unsure about")
