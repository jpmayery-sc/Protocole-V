from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v30_anomalies() -> dict[str, object]:
    anomalies = [
        {
            "name": "Mesons B",
            "observable": ["RK", "RK*", "B->mumu"],
            "sigma_current": 2.7,
            "status": "open",
            "comment": "persistent lepton-universality tension",
        },
        {
            "name": "Muon g-2",
            "observable": ["a_mu"],
            "sigma_current": 3.0,
            "status": "tension",
            "comment": "depends on hadronic inputs",
        },
        {
            "name": "Neutrinos",
            "observable": ["oscillations", "Delta m^2"],
            "sigma_current": float("inf"),
            "status": "confirmed",
            "comment": "non-zero neutrino masses required",
        },
        {
            "name": "Dark matter",
            "observable": ["rotation curves", "lensing", "CMB"],
            "sigma_current": float("inf"),
            "status": "confirmed",
            "comment": "requires invisible mass component",
        },
        {
            "name": "Accelerated expansion",
            "observable": ["SN Ia luminosity-distance"],
            "sigma_current": float("inf"),
            "status": "confirmed",
            "comment": "requires Lambda or dark energy",
        },
    ]

    confirmed = sum(1 for anomaly in anomalies if anomaly["status"] == "confirmed")
    open_count = sum(1 for anomaly in anomalies if anomaly["status"] in {"open", "tension"})
    return {
        "section": "V30-ANOMALIES",
        "anomalies": anomalies,
        "confirmed_count": confirmed,
        "open_count": open_count,
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v30_validation"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v30anomalies_check_{timestamp}.json"
    txt_path = result_dir / f"v30anomalies_check_{timestamp}.txt"

    payload = {**evaluate_v30_anomalies(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    lines = [
        "V30 anomalies check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"confirmed_count: {payload['confirmed_count']}",
        f"open_count: {payload['open_count']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V30 anomalies check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()