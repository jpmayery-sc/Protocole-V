from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v35muon_scan_check import evaluate_v35_muon
from v35neutrino_scan_check import evaluate_v35_neutrinos


def evaluate_v35_tester_summary() -> dict[str, object]:
    muon = evaluate_v35_muon()
    neutrinos = evaluate_v35_neutrinos()

    if muon["muon_verdict"] == "supported" and neutrinos["neutrino_verdict"] == "supported":
        global_verdict = "supported"
    elif muon["muon_verdict"] == "rejected" and neutrinos["neutrino_verdict"] == "rejected":
        global_verdict = "rejected"
    else:
        global_verdict = "partially_supported"

    best_points = {
        "muon": muon["best_muon_point"],
        "neutrinos": neutrinos["best_neutrino_point"],
    }

    scan_statistics = {
        "muon_scan_count": muon["scan_count"],
        "neutrino_scan_count": neutrinos["scan_count"],
    }

    return {
        "section": "V35-VERSION-FINALE",
        "muon_verdict": muon["muon_verdict"],
        "neutrino_verdict": neutrinos["neutrino_verdict"],
        "global_verdict": global_verdict,
        "best_points": best_points,
        "scan_statistics": scan_statistics,
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v35_numeric_calibration"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v35tester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v35tester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v35_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V35 tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"global_verdict: {payload['global_verdict']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V35 tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()