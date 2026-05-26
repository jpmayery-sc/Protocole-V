from __future__ import annotations

import pytest

from regime_flow_check import run_check


pytestmark = pytest.mark.flow


def test_regime_flow_supports_all_four_roles(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["launcher_ok"] is True
    assert result["pressure_scaling_ok"] is True
    assert result["atomic_ok"] is True
    assert result["metal_ok"] is True
    assert result["lanthanide_ok"] is True
    assert result["dense_ok"] is True
    assert result["budget_ok"] is True
    assert len(result["cases"]) == 4

    cases = {case["label"]: case for case in result["cases"]}
    assert cases["A"]["launcher_grid"] == "D1"
    assert cases["B"]["launcher_grid"] == "D1 + D2 + D4"
    assert cases["C"]["launcher_grid"] == "D1 + D3"
    assert cases["D"]["launcher_grid"] == "D1 + D4"
    assert cases["A"]["D1_share"] > cases["A"]["D4_share"]
    assert cases["B"]["D2_share"] > 0.0
    assert cases["C"]["D3_share"] > 0.2
    assert cases["D"]["D4_share"] > 0.9