"""Composable DSPy modules for session analysis."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

import dspy

from . import signatures as sig
from .types import AnalysisArtifact, NarrativeBlueprint


def _safe_json_load(payload: str, default: Any) -> Any:
    """Parse JSON strings produced by language models with resilience."""

    if not payload:
        return default
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        return default


class NPCExtractor(dspy.Module):
    """Module wrapper that converts signature output into Python objects."""

    def __init__(self) -> None:
        super().__init__()
        self.predict = dspy.Predict(sig.NPCExtractionSig)

    def forward(self, transcript: str, avarias_background: str, campaign_overview: str) -> List[Dict]:
        response = self.predict(
            transcript=transcript,
            avarias_background=avarias_background,
            campaign_overview=campaign_overview,
        )
        return _safe_json_load(response.npcs_json, default=[])


class SessionAnalyzer(dspy.Module):
    """Call each sub-module and consolidate the structured artifact."""

    def __init__(self) -> None:
        super().__init__()
        self.npcs = NPCExtractor()
        self.timeline = dspy.Predict(sig.TimelineRetconSig)
        self.pcs = dspy.Predict(sig.PCActionSig)
        self.dialogue = dspy.Predict(sig.DialogueSig)
        self.locobj = dspy.Predict(sig.LocObjSig)
        self.mechanics = dspy.Predict(sig.MechanicsSig)
        self.blueprint = dspy.Predict(sig.NarrativeBlueprintSig)
        self.causality = dspy.Predict(sig.CausalitySig)
        self.vivid = dspy.Predict(sig.VividDescSig)
        self.challenges = dspy.Predict(sig.ChallengesSig)
        self.revelations = dspy.Predict(sig.RevelationsSig)
        self.humor = dspy.Predict(sig.HumorSig)
        self.excluded = dspy.Predict(sig.ExcludedOOGSig)

    def forward(
        self, transcript: str, avarias_background: str, campaign_overview: str
    ) -> Dict[str, Any]:
        """Execute each module and validate the combined JSON payload."""

        npcs = self.npcs(transcript, avarias_background, campaign_overview)
        timeline = self.timeline(
            transcript=transcript,
            avarias_background=avarias_background,
            campaign_overview=campaign_overview,
        )
        pcs = self.pcs(
            transcript=transcript,
            avarias_background=avarias_background,
            campaign_overview=campaign_overview,
        )
        dialogue = self.dialogue(
            transcript=transcript,
            avarias_background=avarias_background,
            campaign_overview=campaign_overview,
        )
        locobj = self.locobj(transcript=transcript)
        mechanics = self.mechanics(transcript=transcript)
        blueprint = self.blueprint(
            transcript=transcript,
            avarias_background=avarias_background,
            campaign_overview=campaign_overview,
        )
        causality = self.causality(transcript=transcript)
        vivid = self.vivid(transcript=transcript)
        challenges = self.challenges(transcript=transcript)
        revelations = self.revelations(transcript=transcript)
        humor = self.humor(transcript=transcript)
        excluded = self.excluded(transcript=transcript)

        artifact = AnalysisArtifact(
            session_overview={},
            pc_actions=_safe_json_load(pcs.pcs_json, default=[]),
            npcs=npcs,
            timeline=_safe_json_load(timeline.events_json, default=[]),
            retcons=_safe_json_load(timeline.retcons_json, default=[]),
            key_dialogue=_safe_json_load(dialogue.key_dialogue_json, default=[]),
            locations_objects=_safe_json_load(locobj.locations_objects_json, default=[]),
            mechanics_impact=_safe_json_load(mechanics.mechanics_json, default=[]),
            narrative_blueprint=_parse_blueprint(blueprint.blueprint_json),
            relationships=[],
            causality_notes=_safe_json_load(causality.causality_json, default=[]),
            vivid_descriptions=_safe_json_load(vivid.vivid_json, default=[]),
            challenges=_safe_json_load(challenges.challenges_json, default=[]),
            revelations_twists=_safe_json_load(revelations.revelations_json, default=[]),
            humor_beats=_safe_json_load(humor.humor_json, default=[]),
            excluded_oog=_safe_json_load(excluded.excluded_json, default=[]),
        )
        return artifact.model_dump()


def _parse_blueprint(payload: str) -> Optional[NarrativeBlueprint]:
    """Parse a narrative blueprint JSON string."""

    if not payload:
        return None
    try:
        data = json.loads(payload)
    except json.JSONDecodeError:
        return None
    try:
        return NarrativeBlueprint.model_validate(data)
    except Exception:
        return None
