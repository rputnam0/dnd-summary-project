"""Pydantic models describing structured analysis artifacts."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Quote(BaseModel):
    """A grounded quote with optional provenance."""

    timestamp: Optional[str] = Field(
        default=None, description="Timestamp in HH:MM or HH:MM:SS format if available."
    )
    speaker: Optional[str] = Field(default=None, description="Speaker name or role.")
    text: str = Field(description="Verbatim or lightly edited quote text.")


class Relationship(BaseModel):
    """A relationship between two characters."""

    with_name: str = Field(description="Counterparty name (PC or NPC).")
    relation: Literal[
        "ally",
        "enemy",
        "neutral",
        "unknown",
        "rival",
        "patron",
        "subordinate",
        "superior",
    ] = Field(description="High-level relationship type.")
    evidence: List[Quote] = Field(default_factory=list, description="Supporting evidence quotes.")


class NPC(BaseModel):
    """Information about a non-player character."""

    name: str
    aliases: List[str] = Field(default_factory=list)
    first_appearance_ts: Optional[str] = None
    description: Optional[str] = None
    role: Optional[str] = None
    objectives: Optional[str] = None
    key_dialogue: List[Quote] = Field(default_factory=list)
    significance_immediate: Optional[str] = None
    significance_campaign: Optional[str] = None
    foreshadowing: Optional[str] = None
    relationships: List[Relationship] = Field(default_factory=list)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)


class LocationObject(BaseModel):
    """Representation of a location or object of interest."""

    type: Literal["location", "object"]
    name: str
    description: Optional[str] = None
    function_purpose: Optional[str] = None
    narrative_significance: Optional[str] = None
    first_appearance_ts: Optional[str] = None


class MechanicImpact(BaseModel):
    """A notable rules interaction or mechanical beat."""

    rule: str
    context: str
    consequence: str
    timestamp: Optional[str] = None


class CharacterAction(BaseModel):
    """Summary of a player character's actions and growth."""

    character: str
    key_actions: List[str] = Field(default_factory=list)
    decision_making: Optional[str] = None
    development: Optional[str] = None
    challenges: List[str] = Field(default_factory=list)
    successes: List[str] = Field(default_factory=list)
    failures: List[str] = Field(default_factory=list)


class Event(BaseModel):
    """Chronological event in the session timeline."""

    timestamp: Optional[str] = None
    title: str
    description: str
    present_pcs: List[str] = Field(default_factory=list)
    present_npcs: List[str] = Field(default_factory=list)


class Retcon(BaseModel):
    """A retcon, clarification, or similar adjustment."""

    original_quote: Quote
    retcon_quote: Quote
    who: str
    reason: Optional[str] = None
    narrative_impact: str
    adjustment_type: Literal["true_retcon", "clarification", "expansion", "perspective_shift"]
    intentionality: Optional[str] = None
    affects_event_title: Optional[str] = Field(
        default=None, description="Name of the event that should be adjusted."
    )


class DialogueInsight(BaseModel):
    """A noteworthy dialogue beat with categorisation."""

    quote: Quote
    category: Literal["character", "plot", "theme", "emotion"]
    why_significant: str
    edits_noted: Optional[str] = None


class ChallengeBreakdown(BaseModel):
    """Detailed look at a combat, puzzle, or other challenge."""

    name: str
    nature: str
    tactics: str
    successes: List[str]
    failures: List[str]
    consequences: str


class NarrativeBlueprint(BaseModel):
    """High-level narrative arc scaffold for the session."""

    initial_goals: str
    evolving_goals: str
    goal_pursuit_effectiveness: str
    arc: List[Dict] = Field(
        description="Ordered sequence of narrative stages with contextual metadata."
    )
    climax: str
    unresolved_questions: Dict[str, List[str]] = Field(
        description="Outstanding questions bucketed by type."
    )
    themes: List[Dict] = Field(description="Session themes with evidence.")


class HumorBeat(BaseModel):
    """Moments of levity worth preserving."""

    quote_or_desc: Quote
    context: str
    why_funny: str
    type_of_humor: str
    impact: str
    integration_suggestion: Optional[str] = None


class AnalysisArtifact(BaseModel):
    """Top-level structured payload for a processed session."""

    session_overview: Dict = Field(default_factory=dict)
    pc_actions: List[CharacterAction] = Field(default_factory=list)
    npcs: List[NPC] = Field(default_factory=list)
    timeline: List[Event] = Field(default_factory=list)
    retcons: List[Retcon] = Field(default_factory=list)
    key_dialogue: List[DialogueInsight] = Field(default_factory=list)
    locations_objects: List[LocationObject] = Field(default_factory=list)
    mechanics_impact: List[MechanicImpact] = Field(default_factory=list)
    narrative_blueprint: Optional[NarrativeBlueprint] = None
    relationships: List[Relationship] = Field(default_factory=list)
    causality_notes: List[Dict] = Field(default_factory=list)
    vivid_descriptions: List[DialogueInsight] = Field(default_factory=list)
    challenges: List[ChallengeBreakdown] = Field(default_factory=list)
    revelations_twists: List[str] = Field(default_factory=list)
    humor_beats: List[HumorBeat] = Field(default_factory=list)
    excluded_oog: List[str] = Field(default_factory=list)
