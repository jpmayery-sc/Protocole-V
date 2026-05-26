from __future__ import annotations

from pathlib import Path

from v8rayon_check import run_check


def test_v8rayon_check_supports_atomic_radius(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["order_ok"] is True
    assert result["measured"]["pb_soft_ok"] is True
    assert result["measured"]["span_ok"] is True
    assert result["measured"]["radius_band_ok"] is True
    assert result["measured"]["minimum_ok"] is True
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v8rayon_check_orders_h_he_fe(tmp_path):
    result = run_check(tmp_path)

    species = {entry["name"]: entry for entry in result["species_results"]}
    assert species["H"]["effective_radius"] < species["He"]["effective_radius"] < species["Fe"]["effective_radius"]
    assert species["Pb"]["gradient_min"] < species["Fe"]["gradient_min"]