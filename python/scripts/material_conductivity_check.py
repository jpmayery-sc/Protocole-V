"""Validate the material conductivity block: copper, iron, aluminum, silicon.

The script keeps the checks deterministic and small. It verifies the reference
ordering and the expected response to temperature, defects, oxide, and doping.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path


CASE_DATA = {
    "copper": {
        "name": "Cuivre",
        "rho_pure": 1.68e-8,
        "rho_hot": 1.95e-8,
        "rho_impure": 3.25e-8,
        "rhos_expected": ["low", "hotter", "impure"],
    },
    "iron": {
        "name": "Fer",
        "rho_pure": 9.71e-8,
        "rho_hot": 1.10e-7,
        "rho_impure": 1.34e-7,
        "rhos_expected": ["above_copper", "hotter", "impure"],
    },
    "aluminum": {
        "name": "Aluminium",
        "rho_pure": 2.82e-8,
        "rho_hot": 3.15e-8,
        "rho_oxide": 4.20e-8,
        "rhos_expected": ["between_copper_and_iron", "hotter", "oxide"],
    },
    "silicon": {
        "name": "Silicium",
        "sigma_intrinsic": 1.0e-4,
        "sigma_hot": 2.0e-3,
        "sigma_doped_n": 1.0e2,
        "sigma_doped_p": 8.0e1,
        "band_gap_ev": 1.12,
    },
}


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def evaluate_copper(copper: dict) -> dict:
    low_ok = copper["rho_pure"] < 2.0e-8
    hot_ok = copper["rho_hot"] > copper["rho_pure"]
    impure_ok = copper["rho_impure"] > copper["rho_hot"] > copper["rho_pure"]
    return {**copper, "low_ok": low_ok, "hot_ok": hot_ok, "impure_ok": impure_ok, "ok": low_ok and hot_ok and impure_ok}


def evaluate_iron(iron: dict, copper: dict) -> dict:
    above_copper_ok = iron["rho_pure"] > copper["rho_pure"]
    hot_ok = iron["rho_hot"] > iron["rho_pure"]
    impurity_ok = iron["rho_impure"] > iron["rho_hot"] > iron["rho_pure"]
    return {
        **iron,
        "above_copper_ok": above_copper_ok,
        "hot_ok": hot_ok,
        "impurity_ok": impurity_ok,
        "ok": above_copper_ok and hot_ok and impurity_ok,
    }


def evaluate_aluminum(aluminum: dict, copper: dict, iron: dict) -> dict:
    between_ok = copper["rho_pure"] < aluminum["rho_pure"] < iron["rho_pure"]
    hot_ok = aluminum["rho_hot"] > aluminum["rho_pure"]
    oxide_ok = aluminum["rho_oxide"] > aluminum["rho_hot"] > aluminum["rho_pure"]
    return {
        **aluminum,
        "between_ok": between_ok,
        "hot_ok": hot_ok,
        "oxide_ok": oxide_ok,
        "ok": between_ok and hot_ok and oxide_ok,
    }


def evaluate_silicon(silicon: dict) -> dict:
    intrinsic_ok = silicon["sigma_intrinsic"] < 1.0e-3
    hot_ok = silicon["sigma_hot"] > silicon["sigma_intrinsic"]
    doped_ok = silicon["sigma_doped_n"] > silicon["sigma_hot"] > silicon["sigma_intrinsic"] and silicon["sigma_doped_p"] > silicon["sigma_intrinsic"]
    gap_ok = silicon["band_gap_ev"] > 0.0
    return {
        **silicon,
        "intrinsic_ok": intrinsic_ok,
        "hot_ok": hot_ok,
        "doped_ok": doped_ok,
        "gap_ok": gap_ok,
        "ok": intrinsic_ok and hot_ok and doped_ok and gap_ok,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    ts = time.strftime("%Y%m%d-%H%M%SZ")
    copper = evaluate_copper(CASE_DATA["copper"])
    iron = evaluate_iron(CASE_DATA["iron"], copper)
    aluminum = evaluate_aluminum(CASE_DATA["aluminum"], copper, iron)
    silicon = evaluate_silicon(CASE_DATA["silicon"])

    copper_ok = copper["ok"]
    iron_ok = iron["ok"]
    aluminum_ok = aluminum["ok"]
    silicon_ok = silicon["ok"]
    ordering_ok = copper["rho_pure"] < aluminum["rho_pure"] < iron["rho_pure"]
    overall_ok = copper_ok and iron_ok and aluminum_ok and silicon_ok and ordering_ok

    data = {
        "timestamp": ts,
        "verdict": "supported" if overall_ok else "contradicted",
        "ordering_ok": ordering_ok,
        "copper_ok": copper_ok,
        "iron_ok": iron_ok,
        "aluminum_ok": aluminum_ok,
        "silicon_ok": silicon_ok,
        "cases": {
            "copper": copper,
            "iron": iron,
            "aluminum": aluminum,
            "silicon": silicon,
        },
    }

    json_path = outdir / f"material_conductivity_check_{ts}.json"
    report_path = outdir / f"material_conductivity_check_{ts}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Material conductivity check",
        f"timestamp: {ts}",
        f"verdict: {data['verdict']}",
        f"ordering_ok: {ordering_ok}",
        f"copper_ok: {copper_ok}",
        f"iron_ok: {iron_ok}",
        f"aluminum_ok: {aluminum_ok}",
        f"silicon_ok: {silicon_ok}",
        "",
        "Cases:",
        f"- cuivre: rho_pure={copper['rho_pure']:.3e} rho_hot={copper['rho_hot']:.3e} rho_impure={copper['rho_impure']:.3e}",
        f"- fer: rho_pure={iron['rho_pure']:.3e} rho_hot={iron['rho_hot']:.3e} rho_impure={iron['rho_impure']:.3e}",
        f"- aluminium: rho_pure={aluminum['rho_pure']:.3e} rho_hot={aluminum['rho_hot']:.3e} rho_oxide={aluminum['rho_oxide']:.3e}",
        f"- silicium: sigma_intrinsic={silicon['sigma_intrinsic']:.3e} sigma_hot={silicon['sigma_hot']:.3e} sigma_doped_n={silicon['sigma_doped_n']:.3e} sigma_doped_p={silicon['sigma_doped_p']:.3e}",
    ]
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["report_path"] = str(report_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate the material conductivity block.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()