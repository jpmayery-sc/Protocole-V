from __future__ import annotations

import pytest

from regime_metal_check import run_check
from run_regime_physics import run_regime


pytestmark = pytest.mark.metal


def test_metal_launcher_routes_to_d1_d2_d4():
    result = run_regime(
        "metal",
        element="Al",
        ionization_ev=5.9858,
        principal_n=3.0,
        electron_density_m3=3.0e28,
    )

    assert result["dominant_grid"] == "D1 + D2 + D4"
    assert result["ok"] is True
    assert result["D4_balance_ev"] > 0.0


def test_metal_regime_stays_in_few_ev_window(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["launcher_ok"] is True
    assert result["d1_dominates_ok"] is True
    assert result["window_ok"] is True
    assert result["nonzero_ok"] is True
    assert len(result["cases"]) >= 4
    assert sum(1 for case in result["cases"] if case["window_ok"]) >= 3