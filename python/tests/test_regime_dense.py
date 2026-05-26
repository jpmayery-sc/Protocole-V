from __future__ import annotations

import pytest

from d1d4_model import density_for_balance, d1_proxy
from regime_dense_check import run_check
from run_regime_physics import run_regime


pytestmark = pytest.mark.dense


def test_dense_launcher_routes_to_d1_and_d4():
    d1_value = d1_proxy(7.4167, 6.0)
    balance_density = density_for_balance(d1_value)
    result = run_regime(
        "dense",
        element="Pb",
        ionization_ev=7.4167,
        principal_n=6.0,
        electron_density_m3=balance_density,
    )

    assert result["dominant_grid"] == "D1 + D4"
    assert result["ok"] is True
    assert result["D1_proxy"] == d1_value
    assert abs(result["dense_balance_gap_ev"]) < 1.0e-12


def test_dense_regime_finds_local_balance(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "supported"
    assert result["launcher_ok"] is True
    assert result["scaling_ok"] is True
    assert result["balance_ok"] is True
    assert result["regime_switch_ok"] is True
    assert result["continuity_ok"] is True
    assert len(result["cases"]) >= 7