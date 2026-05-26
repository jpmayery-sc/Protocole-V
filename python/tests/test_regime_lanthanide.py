from __future__ import annotations

import pytest

from regime_lanthanide_check import run_check
from run_regime_physics import run_regime


pytestmark = pytest.mark.lanthanide


def test_lanthanide_launcher_requires_d3():
    result = run_regime(
        "lanthanide",
        element="Ce",
        ionization_ev=5.5387,
        principal_n=4.0,
        electron_density_m3=4.0e28,
    )

    assert result["dominant_grid"] == "D1 + D3"
    assert result["ok"] is True


def test_lanthanide_regime_refuses_d1_only_collapse(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["launcher_ok"] is True
    assert result["d3_required_ok"] is True
    assert result["non_collapse_ok"] is True
    assert result["balance_band_ok"] is True
    assert len(result["cases"]) >= 5