"""Run the S-law consolidation suite and summarize the results."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from alpha_constant_check import run_check as run_alpha_constant_check
from alpha_phase_observable_check import run_check as run_alpha_phase_observable_check
from runalphaport_suite import run_suite as run_alphaport_suite
from runv6suite import run_suite as run_v6_suite
from runv7unifiedphysics_suite import run_suite as run_v7_suite
from family_l_slope_check import run_check as run_family_l_slope_check
from fine_variation_equivalence_check import run_check as run_fine_variation_equivalence_check
from heavy_border_control_check import main as heavy_border_control_main
from radius_predictivity_check import run_check as run_radius_predictivity_check
from regime_physics_common import latest_report, workspace_root, write_report
from run_regime_physics_suite import run_suite as run_regime_physics_suite
from run_point_atome_master_suite import run_suite as run_point_atome_master_suite
from screening_law_saturation_check import run_check as run_screening_law_saturation_check


def run_script(command: list[str]) -> None:
    print(f"Running: {Path(command[1]).name}")
    subprocess.run(command, check=True)


def run_heavy_border_check() -> dict:
    root = workspace_root()
    script_path = root / "python" / "scripts" / "heavy_border_control_check.py"
    run_script([sys.executable, str(script_path)])
    report_dir = root / "python" / "results" / "heavy_border"
    report_path = latest_report(report_dir, "heavy_border_control_check")
    return json.loads(report_path.read_text(encoding="utf-8"))


def run_lanthanide_residual_check() -> dict:
    root = workspace_root()
    script_path = root / "python" / "scripts" / "lanthanide_internal_residual_check.py"
    run_script([sys.executable, str(script_path)])
    report_dir = root / "python" / "results"
    report_path = latest_report(report_dir, "lanthanide_internal_residual_check")
    return json.loads(report_path.read_text(encoding="utf-8"))


def build_summary() -> dict:
    suite_specs = [
        ("screening_law_saturation", run_screening_law_saturation_check, "support"),
        ("radius_predictivity", run_radius_predictivity_check, "support"),
        ("fine_variation_equivalence", run_fine_variation_equivalence_check, "support"),
        ("family_l_slope", run_family_l_slope_check, "falsifier"),
        ("regime_physics", run_regime_physics_suite, "support"),
        ("alpha_phase_observable", run_alpha_phase_observable_check, "support"),
        ("alpha_constant", run_alpha_constant_check, "falsifier"),
        ("alphaportsuite", run_alphaport_suite, "support"),
        ("v6_d2_electron", run_v6_suite, "support"),
        ("v7unifiedphysics_suite", run_v7_suite, "support"),
        ("point_atome_master", run_point_atome_master_suite, "support"),
    ]

    items = []
    support_total = 0
    support_ok = 0
    falsifier_total = 0
    falsifier_ok = 0

    for label, runner, role in suite_specs:
        suite_result = runner()
        verdict = suite_result.get("overall_verdict") or suite_result.get("verdict") or "unknown"
        json_path = suite_result.get("json_path")
        txt_path = suite_result.get("txt_path")
        if role == "support":
            support_total += 1
            if verdict in {"supported", "conforme strict"}:
                support_ok += 1
        else:
            falsifier_total += 1
            if verdict in {"falsifie", "contradicted"}:
                falsifier_ok += 1
        items.append(
            {
                "label": label,
                "role": role,
                "verdict": verdict,
                "json_path": json_path,
                "txt_path": txt_path,
                "summary": suite_result.get("summary") if isinstance(suite_result.get("summary"), dict) else None,
            }
        )

    lanthanide_result = run_lanthanide_residual_check()
    lanthanide_verdict = lanthanide_result.get("verdict", "unknown")
    support_total += 1
    if lanthanide_verdict in {"supported", "conforme strict"}:
        support_ok += 1
    items.append(
        {
            "label": "lanthanide_internal_residual",
            "role": "support",
            "verdict": lanthanide_verdict,
            "json_path": lanthanide_result.get("json_path"),
            "txt_path": lanthanide_result.get("txt_path"),
            "summary": None,
        }
    )

    heavy_border_result = run_heavy_border_check()
    heavy_border_verdict = heavy_border_result.get("overall_verdict") or heavy_border_result.get("verdict") or "unknown"
    support_total += 1
    if heavy_border_verdict in {"supported", "conforme strict"}:
        support_ok += 1
    items.append(
        {
            "label": "heavy_border",
            "role": "support",
            "verdict": heavy_border_verdict,
            "json_path": heavy_border_result.get("json_path"),
            "txt_path": heavy_border_result.get("txt_path"),
            "summary": heavy_border_result.get("summary") if isinstance(heavy_border_result.get("summary"), dict) else None,
        }
    )

    overall_support_ok = support_ok == support_total
    overall_falsifier_ok = falsifier_ok == falsifier_total
    if overall_support_ok and overall_falsifier_ok:
        overall_verdict = "supported"
    elif overall_support_ok or overall_falsifier_ok:
        overall_verdict = "partiel"
    else:
        overall_verdict = "contradicted"
    return {
        "suite": "s_law_master",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": support_ok,
        "support_total": support_total,
        "falsifier_ok": falsifier_ok,
        "falsifier_total": falsifier_total,
        "total": len(items),
        "items": items,
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"s_law_master_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"s_law_master_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "S-law master suite summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['support_total']}",
        f"falsifier_count: {summary['falsifier_ok']}/{summary['falsifier_total']}",
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
    parser = argparse.ArgumentParser(description="Run the S-law master suite and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()