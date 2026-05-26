"""Build and check the V11 combined redshift block."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v11atom_check import evaluate_internal_redshift
from v11canal_check import evaluate_channel_redshift
from v11geo_check import evaluate_geometric_redshift


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def evaluate_total_redshift() -> dict:
    geo_result = evaluate_geometric_redshift()
    atom_result = evaluate_internal_redshift()
    canal_result = evaluate_channel_redshift()

    cases = []
    for geo_case, atom_case, canal_case in zip(geo_result["cases"], atom_result["cases"], canal_result["cases"]):
        environments = []
        for geo_env, atom_env, canal_env in zip(geo_case["environments"], atom_case["environments"], canal_case["environments"]):
            z_mod = geo_env["redshift"] + atom_env["redshift"] + canal_env["redshift"]
            environments.append(
                {
                    "name": geo_env["name"],
                    "z_geo": geo_env["redshift"],
                    "z_int": atom_env["redshift"],
                    "z_canal": canal_env["redshift"],
                    "z_mod": z_mod,
                }
            )
        cases.append(
            {
                "name": geo_case["name"],
                "z": geo_case["z"],
                "environments": environments,
                "nominal_z_mod": environments[1]["z_mod"],
            }
        )

    nominal_band_ok = all(1.0e-9 <= case["nominal_z_mod"] <= 1.0e-5 for case in cases)
    z_order_ok = all(later["nominal_z_mod"] > earlier["nominal_z_mod"] for earlier, later in zip(cases, cases[1:]))
    env_order_ok = all(
        later["z_mod"] > earlier["z_mod"]
        for case in cases
        for earlier, later in zip(case["environments"], case["environments"][1:])
    )
    testable_window_ok = min(case["nominal_z_mod"] for case in cases) >= 1.0e-6 and max(case["nominal_z_mod"] for case in cases) <= 1.0e-5
    coherence_ok = geo_result["verdict"] == "conforme" and atom_result["verdict"] == "conforme" and canal_result["verdict"] == "conforme"
    verdict = "conforme" if nominal_band_ok and z_order_ok and env_order_ok and testable_window_ok and coherence_ok else "rejette"

    return {
        "cases": cases,
        "nominal_band_ok": nominal_band_ok,
        "z_order_ok": z_order_ok,
        "env_order_ok": env_order_ok,
        "testable_window_ok": testable_window_ok,
        "coherence_ok": coherence_ok,
        "verdict": verdict,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    result = evaluate_total_redshift()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "le redshift total du modele est la somme coherente des contributions geo, atom et canal",
        "case_control": "H, Fe, Pb, U",
        "observable": "z_mod",
        "expected": "effet total petit, structure et testable dans une plage realiste",
        "measured": {
            "nominal_band_ok": result["nominal_band_ok"],
            "z_order_ok": result["z_order_ok"],
            "env_order_ok": result["env_order_ok"],
            "testable_window_ok": result["testable_window_ok"],
            "coherence_ok": result["coherence_ok"],
        },
        "cases": result["cases"],
        "verdict": result["verdict"],
        "reference": "V11 GEO, ATOM and CANAL blocks",
    }

    json_path = outdir / f"v11total_check_{timestamp}.json"
    txt_path = outdir / f"v11total_check_{timestamp}.txt"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V11 total redshift check",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"nominal_band_ok: {result['nominal_band_ok']}",
        f"z_order_ok: {result['z_order_ok']}",
        f"env_order_ok: {result['env_order_ok']}",
        f"testable_window_ok: {result['testable_window_ok']}",
        "",
        "Cases:",
    ]
    for case in result["cases"]:
        environments = ", ".join(
            f"{environment['name']}={environment['z_mod']:.6e}"
            for environment in case["environments"]
        )
        lines.append(f"- {case['name']}: {environments}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Build and check the V11 combined redshift block.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()