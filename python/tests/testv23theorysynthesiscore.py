from __future__ import annotations

from v23theorysynthesis_core import evaluate_v23_theory


def test_v23_theory_synthesis_core_reports_coherent_model():
    result = evaluate_v23_theory()

    assert result["suite"] == "v23theorysynthesissuite"
    assert result["verdict"] == "supported"
    assert result["v23verdict"] == "coherent_model"
    assert result["coherent_model"] is True
    assert result["confidence_level"] == "very_high"
    assert "V23_SCHEMA" in result
    assert "V23_INVARIANTS" in result
    assert "V23_DOMAIN" in result
    assert "V23_OPEN" in result