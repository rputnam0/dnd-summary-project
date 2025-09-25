"""Smoke tests for the DSPy analysis package."""

from dspy_dnd.types import AnalysisArtifact, NPC


def test_analysis_artifact_defaults() -> None:
    npc = NPC(name="Matron Vel")
    artifact = AnalysisArtifact(npcs=[npc])
    assert artifact.npcs[0].name == "Matron Vel"
    assert artifact.pc_actions == []


def test_analysis_artifact_serialises() -> None:
    artifact = AnalysisArtifact()
    dumped = artifact.model_dump()
    assert isinstance(dumped, dict)
    assert "npcs" in dumped
