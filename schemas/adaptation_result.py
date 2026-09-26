from __future__ import annotations

from pydantic import BaseModel, Field, ConfigDict


class SceneChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    aspect: str = Field(..., description="What changed, e.g. 'Kinship + respect'")
    explanation: str = Field(..., description="One sentence: why this change was made")


class AdaptedSceneResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scene_id: str
    adapted_text: str = Field(..., description="The scene's dialogue/action rewritten per the cultural plan")
    changes: list[SceneChange] = Field(default_factory=list)


class AdaptationResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    scenes: list[AdaptedSceneResult]
