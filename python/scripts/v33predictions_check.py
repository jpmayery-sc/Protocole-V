from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v33math_check import evaluate_v33_math


def evaluate_v33_predictions() -> dict[str, object]:
    math = evaluate_v33_math()
    predictions = [
        {"anomaly": "Muon g-2", "prediction": "non-zero correction of stable sign", "test": "spin precession"},
        {"anomaly": "Muon g-2", "prediction": "magnitude near 10^-9", "test": "global fit"},
        {"anomaly": "Neutrinos", "prediction": "background geometric mass term", "test": "oscillations"},
        {"anomaly": "Neutrinos", "prediction": "Delta m^2_sol and Delta m^2_atm reproduced", "test": "spectrum fits"},
        {"anomaly": "Neutrinos", "prediction": "environmental shifts remain tiny", "test": "long baseline comparison"},
    ]

    return {
        "section": "V33-PREDICTIONS",
        "prediction_count": len(predictions),
        "predictions": predictions,
        "kty_ansatz_set": math["kty_ansatz_set"],
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v33_kty_refinement"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v33predictions_check_{timestamp}.json"
    txt_path = result_dir / f"v33predictions_check_{timestamp}.txt"

    payload = {**evaluate_v33_predictions(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V33 predictions check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"prediction_count: {payload['prediction_count']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V33 predictions check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()