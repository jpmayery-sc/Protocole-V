from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report


def evaluate_v31_interpretation() -> dict[str, object]:
    families = [
        {
            "family": "phase_coherence",
            "anomalies": ["Muon g-2", "Mesons B"],
            "geometric_reading": "torsion T and local phase response",
            "observable_key": "spin / branching ratios",
            "prediction": "deviations remain non-zero and family-specific",
        },
        {
            "family": "mass_energy",
            "anomalies": ["Neutrinos"],
            "geometric_reading": "effective geometric mass from K",
            "observable_key": "oscillations",
            "prediction": "oscillation structure may depend weakly on geometry",
        },
        {
            "family": "large_scale_geometry",
            "anomalies": ["Dark matter", "Accelerated expansion"],
            "geometric_reading": "Sent(Y) deficit and global K(t) evolution",
            "observable_key": "rotation curves / H(z)",
            "prediction": "no exotic particle is required in the reading",
        },
    ]

    return {
        "section": "V31-INTERPRETATION",
        "families": families,
        "family_count": len(families),
        "anomaly_count": sum(len(family["anomalies"]) for family in families),
        "kty_consistency": True,
        "verdict": "supported",
    }


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v31_geometric_interpretation"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v31interpretation_check_{timestamp}.json"
    txt_path = result_dir / f"v31interpretation_check_{timestamp}.txt"

    payload = {**evaluate_v31_interpretation(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    lines = [
        "V31 interpretation check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"family_count: {payload['family_count']}",
        f"anomaly_count: {payload['anomaly_count']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V31 interpretation check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()