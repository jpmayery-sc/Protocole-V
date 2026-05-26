from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v34muon_check import evaluate_v34_muon
from v34neutrinos_check import evaluate_v34_neutrinos


def evaluate_v34_tester_summary() -> dict[str, object]:
    muon = evaluate_v34_muon()
    neutrinos = evaluate_v34_neutrinos()

    rejected_reasons = list(muon["rejected_reasons"]) + list(neutrinos["rejected_reasons"])
    if muon["muon_verdict"] == "supported" and neutrinos["neutrino_verdict"] == "supported":
        global_verdict = "supported"
    elif muon["muon_verdict"] == "rejected" and neutrinos["neutrino_verdict"] == "rejected":
        global_verdict = "rejected"
    else:
        global_verdict = "partially_supported"

    return {
        "section": "V34-VERSION-FINALE",
        "muon_verdict": muon["muon_verdict"],
        "neutrino_verdict": neutrinos["neutrino_verdict"],
        "global_verdict": global_verdict,
        "rejected_reasons": rejected_reasons,
        "parameter_ranges": {
            "muon": muon["parameter_ranges"],
            "neutrinos": neutrinos["parameter_ranges"],
        },
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v34_geometric_falsification"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v34tester_summary_check_{timestamp}.json"
    txt_path = result_dir / f"v34tester_summary_check_{timestamp}.txt"

    payload = {**evaluate_v34_tester_summary(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V34 tester summary check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"global_verdict: {payload['global_verdict']}",
                f"rejected_reasons_count: {len(payload['rejected_reasons'])}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V34 tester summary check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()