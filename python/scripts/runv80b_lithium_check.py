"""Run the V80B lithium check at the fixed V80 best-fit epsilon."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from runv80_bbn_scan import toy_bbn_proxy, z_score, workspace_root


def evaluate(delta_em: float = -0.0069) -> dict[str, object]:
    abundances = toy_bbn_proxy(delta_em)

    d_obs = 2.527e-5
    d_sigma = 0.030e-5
    y_obs = 0.2465
    y_sigma = 0.0097
    li_obs = 1.58e-10
    li_sigma = 0.31e-10

    d_z = z_score(abundances["D_over_H"], d_obs, d_sigma)
    y_z = z_score(abundances["Y_p"], y_obs, y_sigma)
    li_z = z_score(abundances["Li7_over_H"], li_obs, li_sigma)

    verdict = "bbn_liou_solved" if (d_z <= 1.0 and y_z <= 1.0 and li_z <= 1.0) else "bbn_liou_tension"

    return {
        "suite": "v80b_lithium_check",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "delta_em": delta_em,
        "D_over_H": abundances["D_over_H"],
        "Y_p": abundances["Y_p"],
        "Li7_over_H": abundances["Li7_over_H"],
        "Be7_over_H": abundances["Be7_over_H"],
        "D_z": d_z,
        "Y_z": y_z,
        "Li_z": li_z,
        "passes_D": d_z <= 1.0,
        "passes_Y": y_z <= 1.0,
        "passes_Li": li_z <= 1.0,
        "passes_all": d_z <= 1.0 and y_z <= 1.0 and li_z <= 1.0,
        "notes": [
            "V80B is a fixed-point BBN check at epsilon_best.",
            "The same toy proxy as V80 is reused so the result stays reproducible.",
        ],
    }


def write_summary(summary: dict[str, object], output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"v80b_lithium_check_summary_{timestamp}.json"
    txt_path = output_dir / f"v80b_lithium_check_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V80B lithium check summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"delta_em: {summary['delta_em']}",
        f"D_over_H: {summary['D_over_H']}",
        f"Y_p: {summary['Y_p']}",
        f"Li7_over_H: {summary['Li7_over_H']}",
        f"Be7_over_H: {summary['Be7_over_H']}",
        f"D_z: {summary['D_z']}",
        f"Y_z: {summary['Y_z']}",
        f"Li_z: {summary['Li_z']}",
        "",
        "Notes:",
    ]
    for note in summary["notes"]:
        lines.append(f"- {note}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_check(delta_em: float = -0.0069, output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v80b_lithium_check"
    summary = evaluate(delta_em)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V80B lithium check at fixed epsilon_best.")
    parser.add_argument("--delta-em", type=float, default=-0.0069, help="Fixed delta_EM / epsilon_best value")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_check(args.delta_em, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()