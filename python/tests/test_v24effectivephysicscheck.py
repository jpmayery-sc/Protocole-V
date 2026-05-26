from __future__ import annotations

from pathlib import Path

from v24effectivephysics_check import run_check


def test_v24_effective_physics_check_reports_supported_relations(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["consistencywithdata"] is True
    assert len(result["effective_relations"]) == 6
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()