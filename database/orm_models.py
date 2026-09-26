"""ORM tables for the extraction milestone (Project, Scene, Character,
Location, Costume, Prop). Cultural-plan / adaptation / continuity tables
get added in later milestones on top of this.
"""
from __future__ import annotations

import datetime as dt

from sqlalchemy import String, Text, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.connection import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, default="Untitled Project")
    source_filename: Mapped[str | None] = mapped_column(String, nullable=True)
    raw_screenplay_text: Mapped[str] = mapped_column(Text)

    selected_culture: Mapped[str | None] = mapped_column(String, nullable=True)
    selected_region: Mapped[str | None] = mapped_column(String, nullable=True)
    selected_setting: Mapped[str | None] = mapped_column(String, nullable=True)
    selected_script: Mapped[str | None] = mapped_column(String, nullable=True)

    extraction_status: Mapped[str] = mapped_column(String, default="pending")
    # pending -> extracting -> extracted -> failed

    cultural_plan_status: Mapped[str] = mapped_column(String, default="not_started")
    # not_started -> generating -> awaiting_approval -> approved -> rejected -> failed

    adaptation_status: Mapped[str] = mapped_column(String, default="not_started")
    # not_started -> adapting -> adapted -> failed (requires cultural_plan_status == approved)

    continuity_status: Mapped[str] = mapped_column(String, default="not_started")
    # not_started -> checked

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)

    scenes: Mapped[list["Scene"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    characters: Mapped[list["Character"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    locations: Mapped[list["Location"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    costumes: Mapped[list["Costume"]] = relationship(back_populates="project", cascade="all, delete-orphan")
    props: Mapped[list["Prop"]] = relationship(back_populates="project", cascade="all, delete-orphan")


class Scene(Base):
    __tablename__ = "scenes"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # scene_id, e.g. SC01
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    scene_number: Mapped[int] = mapped_column()
    heading: Mapped[str] = mapped_column(String)
    location_name: Mapped[str] = mapped_column(String)
    time_of_day: Mapped[str] = mapped_column(String, default="UNKNOWN")
    interior_exterior: Mapped[str] = mapped_column(String, default="UNKNOWN")
    character_names: Mapped[list] = mapped_column(JSON, default=list)
    prop_names: Mapped[list] = mapped_column(JSON, default=list)
    costume_notes: Mapped[list] = mapped_column(JSON, default=list)
    summary: Mapped[str] = mapped_column(Text)
    raw_text: Mapped[str] = mapped_column(Text)
    review_status: Mapped[str] = mapped_column(String, default="ok")  # ok | needs_review

    project: Mapped["Project"] = relationship(back_populates="scenes")


class Character(Base):
    __tablename__ = "characters"

    id: Mapped[str] = mapped_column(String, primary_key=True)  # character_id
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    canonical_name: Mapped[str] = mapped_column(String)
    aliases: Mapped[list] = mapped_column(JSON, default=list)
    age: Mapped[str | None] = mapped_column(String, nullable=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    relationships: Mapped[list] = mapped_column(JSON, default=list)
    first_scene_id: Mapped[str | None] = mapped_column(String, nullable=True)
    image_path: Mapped[str | None] = mapped_column(String, nullable=True)
    approved: Mapped[bool] = mapped_column(default=False)

    project: Mapped["Project"] = relationship(back_populates="characters")


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String)
    scene_ids: Mapped[list] = mapped_column(JSON, default=list)

    project: Mapped["Project"] = relationship(back_populates="locations")


class Costume(Base):
    __tablename__ = "costumes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    description: Mapped[str] = mapped_column(Text)
    character_id: Mapped[str | None] = mapped_column(String, nullable=True)
    scene_ids: Mapped[list] = mapped_column(JSON, default=list)

    project: Mapped["Project"] = relationship(back_populates="costumes")


class Prop(Base):
    __tablename__ = "props"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    name: Mapped[str] = mapped_column(String)
    scene_ids: Mapped[list] = mapped_column(JSON, default=list)
    continuity_status: Mapped[str] = mapped_column(String, default="ok")  # ok | warning

    project: Mapped["Project"] = relationship(back_populates="props")


class CulturalPlan(Base):
    """One cultural-adaptation plan per project. Regenerating replaces it
    wholesale (same pattern as extraction) rather than being patched.
    """
    __tablename__ = "cultural_plans"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), unique=True)

    verbal_adaptation: Mapped[dict] = mapped_column(JSON, default=dict)
    non_verbal_adaptation: Mapped[dict] = mapped_column(JSON, default=dict)
    visual_world: Mapped[dict] = mapped_column(JSON, default=dict)
    uncertain_decisions: Mapped[list] = mapped_column(JSON, default=list)
    # each: {"topic": str, "question": str, "options": [str], "confidence": "low"}

    confidence_summary: Mapped[dict] = mapped_column(JSON, default=dict)
    # e.g. {"high": 10, "needs_review": 2}

    approval_status: Mapped[str] = mapped_column(String, default="awaiting_approval")
    # awaiting_approval | approved | rejected

    created_at: Mapped[dt.datetime] = mapped_column(DateTime, default=dt.datetime.utcnow)


class AdaptedScene(Base):
    __tablename__ = "adapted_scenes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    scene_id: Mapped[str] = mapped_column(ForeignKey("scenes.id"))

    adapted_text: Mapped[str] = mapped_column(Text)
    changes: Mapped[list] = mapped_column(JSON, default=list)
    # each: {"aspect": str, "explanation": str}


class ContinuityIssue(Base):
    __tablename__ = "continuity_issues"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"))
    category: Mapped[str] = mapped_column(String)  # character | location | costume | prop | scene_order
    description: Mapped[str] = mapped_column(Text)
    affected_scene_ids: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String, default="open")  # open | resolved
