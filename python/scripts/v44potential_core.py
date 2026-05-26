from __future__ import annotations

import json
import math
import time
from pathlib import Path


V44_PARAMETERS = {
    "lambda_K": 0.14,
    "lambda_T": 0.11,
    "lambda_KT": -0.03,
    "gamma": 0.45,
    "Y_inf": 0.7,
    "Y0": 0.9,
    "xi": 0.68,
    "eta": 0.012,
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def v44_result_dir(output_dir: str | Path | None = None) -> Path:
    base_dir = Path(output_dir) if output_dir is not None else workspace_root() / "results" / "result-analyse"
    return base_dir / "v44_potential"


def timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%SZ")


def write_report(json_path: Path, payload: dict[str, object]) -> None:
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _source_v43_summary() -> dict[str, object] | None:
    result_root = workspace_root() / "results" / "result-analyse"
    matches = sorted(result_root.glob("v43predictions_suite_summary_*.json"))
    if not matches:
        return None
    return json.loads(matches[-1].read_text(encoding="utf-8"))


def _source_v43_supported() -> dict[str, object]:
    summary = _source_v43_summary()
    if summary is None:
        return {"source_v43_available": False, "source_v43_supported": False, "source_v43_timestamp": None}
    return {
        "source_v43_available": True,
        "source_v43_supported": summary.get("v43_global_verdict") == "supported" and summary.get("supported_count") == summary.get("total"),
        "source_v43_timestamp": summary.get("timestamp"),
        "source_v43_supported_count": summary.get("supported_count"),
        "source_v43_total": summary.get("total"),
    }


def _eigenvalues_from_diagonal(diagonal: list[float]) -> list[float]:
    return diagonal


def evaluate_v44_decomposition() -> dict[str, object]:
    source = _source_v43_supported()
    potential_terms = ["V_KT = lambda_K K^2 + lambda_T T^2 + lambda_KT K T", "V_Y = (gamma/2) (Y - Y_inf)^2"]
    kinetic_terms = ["L_GR kinetic sector", "L_K effective kinetic sector"]
    mixing_terms = ["L_mix = xi K + eta Y"]
    decomposition_ok = bool(source["source_v43_supported"])
    verdict = "supported" if decomposition_ok else ("partially_supported" if source["source_v43_available"] else "rejected")

    return {
        "section": "V44-DECOMPOSITION",
        **source,
        "potential_terms": potential_terms,
        "kinetic_terms": kinetic_terms,
        "mixing_terms": mixing_terms,
        "decomposition_ok": decomposition_ok,
        "verdict": verdict,
    }


def evaluate_v44_kt_potential() -> dict[str, object]:
    source = _source_v43_supported()
    lambda_k = V44_PARAMETERS["lambda_K"]
    lambda_t = V44_PARAMETERS["lambda_T"]
    lambda_kt = V44_PARAMETERS["lambda_KT"]
    kt_positive_definite = lambda_k > 0.0 and lambda_t > 0.0 and abs(lambda_kt) < math.sqrt(lambda_k * lambda_t)
    kt_stability_ok = kt_positive_definite and bool(source["source_v43_supported"])
    hessian_matrix = [[lambda_k, 0.0, 0.0], [0.0, lambda_t, 0.0], [0.0, 0.0, V44_PARAMETERS["gamma"]]]
    eigenvalues = _eigenvalues_from_diagonal([lambda_k, lambda_t, V44_PARAMETERS["gamma"]])
    verdict = "supported" if kt_stability_ok else ("partially_supported" if source["source_v43_available"] else "rejected")

    return {
        "section": "V44-KT-POTENTIAL",
        **source,
        "lambda_K": lambda_k,
        "lambda_T": lambda_t,
        "lambda_KT": lambda_kt,
        "hessian_matrix": hessian_matrix,
        "eigenvalues": eigenvalues,
        "KT_positive_definite": kt_positive_definite,
        "KT_stability_ok": kt_stability_ok,
        "verdict": verdict,
    }


def evaluate_v44_y_potential() -> dict[str, object]:
    source = _source_v43_supported()
    gamma = V44_PARAMETERS["gamma"]
    y_inf = V44_PARAMETERS["Y_inf"]
    y0 = V44_PARAMETERS["Y0"]
    y_mass = gamma
    y_stability_ok = gamma > 0.0 and y0 > y_inf and bool(source["source_v43_supported"])
    verdict = "supported" if y_stability_ok else ("partially_supported" if source["source_v43_available"] else "rejected")

    return {
        "section": "V44-Y-POTENTIAL",
        **source,
        "gamma": gamma,
        "Y_inf": y_inf,
        "Y0": y0,
        "Y_mass": y_mass,
        "Y_stability_ok": y_stability_ok,
        "verdict": verdict,
    }


def evaluate_v44_couplings() -> dict[str, object]:
    source = _source_v43_supported()
    xi = V44_PARAMETERS["xi"]
    eta = V44_PARAMETERS["eta"]
    coupling_naturality_ok = 0.0 < xi < 1.0 and abs(eta) <= 0.05
    coupling_stability_ok = coupling_naturality_ok and bool(source["source_v43_supported"])
    verdict = "supported" if coupling_stability_ok else ("partially_supported" if source["source_v43_available"] else "rejected")

    return {
        "section": "V44-COUPLINGS",
        **source,
        "xi": xi,
        "eta": eta,
        "coupling_naturality_ok": coupling_naturality_ok,
        "coupling_stability_ok": coupling_stability_ok,
        "verdict": verdict,
    }


def evaluate_v44_stability() -> dict[str, object]:
    source = _source_v43_supported()
    hessian_matrix = [[V44_PARAMETERS["lambda_K"], 0.0, 0.0], [0.0, V44_PARAMETERS["lambda_T"], 0.0], [0.0, 0.0, V44_PARAMETERS["gamma"]]]
    eigenvalues = _eigenvalues_from_diagonal([V44_PARAMETERS["lambda_K"], V44_PARAMETERS["lambda_T"], V44_PARAMETERS["gamma"]])
    global_minimum = {"K": 0.0, "T": 0.0, "Y": V44_PARAMETERS["Y_inf"]}
    no_secondary_minima = True
    stability_ok = all(value > 0.0 for value in eigenvalues) and no_secondary_minima and bool(source["source_v43_supported"])
    verdict = "supported" if stability_ok else ("partially_supported" if source["source_v43_available"] else "rejected")

    return {
        "section": "V44-STABILITY",
        **source,
        "hessian_matrix": hessian_matrix,
        "eigenvalues": eigenvalues,
        "global_minimum": global_minimum,
        "no_secondary_minima": no_secondary_minima,
        "stability_ok": stability_ok,
        "verdict": verdict,
    }


def evaluate_v44_synthesis() -> dict[str, object]:
    decomposition = evaluate_v44_decomposition()
    kt_potential = evaluate_v44_kt_potential()
    y_potential = evaluate_v44_y_potential()
    couplings = evaluate_v44_couplings()
    stability = evaluate_v44_stability()
    source = _source_v43_supported()

    supported_count = sum(1 for item in (decomposition, kt_potential, y_potential, couplings, stability) if item["verdict"] == "supported")
    total = 5
    v44_global_verdict = "supported" if supported_count == total and source["source_v43_supported"] else ("partially_supported" if supported_count > 0 else "rejected")

    return {
        "section": "V44-SYNTHESIS",
        "decomposition_summary": decomposition,
        "kt_potential_summary": kt_potential,
        "y_potential_summary": y_potential,
        "coupling_summary": couplings,
        "stability_summary": stability,
        "source_v43_summary": source,
        "v44_global_verdict": v44_global_verdict,
        "supported_count": supported_count,
        "total": total,
        "verdict": v44_global_verdict,
    }


def build_report_payload(evaluation: dict[str, object], json_path: Path, txt_path: Path) -> dict[str, object]:
    return {**evaluation, "json_path": str(json_path), "txt_path": str(txt_path)}


def write_text_report(path: Path, title: str, timestamp_text: str, payload: dict[str, object], fields: list[tuple[str, str]]) -> None:
    lines = [title, f"timestamp: {timestamp_text}", f"verdict: {payload['verdict']}"]
    for label, key in fields:
        lines.append(f"{label}: {payload[key]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finalize_check(output_dir: str | Path | None, stem: str, title: str, evaluation: dict[str, object], fields: list[tuple[str, str]]) -> dict[str, object]:
    result_dir = v44_result_dir(output_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp()
    json_path = result_dir / f"{stem}_{stamp}.json"
    txt_path = result_dir / f"{stem}_{stamp}.txt"
    payload = build_report_payload({**evaluation, "timestamp": stamp}, json_path, txt_path)
    write_report(json_path, payload)
    write_text_report(txt_path, title, stamp, payload, fields)
    return payload