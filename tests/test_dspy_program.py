"""Ensure the SessionAnalyzer module assembles outputs safely."""

from types import SimpleNamespace

import dspy
import pytest

from dspy_dnd import AnalysisArtifact
from dspy_dnd.program import SessionAnalyzer


class FakePredict:
    """Deterministic stand-in for ``dspy.Predict``."""

    def __call__(self, **_: str) -> SimpleNamespace:  # type: ignore[override]
        return SimpleNamespace(
            npcs_json="[]",
            events_json="[]",
            retcons_json="[]",
            pcs_json="[]",
            key_dialogue_json="[]",
            locations_objects_json="[]",
            mechanics_json="[]",
            blueprint_json="{}",
            causality_json="[]",
            vivid_json="[]",
            challenges_json="[]",
            revelations_json="[]",
            humor_json="[]",
            excluded_json="[]",
        )


@pytest.fixture(autouse=True)
def patch_predict(monkeypatch):  # type: ignore[override]
    monkeypatch.setattr(dspy, "Predict", lambda *args, **kwargs: FakePredict())


def test_session_analyzer_returns_analysis_artifact() -> None:
    analyzer = SessionAnalyzer()
    result = analyzer(transcript="", avarias_background="", campaign_overview="")
    artifact = AnalysisArtifact(**result)
    assert artifact.npcs == []
    assert artifact.timeline == []
    assert artifact.mechanics_impact == []
