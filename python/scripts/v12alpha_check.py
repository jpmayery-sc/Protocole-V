"""Check the V12 alpha-field falsification bounds."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v7coupling_check import evaluate_coupling_field


STRICT_BAND = 1.0e-8


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def evaluate_alpha_bounds() -> dict:
    coupling_result = evaluate_coupling_field()
    alpha_ref = coupling_result["alpha0"]
    grid = coupling_result["grid"]
    values = [entry["alpha"] for entry in grid]
    deviations = [abs(value - alpha_ref) for value in values]

    strict_band_ok = max(deviations) <= STRICT_BAND
    derivative_r_ok = coupling_result["partial_r_negative_ok"]
    derivative_e_ok = coupling_result["partial_E_positive_ok"]
    derivative_n_ok = coupling_result["partial_n_negative_ok"]
    surface_present_ok = coupling_result["stability_surface_ok"] and coupling_result["stability_band_ok"]

    if strict_band_ok and derivative_r_ok and derivative_e_ok and derivative_n_ok and surface_present_ok:
        verdict = "conforme"
    elif (not strict_band_ok) or (not surface_present_ok):
        verdict = "falsifie"
    else:
        verdict = "partiel"

    return {
        "alpha_ref": alpha_ref,
        "grid": grid,
        "deviations": deviations,
        "strict_band_ok": strict_band_ok,
        "derivative_r_ok": derivative_r_ok,
        "derivative_e_ok": derivative_e_ok,
        "derivative_n_ok": derivative_n_ok,
        "surface_present_ok": surface_present_ok,
        "max_deviation": max(deviations),
        "stability_range": coupling_result["stability_range"],
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_alpha_bounds()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "alpha(E,n,r) must stay extremely close to alpha_ref and preserve its geometric gradients",
        "case_control": "V7 coupling grid",
        "observable": "alpha(E,n,r)",
        "expected": "strict band, monotone radial decay, nonzero stability surface",
        "measured": {
            "alpha_ref": result["alpha_ref"],
            "strict_band_ok": result["strict_band_ok"],
            "derivative_r_ok": result["derivative_r_ok"],
            "derivative_e_ok": result["derivative_e_ok"],
            "derivative_n_ok": result["derivative_n_ok"],
            "surface_present_ok": result["surface_present_ok"],
            "max_deviation": result["max_deviation"],
            "stability_range": result["stability_range"],
        },
        "verdict": result["verdict"],
        "reference": "V7 coupling field alpha(E,n,r)",
    }

    json_path = outdir / f"v12alpha_check_{timestamp}.json"
    txt_path = outdir / f"v12alpha_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V12 alpha bounds check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"strict_band_ok: {result['strict_band_ok']}",
        f"derivative_r_ok: {result['derivative_r_ok']}",
        f"derivative_e_ok: {result['derivative_e_ok']}",
        f"derivative_n_ok: {result['derivative_n_ok']}",
        f"surface_present_ok: {result['surface_present_ok']}",
        f"max_deviation: {result['max_deviation']:.6e}",
        f"stability_range: {result['stability_range']:.6e}",
    ]
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check V12 alpha-field falsification bounds.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()