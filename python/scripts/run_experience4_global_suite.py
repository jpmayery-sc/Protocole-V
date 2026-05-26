"""Run the experience 4 global suite and summarize the added levels."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from run_atom_basics_suite import run_suite as run_atom_basics_suite
from runalphaport_suite import run_suite as run_alphaport_suite
from runv6suite import run_suite as run_v6_suite
from runv7unifiedphysics_suite import run_suite as run_v7_suite
from run_point_atome_master_suite import run_suite as run_point_atome_master_suite
from run_point_atome_protocol_suite import run_suite as run_point_atome_protocol_suite
from run_s_law_suite import run_suite as run_s_law_suite
from runv47baryons_suite import run_suite as run_v47_baryons_suite
from runv48b_suite import run_suite as run_v48_b_suite
from runv48neutrinos_suite import run_suite as run_v48_neutrinos_suite
from runv49photon_suite import run_suite as run_v49_photon_suite


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_summary() -> dict:
    suite_specs = [
        ("atom_basics", run_atom_basics_suite),
        ("point_atome_protocol", run_point_atome_protocol_suite),
        ("point_atome_master", run_point_atome_master_suite),
        ("s_law_master", run_s_law_suite),
        ("alphaportsuite", run_alphaport_suite),
        ("v6_d2_electron", run_v6_suite),
        ("v7unifiedphysics_suite", run_v7_suite),
        ("v47_baryons_suite", run_v47_baryons_suite),
        ("v48_b_suite", run_v48_b_suite),
        ("v48_neutrinos_suite", run_v48_neutrinos_suite),
        ("v49_photon_suite", run_v49_photon_suite),
    ]

    items = []
    supported = 0
    for label, runner in suite_specs:
        suite_result = runner()
        verdict = suite_result.get("overall_verdict") or suite_result.get("verdict") or "unknown"
        if verdict in {"supported", "conforme strict"}:
            supported += 1
        items.append(
            {
                "label": label,
                "verdict": verdict,
                "json_path": suite_result.get("json_path"),
                "txt_path": suite_result.get("txt_path"),
                "items": suite_result.get("items", []),
            }
        )

    overall_verdict = "supported" if supported == len(items) else ("contradicted" if supported == 0 else "partiel")
    return {
        "suite": "experience4_global",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported,
        "total": len(items),
        "items": items,
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"experience4_global_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"experience4_global_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Experience 4 global suite summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        "",
        "Items:",
    ]
    for item in summary["items"]:
        lines.append(f"- {item['label']}: {item['verdict']} -> {item['json_path']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_suite(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"

    summary = build_summary()
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the experience 4 global suite and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()