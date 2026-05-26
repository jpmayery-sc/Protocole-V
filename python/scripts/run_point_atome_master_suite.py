"""Run the top-level point_atome master suite and summarize the result."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from run_atom_basics_suite import run_suite as run_atom_basics_suite
from run_d1d4_suite import run_suite as run_d1d4_suite
from run_electron5_core_suite import run_suite as run_electron5_core_suite
from run_electron5_extended_suite import run_suite as run_electron5_extended_suite
from run_point_atome_protocol_suite import run_suite as run_point_atome_protocol_suite
from runv8atomic_suite import run_suite as run_v8_suite
from runv9atomic_suite import run_suite as run_v9_suite
from run_v10atomdynamics_suite import run_suite as run_v10_suite
from runv11redshiftsuite import run_suite as run_v11_suite
from runv12falsifiersuite import run_suite as run_v12_suite
from runv13mcmc_suite import run_suite as run_v13_suite
from runv14reduction_suite import run_suite as run_v14_suite
from runv15consolidation_suite import run_suite as run_v15_suite
from runv16prediction_suite import run_suite as run_v16_suite
from runv17validation_suite import run_suite as run_v17_suite
from runv18calibration_suite import run_suite as run_v18_suite
from runv19metacalibration_suite import run_suite as run_v19_suite
from runv20research_suite import run_suite as run_v20_suite
from runv21borderline_suite import run_suite as run_v21_suite
from runv22theory_suite import run_suite as run_v22_suite
from runv22experiment_suite import run_suite as run_v22_experiment_suite
from runv22simulation_suite import run_suite as run_v22_simulation_suite


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def build_summary() -> dict:
    suite_specs = [
        ("point_atome_protocol", run_point_atome_protocol_suite),
        ("atom_basics", run_atom_basics_suite),
        ("v8atomicsuite", run_v8_suite),
        ("v9atomicsuite", run_v9_suite),
        ("v10atomdynamics_suite", run_v10_suite),
        ("v11redshift_suite", run_v11_suite),
        ("v12falsifier_suite", run_v12_suite),
        ("v13mcmc_suite", run_v13_suite),
        ("v14reduction_suite", run_v14_suite),
        ("v15consolidation_suite", run_v15_suite),
        ("v16prediction_suite", run_v16_suite),
        ("v17validation_suite", run_v17_suite),
        ("v18calibration_suite", run_v18_suite),
        ("v19metacalibration_suite", run_v19_suite),
        ("v20research_suite", run_v20_suite),
        ("v21borderline_suite", run_v21_suite),
        ("v22theory_suite", run_v22_suite),
        ("v22experiment_suite", run_v22_experiment_suite),
        ("v22simulation_suite", run_v22_simulation_suite),
        ("d1d4", run_d1d4_suite),
        ("electron5_core", run_electron5_core_suite),
        ("electron5_extended", run_electron5_extended_suite),
    ]

    items = []
    supported = 0

    for label, runner in suite_specs:
        suite_result = runner()
        verdict = suite_result.get("overall_verdict") or suite_result.get("verdict") or "unknown"
        json_path = suite_result.get("json_path")
        txt_path = suite_result.get("txt_path")
        if verdict in {"supported", "conforme strict"}:
            supported += 1
        items.append(
            {
                "label": label,
                "verdict": verdict,
                "json_path": json_path,
                "txt_path": txt_path,
                "summary": suite_result.get("summary") if isinstance(suite_result.get("summary"), dict) else None,
            }
        )

    overall_verdict = "supported" if supported == len(items) else ("contradicted" if supported == 0 else "partiel")
    return {
        "suite": "point_atome_master",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported,
        "total": len(items),
        "items": items,
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"point_atome_master_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"point_atome_master_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Point Atome master suite summary",
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
    parser = argparse.ArgumentParser(description="Run the point_atome master suite and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()