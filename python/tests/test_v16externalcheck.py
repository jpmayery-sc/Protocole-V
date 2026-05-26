from __future__ import annotations

from pathlib import Path

from v16external_check import run_check


def test_v16external_check_maps_internal_to_external_observables(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["external_ok"] is True
    assert result["measured"]["consistency_ok"] is True
    assert result["external"]["z_obs"] > result["internal"]["z_mod"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()