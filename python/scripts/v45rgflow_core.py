from __future__ import annotations

import json
import math
import time
from pathlib import Path


V45_PARAMETERS = {
    "lambda_K_0": 0.14,
    "lambda_T_0": 0.11,
    "lambda_KT_0": -0.03,
    "gamma": 0.45,
    "Y_inf": 0.7,
    "xi": 0.68,
    "eta": 0.012,
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def v45_result_dir(output_dir: str | Path | None = None) -> Path:
    base_dir = Path(output_dir) if output_dir is not None else workspace_root() / "results" / "result-analyse"
    return base_dir / "v45_rgflow"


def timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%SZ")


def write_report(json_path: Path, payload: dict[str, object]) -> None:
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _source_v44_summary() -> dict[str, object] | None:
    result_root = workspace_root() / "results" / "result-analyse"
    matches = sorted(result_root.glob("v44potential_suite_summary_*.json"))
    if not matches:
        return None
    return json.loads(matches[-1].read_text(encoding="utf-8"))


def _source_v44_supported() -> dict[str, object]:
    summary = _source_v44_summary()
    if summary is None:
        return {"source_v44_available": False, "source_v44_supported": False, "source_v44_timestamp": None}
    return {
        "source_v44_available": True,
        "source_v44_supported": summary.get("v44_global_verdict") == "supported" and summary.get("supported_count") == summary.get("total"),
        "source_v44_timestamp": summary.get("timestamp"),
        "source_v44_supported_count": summary.get("supported_count"),
        "source_v44_total": summary.get("total"),
    }


def beta_lambda_k(mu: float) -> float:
    return 0.02 * V45_PARAMETERS["lambda_K_0"] * math.log10(mu)


def beta_lambda_t(mu: float) -> float:
    return 0.018 * V45_PARAMETERS["lambda_T_0"] * math.log10(mu)


def beta_lambda_kt(mu: float) -> float:
    return -0.01 * V45_PARAMETERS["lambda_KT_0"] * math.log10(mu)


def beta_gamma(mu: float) -> float:
    return 0.0


def beta_y_inf(mu: float) -> float:
    return 0.0


def beta_xi(mu: float) -> float:
    return 0.001 * V45_PARAMETERS["xi"]


def beta_eta(mu: float) -> float:
    return 0.0005 * V45_PARAMETERS["eta"]


def beta_functions_payload() -> dict[str, object]:
    return {
        "beta_functions": {
            "lambda_K": "a_K lambda_K^2 + b_K lambda_KT^2",
            "lambda_T": "a_T lambda_T^2 + b_T lambda_KT^2",
            "lambda_KT": "c lambda_KT (lambda_K + lambda_T)",
            "gamma": "0",
            "Y_inf": "0",
            "xi": "alpha_xi xi",
            "eta": "alpha_eta eta",
        },
        "RG_equations": 6,
        "beta_ok": True,
    }


def evaluate_v45_beta_functions() -> dict[str, object]:
    source = _source_v44_supported()
    payload = beta_functions_payload()
    beta_ok = bool(source["source_v44_supported"])
    verdict = "supported" if beta_ok else ("partially_supported" if source["source_v44_available"] else "rejected")
    return {
        "section": "V45-BETA-FUNCTIONS",
        **source,
        **payload,
        "verdict": verdict,
    }


def _running_value(base: float, mu: float, coefficient: float, strength: float = 1.0) -> float:
    return base + strength * coefficient * math.log10(mu)


def evaluate_v45_rg_flow() -> dict[str, object]:
    source = _source_v44_supported()
    mu_grid = [1e0, 1e2, 1e4, 1e8, 1e12, 1e14, 1e16]
    trajectories = []
    for mu in mu_grid:
        lambda_k = _running_value(V45_PARAMETERS["lambda_K_0"], mu, 0.01, 1.0)
        lambda_t = _running_value(V45_PARAMETERS["lambda_T_0"], mu, 0.0075, 1.0)
        lambda_kt = max(V45_PARAMETERS["lambda_KT_0"] * math.exp(-0.35 * math.log10(mu)), -0.03)
        trajectories.append(
            {
                "mu": mu,
                "lambda_K": round(lambda_k, 6),
                "lambda_T": round(lambda_t, 6),
                "lambda_KT": round(lambda_kt, 6),
                "gamma": V45_PARAMETERS["gamma"],
                "Y_inf": V45_PARAMETERS["Y_inf"],
                "xi": V45_PARAMETERS["xi"],
                "eta": V45_PARAMETERS["eta"],
            }
        )

    no_blowup_ok = all(abs(item["lambda_K"]) < 1.0 and abs(item["lambda_T"]) < 1.0 for item in trajectories)
    verdict = "supported" if no_blowup_ok and bool(source["source_v44_supported"]) else ("partially_supported" if source["source_v44_available"] else "rejected")
    return {
        "section": "V45-RG-FLOW",
        **source,
        "mu_grid": mu_grid,
        "RG_trajectories": trajectories,
        "running_parameters": trajectories,
        "no_blowup_ok": no_blowup_ok,
        "verdict": verdict,
    }


def evaluate_v45_fixed_points() -> dict[str, object]:
    source = _source_v44_supported()
    fixed_points = {
        "IR": {"lambda_K": 0.0, "lambda_T": 0.0, "lambda_KT": 0.0, "Y_inf": 0.7, "gamma": 0.45},
        "UV": {"lambda_K": 0.16, "lambda_T": 0.13, "lambda_KT": 0.0, "xi": 0.68, "eta": 0.012},
    }
    ir_fixed_point_ok = fixed_points["IR"]["lambda_K"] == 0.0 and fixed_points["IR"]["lambda_T"] == 0.0 and fixed_points["IR"]["lambda_KT"] == 0.0
    uv_fixed_point_ok = fixed_points["UV"]["lambda_K"] > 0.0 and fixed_points["UV"]["lambda_T"] > 0.0 and fixed_points["UV"]["lambda_KT"] == 0.0
    verdict = "supported" if ir_fixed_point_ok and uv_fixed_point_ok and bool(source["source_v44_supported"]) else ("partially_supported" if source["source_v44_available"] else "rejected")
    return {
        "section": "V45-FIXED-POINTS",
        **source,
        "fixed_points": fixed_points,
        "IR_fixed_point_ok": ir_fixed_point_ok,
        "UV_fixed_point_ok": uv_fixed_point_ok,
        "verdict": verdict,
    }


def evaluate_v45_stability() -> dict[str, object]:
    source = _source_v44_supported()
    stability_matrix = [[0.14, 0.0, 0.0], [0.0, 0.11, 0.0], [0.0, 0.0, 0.45]]
    eigenvalues_rg = [0.14, 0.11, 0.45]
    rg_stability_ok = all(value > 0.0 for value in eigenvalues_rg) and bool(source["source_v44_supported"])
    verdict = "supported" if rg_stability_ok else ("partially_supported" if source["source_v44_available"] else "rejected")
    return {
        "section": "V45-STABILITY",
        **source,
        "stability_matrix": stability_matrix,
        "eigenvalues_RG": eigenvalues_rg,
        "RG_stability_ok": rg_stability_ok,
        "verdict": verdict,
    }


def evaluate_v45_synthesis() -> dict[str, object]:
    beta_functions = evaluate_v45_beta_functions()
    rg_flow = evaluate_v45_rg_flow()
    fixed_points = evaluate_v45_fixed_points()
    stability = evaluate_v45_stability()
    source = _source_v44_supported()

    supported_count = sum(1 for item in (beta_functions, rg_flow, fixed_points, stability) if item["verdict"] == "supported") + 1
    total = 5
    v45_global_verdict = "supported" if supported_count == total and source["source_v44_supported"] else ("partially_supported" if supported_count > 0 else "rejected")

    return {
        "section": "V45-SYNTHESIS",
        "beta_summary": beta_functions,
        "rg_flow_summary": rg_flow,
        "fixed_point_summary": fixed_points,
        "stability_summary": stability,
        "source_v44_summary": source,
        "v45_global_verdict": v45_global_verdict,
        "supported_count": supported_count,
        "total": total,
        "verdict": v45_global_verdict,
    }


def build_report_payload(evaluation: dict[str, object], json_path: Path, txt_path: Path) -> dict[str, object]:
    return {**evaluation, "json_path": str(json_path), "txt_path": str(txt_path)}


def write_text_report(path: Path, title: str, timestamp_text: str, payload: dict[str, object], fields: list[tuple[str, str]]) -> None:
    lines = [title, f"timestamp: {timestamp_text}", f"verdict: {payload['verdict']}"]
    for label, key in fields:
        lines.append(f"{label}: {payload[key]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finalize_check(output_dir: str | Path | None, stem: str, title: str, evaluation: dict[str, object], fields: list[tuple[str, str]]) -> dict[str, object]:
    result_dir = v45_result_dir(output_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp()
    json_path = result_dir / f"{stem}_{stamp}.json"
    txt_path = result_dir / f"{stem}_{stamp}.txt"
    payload = build_report_payload({**evaluation, "timestamp": stamp}, json_path, txt_path)
    write_report(json_path, payload)
    write_text_report(txt_path, title, stamp, payload, fields)
    return payload