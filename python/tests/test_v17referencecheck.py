from __future__ import annotations

from pathlib import Path

from v17reference_check import run_check


def test_v17reference_check_loads_the_external_reference(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["measured"]["reference_source"] == "minimal theoretical bounds"
    assert result["measured"]["locked_names"] == ["alpha0", "s_geo", "s_atom", "A_kappa", "p"]
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()