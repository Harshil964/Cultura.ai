"""Contract the cultural_agent must return: a plan covering verbal,
non-verbal, and visual-world adaptation, plus explicit uncertain decisions
that need a human's eyes before adaptation runs.
"""
from __future__ import annotations

from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class UncertainDecision(BaseModel):
    model_config = ConfigDict(extra="forbid")

    topic: str = Field(..., description="Short label, e.g. 'Honorific for elder brother'")
    question: str = Field(..., description="What exactly is unclear or ambiguous")
    options: list[str] = Field(default_factory=list, description="Plausible choices, if any")
    confidence: Literal["low", "medium"] = "low"


class CulturalPlanResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # Each dict is topic -> short prescriptive note, e.g.
    # {"dialect": "Marwari-inflected Hindi, softened for on-screen readability", ...}
    verbal_adaptation: dict[str, str] = Field(default_factory=dict)
    non_verbal_adaptation: dict[str, str] = Field(default_factory=dict)
    visual_world: dict[str, str] = Field(default_factory=dict)

    uncertain_decisions: list[UncertainDecision] = Field(default_factory=list)
    high_confidence_count: int = Field(..., description="How many total decisions above were made with high confidence")
