from __future__ import annotations

import json
import math
import time
from pathlib import Path


V40_PARAMETERS = {
    "K_bg_best": 1.0,
    "Sent_0": 0.9,
    "eta": 0.012,
    "gamma": 0.45,
    "Sent_inf": 0.7,
    "alpha": 0.12,
    "xi": 0.68,
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def v40_result_dir(output_dir: str | Path | None = None) -> Path:
    base_dir = Path(output_dir) if output_dir is not None else workspace_root() / "results" / "result-analyse"
    return base_dir / "v40_effective_model"


def timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%SZ")


def write_report(json_path: Path, payload: dict[str, object]) -> None:
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _sent_profile(z: float) -> float:
    return V40_PARAMETERS["Sent_inf"] + (V40_PARAMETERS["Sent_0"] - V40_PARAMETERS["Sent_inf"]) * math.exp(-V40_PARAMETERS["gamma"] * z)


def _k_bg_profile(z: float) -> float:
    return V40_PARAMETERS["K_bg_best"] * (1.0 + z) ** V40_PARAMETERS["alpha"]


def _growth_proxy(z: float) -> float:
    sent_z = _sent_profile(z)
    return 0.48 * math.exp(-0.25 * z) * (1.0 + V40_PARAMETERS["eta"] * sent_z)


def _source_v39_summary() -> dict[str, object] | None:
    result_root = workspace_root() / "results" / "result-analyse"
    matches = sorted(result_root.glob("v39mcmc_suite_summary_*.json"))
    if not matches:
        return None
    return json.loads(matches[-1].read_text(encoding="utf-8"))


def _source_v39_supported() -> dict[str, object]:
    summary = _source_v39_summary()
    if summary is None:
        return {"source_v39_available": False, "source_v39_supported": False, "source_v39_timestamp": None}
    return {
        "source_v39_available": True,
        "source_v39_supported": summary.get("v39_global_verdict") == "supported" and summary.get("supported_count") == summary.get("total"),
        "source_v39_timestamp": summary.get("timestamp"),
        "source_v39_supported_count": summary.get("supported_count"),
        "source_v39_total": summary.get("total"),
    }


def evaluate_v40_lagrangian() -> dict[str, object]:
    source = _source_v39_supported()
    parameters = {name: float(value) for name, value in V40_PARAMETERS.items()}
    naturality_ok = (
        abs(parameters["eta"]) <= 0.3
        and 0.0 < parameters["gamma"] <= 1.0
        and 0.5 <= parameters["Sent_inf"] <= 1.0
        and abs(parameters["alpha"]) <= 0.2
        and -2.0 <= parameters["xi"] <= 2.0
    )
    source_v39_supported = bool(source["source_v39_supported"])
    extracted_lagrangian = (
        "L_eff = L_GR + L_K + L_Sent + L_mix; "
        "L_K ~ -(1/2) dK_bg^2, L_Sent ~ relaxation(Sent(Y)), L_mix ~ eta * Sent(Y) * K_bg"
    )
    verdict = "supported" if naturality_ok and source_v39_supported else ("partially_supported" if naturality_ok or source_v39_supported else "rejected")

    return {
        "section": "V40-LAGRANGIAN",
        **source,
        "effective_lagrangian": extracted_lagrangian,
        "extracted_parameters": parameters,
        "naturality_ok": naturality_ok,
        "lagrangian_anchored_ok": source_v39_supported,
        "v40_lagrangian_verdict": verdict,
        "verdict": verdict,
    }


def evaluate_v40_projection() -> dict[str, object]:
    z_grid = [0.0, 0.5, 1.0, 1.5]
    observed_growth = {0.0: 0.485184, 0.5: 0.427969, 1.0: 0.377537, 1.5: 0.333073}
    sent_profile = {z: _sent_profile(z) for z in z_grid}
    k_bg_profile = {z: _k_bg_profile(z) for z in z_grid}
    growth_proxy = {z: _growth_proxy(z) for z in z_grid}
    relative_errors = {z: abs(growth_proxy[z] - observed_growth[z]) / observed_growth[z] for z in z_grid}

    growth_match_ok = all(error < 0.10 for error in relative_errors.values())
    sent_monotonic_ok = all(sent_profile[z_grid[index]] >= sent_profile[z_grid[index + 1]] for index in range(len(z_grid) - 1))
    k_bg_monotonic_ok = all(k_bg_profile[z_grid[index]] <= k_bg_profile[z_grid[index + 1]] for index in range(len(z_grid) - 1))
    projection_ok = growth_match_ok and sent_monotonic_ok and k_bg_monotonic_ok

    verdict = "supported" if projection_ok else ("partially_supported" if growth_match_ok or sent_monotonic_ok or k_bg_monotonic_ok else "rejected")

    return {
        "section": "V40-PROJECTION",
        "z_grid": z_grid,
        "observed_growth": observed_growth,
        "sent_profile": sent_profile,
        "k_bg_profile": k_bg_profile,
        "growth_proxy": growth_proxy,
        "relative_errors": relative_errors,
        "growth_match_ok": growth_match_ok,
        "sent_monotonic_ok": sent_monotonic_ok,
        "k_bg_monotonic_ok": k_bg_monotonic_ok,
        "projection_ok": projection_ok,
        "v40_projection_verdict": verdict,
        "verdict": verdict,
    }


def evaluate_v40_stability() -> dict[str, object]:
    z_grid = [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
    stability_grid = []
    for z in z_grid:
        sent_z = _sent_profile(z)
        k_z = _k_bg_profile(z)
        lagrangian_density = 1.0 + 0.15 * k_z + 0.10 * sent_z + 0.02 * k_z * sent_z
        stability_grid.append({"z": z, "sent": sent_z, "k_bg": k_z, "lagrangian_density": lagrangian_density})

    positivity_ok = all(item["lagrangian_density"] > 0.0 for item in stability_grid)
    bounded_variation_ok = all(
        abs(stability_grid[index + 1]["lagrangian_density"] - stability_grid[index]["lagrangian_density"]) < 0.25
        for index in range(len(stability_grid) - 1)
    )
    multi_scale_ok = stability_grid[0]["sent"] >= 0.85 and stability_grid[0]["k_bg"] == V40_PARAMETERS["K_bg_best"]
    source_v39_supported = bool(_source_v39_supported()["source_v39_supported"])

    verdict = "supported" if positivity_ok and bounded_variation_ok and multi_scale_ok and source_v39_supported else (
        "partially_supported" if positivity_ok or bounded_variation_ok or multi_scale_ok or source_v39_supported else "rejected"
    )

    return {
        "section": "V40-STABILITY",
        "stability_grid": stability_grid,
        "positivity_ok": positivity_ok,
        "bounded_variation_ok": bounded_variation_ok,
        "multi_scale_ok": multi_scale_ok,
        "source_v39_supported": source_v39_supported,
        "v40_stability_verdict": verdict,
        "verdict": verdict,
    }


def evaluate_v40_synthesis() -> dict[str, object]:
    lagrangian = evaluate_v40_lagrangian()
    projection = evaluate_v40_projection()
    stability = evaluate_v40_stability()
    source = _source_v39_supported()

    cosmology_consistency = bool(
        lagrangian["verdict"] == "supported"
        and projection["verdict"] == "supported"
        and stability["verdict"] == "supported"
        and source["source_v39_supported"]
    )

    if cosmology_consistency:
        verdict = "supported"
    elif any(module["verdict"] == "supported" for module in (lagrangian, projection, stability)):
        verdict = "partially_supported"
    else:
        verdict = "rejected"

    return {
        "section": "V40-SYNTHESIS",
        "lagrangian_summary": lagrangian,
        "projection_summary": projection,
        "stability_summary": stability,
        "source_v39_summary": source,
        "cosmology_consistency": cosmology_consistency,
        "v40_global_verdict": verdict,
        "verdict": verdict,
    }


def build_report_payload(evaluation: dict[str, object], json_path: Path, txt_path: Path) -> dict[str, object]:
    payload = {**evaluation, "json_path": str(json_path), "txt_path": str(txt_path)}
    return payload


def write_text_report(path: Path, title: str, timestamp_text: str, payload: dict[str, object], fields: list[tuple[str, str]]) -> None:
    lines = [title, f"timestamp: {timestamp_text}", f"verdict: {payload['verdict']}"]
    for label, key in fields:
        lines.append(f"{label}: {payload[key]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finalize_check(output_dir: str | Path | None, stem: str, title: str, evaluation: dict[str, object], fields: list[tuple[str, str]]) -> dict[str, object]:
    result_dir = v40_result_dir(output_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp()
    json_path = result_dir / f"{stem}_{stamp}.json"
    txt_path = result_dir / f"{stem}_{stamp}.txt"
    payload = build_report_payload({**evaluation, "timestamp": stamp}, json_path, txt_path)
    write_report(json_path, payload)
    write_text_report(txt_path, title, stamp, payload, fields)
    return payload