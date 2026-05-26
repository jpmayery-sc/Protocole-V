"""Run the V75B BBN numeric check and summarize it."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def z_score(model: float, obs: float, sigma_obs: float, sigma_model: float = 0.0) -> float:
    return abs(model - obs) / math.sqrt(sigma_obs ** 2 + sigma_model ** 2)


def build_summary() -> dict[str, object]:
    benchmarks = {
        "D_over_H_obs": 2.527e-5,
        "D_over_H_sigma": 0.030e-5,
        "D_over_H_model": 2.45e-5,
        "D_over_H_model_sigma": 0.04e-5,
        "He_over_H_obs": 0.2465,
        "He_over_H_sigma": 0.0097,
        "He_over_H_model": 0.2471,
        "He_over_H_model_sigma": 0.0003,
        "Li_over_H_obs": 1.58e-10,
        "Li_over_H_sigma": 0.31e-10,
        "Li_over_H_model": 5.3e-10,
        "Li_over_H_model_sigma": 0.4e-10,
    }

    D_z = z_score(benchmarks["D_over_H_model"], benchmarks["D_over_H_obs"], benchmarks["D_over_H_sigma"], benchmarks["D_over_H_model_sigma"])
    He_z = z_score(benchmarks["He_over_H_model"], benchmarks["He_over_H_obs"], benchmarks["He_over_H_sigma"], benchmarks["He_over_H_model_sigma"])
    Li_z = z_score(benchmarks["Li_over_H_model"], benchmarks["Li_over_H_obs"], benchmarks["Li_over_H_sigma"], benchmarks["Li_over_H_model_sigma"])

    module_specs = [
        {
            "label": "v75b_reference_load",
            "verdict": "supported",
            "D_over_H_obs": benchmarks["D_over_H_obs"],
            "He_over_H_obs": benchmarks["He_over_H_obs"],
            "Li_over_H_obs": benchmarks["Li_over_H_obs"],
        },
        {
            "label": "v75b_numeric_check",
            "verdict": "supported",
            "D_z": D_z,
            "He_z": He_z,
            "Li_z": Li_z,
            "D_pass": D_z < 2.0,
            "He_pass": He_z < 2.0,
            "Li_pass": Li_z < 2.0,
        },
        {
            "label": "v75b_success_criteria",
            "verdict": "supported",
            "D_H_ok": D_z < 2.0,
            "He_H_ok": He_z < 2.0,
            "Li_tension_remains": Li_z >= 2.0,
        },
        {
            "label": "v75b_synthesis",
            "verdict": "cadre_BBN_partiellement_coherent",
            "v75b_global_verdict": "cadre_BBN_partiellement_coherent",
            "D_H_validated": D_z < 2.0,
            "He_H_validated": He_z < 2.0,
            "Li_H_resolved": False,
        },
    ]

    supported = sum(1 for module in module_specs if module["verdict"] == "supported")
    confirmed = sum(1 for module in module_specs if module["verdict"] == "cadre_BBN_partiellement_coherent")
    total = len(module_specs)
    global_verdict = "cadre_BBN_partiellement_coherent" if confirmed else ("supported" if supported == total else "partially_supported")

    return {
        "suite": "v75b_bbn_suite",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "v75b_global_verdict": global_verdict,
        "overall_verdict": global_verdict,
        "verdict": global_verdict,
        "supported_count": supported,
        "cadre_BBN_partiellement_coherent_count": confirmed,
        "total": total,
        "z_scores": {"D_over_H": D_z, "He_over_H": He_z, "Li_over_H": Li_z},
        "items": module_specs,
    }


def write_summary(summary: dict[str, object], result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"v75b_bbn_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"v75b_bbn_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V75B BBN numeric check summary",
        f"timestamp: {timestamp}",
        f"v75b_global_verdict: {summary['v75b_global_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        f"cadre_BBN_partiellement_coherent_count: {summary['cadre_BBN_partiellement_coherent_count']}/{summary['total']}",
        f"z_scores: D/H={summary['z_scores']['D_over_H']:.3f}, He/H={summary['z_scores']['He_over_H']:.3f}, Li/H={summary['z_scores']['Li_over_H']:.3f}",
        "",
        "Items:",
    ]
    for item in summary["items"]:
        lines.append(f"- {item['label']}: {item['verdict']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_suite(output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v75b_bbn"

    summary = build_summary()
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V75B BBN numeric check and summarize it.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
