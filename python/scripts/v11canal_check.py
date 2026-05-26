"""Check the V11 electronic-channel redshift block."""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

from v7electronic_check import evaluate_electron_response


CHANNEL_CASES = [
    {"name": "H", "z": 1},
    {"name": "Fe", "z": 26},
    {"name": "Pb", "z": 82},
    {"name": "U", "z": 92},
]
ENVIRONMENTS = [
    {"name": "quiet", "channel_scale": 0.8},
    {"name": "nominal", "channel_scale": 1.0},
    {"name": "extreme", "channel_scale": 1.2},
]


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def kappa_lookup() -> dict[int, float]:
    electron_result = evaluate_electron_response()
    lookup = {int(n_value): float(kappa_value) for n_value, kappa_value in zip(electron_result["base_ns"], electron_result["base_kappas"])}
    for entry in electron_result["extrapolated"]:
        lookup[int(entry["n"])] = float(entry["kappa"])
    return lookup


def relative_channel_shift(z_value: int, lookup: dict[int, float], channel_scale: float) -> float:
    band = min(7, max(2, 2 + (z_value - 1) // 20))
    upper_band = min(7, band + 1)
    delta_kappa = abs(lookup[band] - lookup[upper_band])
    return (delta_kappa / lookup[band]) * 1.0e-6 * channel_scale * math.exp(float(z_value) / 60.0)


def evaluate_channel_redshift() -> dict:
    lookup = kappa_lookup()
    cases = []
    for case in CHANNEL_CASES:
        environments = []
        redshifts = []
        for environment in ENVIRONMENTS:
            redshift = relative_channel_shift(case["z"], lookup, environment["channel_scale"])
            environments.append(
                {
                    "name": environment["name"],
                    "channel_scale": environment["channel_scale"],
                    "redshift": redshift,
                }
            )
            redshifts.append(redshift)
        cases.append(
            {
                "name": case["name"],
                "z": case["z"],
                "environments": environments,
                "nominal_redshift": redshifts[1],
            }
        )

    monotone_ok = all(later["nominal_redshift"] > earlier["nominal_redshift"] for earlier, later in zip(cases, cases[1:]))
    env_growth_ok = all(
        later["redshift"] > earlier["redshift"]
        for case in cases
        for earlier, later in zip(case["environments"], case["environments"][1:])
    )
    band_ok = all(1.0e-7 <= environment["redshift"] <= 1.0e-5 for case in cases for environment in case["environments"])
    no_divergence_ok = max(environment["redshift"] for case in cases for environment in case["environments"]) < 1.0e-4
    verdict = "conforme" if monotone_ok and env_growth_ok and band_ok and no_divergence_ok else "rejette"

    return {
        "cases": cases,
        "monotone_ok": monotone_ok,
        "env_growth_ok": env_growth_ok,
        "band_ok": band_ok,
        "no_divergence_ok": no_divergence_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_channel_redshift()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la variation relative du canal electronique induit un redshift effectif petit et monotone",
        "case_control": "H, Fe, Pb, U",
        "observable": "z_canal",
        "expected": "variation monotone avec Z, sans divergence, plus marquee pour des torsions plus fortes",
        "measured": {
            "monotone_ok": result["monotone_ok"],
            "env_growth_ok": result["env_growth_ok"],
            "band_ok": result["band_ok"],
            "no_divergence_ok": result["no_divergence_ok"],
        },
        "cases": result["cases"],
        "verdict": result["verdict"],
        "reference": "V7 electron response",
    }

    json_path = outdir / f"v11canal_check_{timestamp}.json"
    txt_path = outdir / f"v11canal_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V11 channel redshift check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"monotone_ok: {result['monotone_ok']}",
        f"env_growth_ok: {result['env_growth_ok']}",
        f"band_ok: {result['band_ok']}",
        f"no_divergence_ok: {result['no_divergence_ok']}",
        "",
        "Cases:",
    ]
    for case in result["cases"]:
        environments = ", ".join(f"{environment['name']}={environment['redshift']:.6e}" for environment in case["environments"])
        lines.append(f"- {case['name']}: {environments}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check the V11 electronic-channel redshift block.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()