from __future__ import annotations

from pathlib import Path

from v20verdict_check import run_check


def test_v20verdict_check_reports_global_coherence(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict_global"] == "supported"
    assert result["structure_detectee"] == "coherente"
    assert result["niveau_de_confiance"] == "haute"
    assert result["v20_geo"]["verdict"] == "supported"
    assert result["v20_torsion"]["verdict"] == "supported"
    assert result["v20_hierarchy"]["verdict"] == "supported"
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()