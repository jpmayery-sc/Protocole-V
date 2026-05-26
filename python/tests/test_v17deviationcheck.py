from __future__ import annotations

from pathlib import Path

from v17deviation_check import run_check


def test_v17deviation_check_classifies_v16_as_supported(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["deviation_class"] == "supported"
    assert result["measured"]["deviation_score"] <= 0.25
    assert result["measured"]["monotone_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()