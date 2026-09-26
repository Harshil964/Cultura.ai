from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict


class CharacterSchema(BaseModel):
    model_config = ConfigDict(extra="forbid")

    character_id: str = Field(..., description="Stable id, e.g. CHAR_RAVI_001")
    canonical_name: str = Field(..., description="The name to use everywhere downstream")
    aliases: list[str] = Field(default_factory=list, description="Other names/references the same person is called, e.g. 'Son', 'the young man'")
    age: str | None = Field(default=None, description="Age or age range if statable, else null")
    role: str | None = Field(default=None, description="Narrative role, e.g. 'Son', 'Antagonist'")
    relationships: list[str] = Field(default_factory=list, description="Short free-text relationship notes, e.g. 'Father of Ravi'")
    first_scene_id: str | None = Field(default=None, description="scene_id where this character is first introduced")
