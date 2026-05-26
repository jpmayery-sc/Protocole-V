from __future__ import annotations

import json
from pathlib import Path

import pytest

from ecgp_bench import load_trials, run_bench


pytestmark = pytest.mark.flow


def test_load_trials_accepts_demo_dataset():
    root = Path(__file__).resolve().parents[1]
    input_path = root / "data" / "ecgp_trials_demo_control.json"

    trials, metadata = load_trials(input_path)

    assert metadata["status"] == "demo_control"
    assert len(trials) == 6
    assert trials[0].material == "cu"


def test_run_bench_builds_report(tmp_path):
    input_path = tmp_path / "ecgp_trials.json"
    output_dir = tmp_path / "results"

    payload = {
        "schema_version": 1,
        "status": "real",
        "trials": [
            {
                "trial_id": "cu-1",
                "material": "cu",
                "frequency_hz": 1000000,
                "measured_fidelity": 0.976,
                "control_fidelity": 0.971,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "straight",
            },
            {
                "trial_id": "cu-2",
                "material": "cu",
                "frequency_hz": 5000000,
                "measured_fidelity": 0.977,
                "control_fidelity": 0.971,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "straight",
            },
            {
                "trial_id": "fe-1",
                "material": "fe",
                "frequency_hz": 1000000,
                "measured_fidelity": 0.972,
                "control_fidelity": 0.920,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "spiral",
            },
            {
                "trial_id": "fe-2",
                "material": "fe",
                "frequency_hz": 5000000,
                "measured_fidelity": 0.973,
                "control_fidelity": 0.920,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "spiral",
            },
        ],
    }
    input_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    result = run_bench(input_path, output_dir)

    assert result["overall_verdict"] == "supported"
    assert result["trial_count"] == 4
    assert result["material_spread"] > 0.02
    assert Path(result["json_path"]).exists()
    assert Path(result["txt_path"]).exists()


def test_run_bench_rejects_flat_control(tmp_path):
    input_path = tmp_path / "flat.json"
    output_dir = tmp_path / "results"

    payload = {
        "schema_version": 1,
        "status": "real",
        "trials": [
            {
                "trial_id": "a-1",
                "material": "cu",
                "frequency_hz": 1000000,
                "measured_fidelity": 0.971,
                "control_fidelity": 0.969,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "straight",
            },
            {
                "trial_id": "a-2",
                "material": "al",
                "frequency_hz": 5000000,
                "measured_fidelity": 0.962,
                "control_fidelity": 0.960,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "straight",
            },
            {
                "trial_id": "a-3",
                "material": "fe",
                "frequency_hz": 1000000,
                "measured_fidelity": 0.953,
                "control_fidelity": 0.951,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "spiral",
            },
            {
                "trial_id": "a-4",
                "material": "fe",
                "frequency_hz": 5000000,
                "measured_fidelity": 0.954,
                "control_fidelity": 0.952,
                "loss_db": 1.0,
                "temperature_k": 295.0,
                "geometry": "spiral",
            },
        ],
    }
    input_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    result = run_bench(input_path, output_dir)

    assert result["overall_verdict"] == "rejected"
    assert result["delta_spread"] <= 0.005
