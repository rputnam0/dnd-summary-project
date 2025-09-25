"""DSPy signatures describing each analysis sub-task."""

import dspy


class NPCExtractionSig(dspy.Signature):
    """Extract all NPCs with attributes and evidence."""

    transcript = dspy.InputField(desc="Full transcript with timestamps and speakers.")
    avarias_background = dspy.InputField()
    campaign_overview = dspy.InputField()
    npcs_json = dspy.OutputField(desc="JSON list of NPC objects (strict JSON).")


class TimelineRetconSig(dspy.Signature):
    """Build chronological major events with timestamps and impactful retcons."""

    transcript = dspy.InputField()
    avarias_background = dspy.InputField()
    campaign_overview = dspy.InputField()
    events_json = dspy.OutputField(desc="JSON list of Event objects (chronological).")
    retcons_json = dspy.OutputField(desc="JSON list of Retcon objects.")


class PCActionSig(dspy.Signature):
    """Summarise party member actions."""

    transcript = dspy.InputField()
    avarias_background = dspy.InputField()
    campaign_overview = dspy.InputField()
    pcs_json = dspy.OutputField(
        desc="JSON list of CharacterAction objects for PCs: Kaladen, Leopold, Zariel, Cletus, Cyrus."
    )


class DialogueSig(dspy.Signature):
    """Surface key dialogue beats."""

    transcript = dspy.InputField()
    avarias_background = dspy.InputField()
    campaign_overview = dspy.InputField()
    key_dialogue_json = dspy.OutputField(desc="JSON list of DialogueInsight objects.")


class LocObjSig(dspy.Signature):
    """Identify locations and objects of note."""

    transcript = dspy.InputField()
    locations_objects_json = dspy.OutputField(desc="JSON list of LocationObject objects.")


class MechanicsSig(dspy.Signature):
    """Capture important mechanical rulings or rolls."""

    transcript = dspy.InputField()
    mechanics_json = dspy.OutputField(desc="JSON list of MechanicImpact objects.")


class NarrativeBlueprintSig(dspy.Signature):
    """Outline the session's narrative blueprint."""

    transcript = dspy.InputField()
    avarias_background = dspy.InputField()
    campaign_overview = dspy.InputField()
    blueprint_json = dspy.OutputField(desc="JSON NarrativeBlueprint object.")


class CausalitySig(dspy.Signature):
    """Describe causal chains and consequences."""

    transcript = dspy.InputField()
    causality_json = dspy.OutputField(
        desc="JSON list of cause→effect entries: {trigger, reactions, immediate, long_term}."
    )


class VividDescSig(dspy.Signature):
    """Collect vivid sensory descriptions."""

    transcript = dspy.InputField()
    vivid_json = dspy.OutputField(desc="JSON list of DialogueInsight with sensory analysis.")


class ChallengesSig(dspy.Signature):
    """Break down notable challenges."""

    transcript = dspy.InputField()
    challenges_json = dspy.OutputField(desc="JSON list of ChallengeBreakdown objects.")


class RevelationsSig(dspy.Signature):
    """List key revelations or twists."""

    transcript = dspy.InputField()
    revelations_json = dspy.OutputField(desc="JSON list of strings for revelations/twists.")


class HumorSig(dspy.Signature):
    """Capture humour beats."""

    transcript = dspy.InputField()
    humor_json = dspy.OutputField(desc="JSON list of HumorBeat objects.")


class ExcludedOOGSig(dspy.Signature):
    """Track out-of-game sections that were skipped."""

    transcript = dspy.InputField()
    excluded_json = dspy.OutputField(desc="JSON list of brief OOG exclusions and reasons.")
