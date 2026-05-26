from __future__ import annotations

import pytest

from regime_atomique_check import run_check
from run_regime_physics import run_regime


pytestmark = pytest.mark.atomique


def test_atomic_launcher_routes_to_d1():
    result = run_regime(
        "atomique",
        element="H",
        ionization_ev=13.6,
        principal_n=1.0,
        electron_density_m3=1.0e20,
    )

    assert result["dominant_grid"] == "D1"
    assert result["ok"] is True


def test_atomic_regime_stays_negligible(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["launcher_ok"] is True
    assert result["d1_dominates_ok"] is True
    assert result["negligible_ok"] is True
    assert result["pressure_scaling_ok"] is True
    assert len(result["cases"]) >= 4
    assert max(case["D4_over_D1"] for case in result["cases"]) < 5.0e-4