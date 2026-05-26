"""Check the V5-E alpha(E) running-coupling port."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


ENERGY_POINTS = [
    {"name": "E1", "energy_gev": 0.0, "alpha": 1.0 / 137.036},
    {"name": "E2", "energy_gev": 91.1876, "alpha": 1.0 / 128.0},
]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_running_coupling() -> dict:
    point_1 = ENERGY_POINTS[0]
    point_2 = ENERGY_POINTS[1]

    alpha_e1 = point_1["alpha"]
    alpha_e2 = point_2["alpha"]
    energy_e1 = point_1["energy_gev"]
    energy_e2 = point_2["energy_gev"]

    delta_alpha = alpha_e2 - alpha_e1
    delta_energy = energy_e2 - energy_e1
    dalphadE = delta_alpha / delta_energy
    sign = "positive" if dalphadE > 0 else ("negative" if dalphadE < 0 else "zero")

    running_coupling_ok = dalphadE > 0 and alpha_e2 > alpha_e1
    small_slope_ok = dalphadE < 1.0e-4
    verdict = "conforme" if running_coupling_ok and small_slope_ok else ("partiel" if running_coupling_ok else "rejette")

    return {
        "alpha_E1": alpha_e1,
        "alpha_E2": alpha_e2,
        "energy_E1_GeV": energy_e1,
        "energy_E2_GeV": energy_e2,
        "delta_alpha": delta_alpha,
        "delta_energy_GeV": delta_energy,
        "dalphadE": dalphadE,
        "sign": sign,
        "running_coupling_ok": running_coupling_ok,
        "small_slope_ok": small_slope_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_running_coupling()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "alpha varie avec l'energie (running coupling)",
        "case_control": "valeurs tabulees de alpha(E)",
        "observable": "pente d_alpha/dE",
        "expected": "pente positive faible, alpha croissante avec E",
        "measured": {
            "alpha_E1": result["alpha_E1"],
            "alpha_E2": result["alpha_E2"],
            "energy_E1_GeV": result["energy_E1_GeV"],
            "energy_E2_GeV": result["energy_E2_GeV"],
            "delta_alpha": result["delta_alpha"],
            "delta_energy_GeV": result["delta_energy_GeV"],
            "dalphadE": result["dalphadE"],
            "sign": result["sign"],
        },
        "running_coupling_ok": result["running_coupling_ok"],
        "small_slope_ok": result["small_slope_ok"],
        "verdict": result["verdict"],
        "reference": "QED running coupling",
    }

    json_path = outdir / f"alphaenergyrunning_check_{timestamp}.json"
    txt_path = outdir / f"alphaenergyrunning_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Alpha energy running check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"alpha_E1: {result['alpha_E1']:.15f}",
        f"alpha_E2: {result['alpha_E2']:.15f}",
        f"energy_E1_GeV: {result['energy_E1_GeV']:.4f}",
        f"energy_E2_GeV: {result['energy_E2_GeV']:.4f}",
        f"delta_alpha: {result['delta_alpha']:.15e}",
        f"delta_energy_GeV: {result['delta_energy_GeV']:.4f}",
        f"dalphadE: {result['dalphadE']:.15e}",
        f"sign: {result['sign']}",
        f"running_coupling_ok: {result['running_coupling_ok']}",
        f"small_slope_ok: {result['small_slope_ok']}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V5-E alpha(E) running-coupling port.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()