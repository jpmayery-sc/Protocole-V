from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v32math_check import evaluate_v32_math


def evaluate_v32_predictions() -> dict[str, object]:
    math = evaluate_v32_math()
    predictions = [
        {"anomaly": "Muon g-2", "prediction": "non-zero stable correction", "test": "spin precession"},
        {"anomaly": "Mesons B", "prediction": "lepton-dependent corrections", "test": "branching ratios"},
        {"anomaly": "Neutrinos", "prediction": "geometric effective mass", "test": "oscillations"},
        {"anomaly": "Dark matter", "prediction": "Sent(Y)-driven halo behavior", "test": "rotation curves"},
        {"anomaly": "Expansion", "prediction": "K(t)-driven H(t) evolution", "test": "H(z)"},
    ]

    return {
        "section": "V32-PREDICTIONS",
        "prediction_count": len(predictions),
        "predictions": predictions,
        "kty_ansatz_set": math["kty_ansatz_set"],
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v32_kty_integration"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v32predictions_check_{timestamp}.json"
    txt_path = result_dir / f"v32predictions_check_{timestamp}.txt"

    payload = {**evaluate_v32_predictions(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V32 predictions check",
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
    parser = argparse.ArgumentParser(description="Run the V32 predictions check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()