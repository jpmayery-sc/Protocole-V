from __future__ import annotations

from pathlib import Path

from v11falsifier_check import run_check


def test_v11falsifier_check_supports_v11_within_bounds(tmp_path):
    result = run_check(tmp_path)

    assert result["verdict"] == "conforme"
    assert result["measured"]["supported_count"] == 4
    assert result["measured"]["falsified_count"] == 0
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_v11falsifier_check_rejects_out_of_bounds_series():
    from v11falsifier_check import check_series

    check = check_series([1e-6, 2e-6, 3e-6], 1e-7, 2e-6)
    assert check["verdict"] == "falsifie"