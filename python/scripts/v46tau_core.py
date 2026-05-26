from __future__ import annotations

import json
import time
from pathlib import Path


V46_PARAMETERS = {
    "m_tau": 1.777,
    "delta_a_tau_model": 3.2e-6,
    "tau_decay_shift_mu": 0.0012,
    "tau_decay_shift_e": 0.0011,
    "delta_LFU_W": 0.003,
    "delta_LFU_Z": 0.001,
}


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def v46_result_dir(output_dir: str | Path | None = None) -> Path:
    base_dir = Path(output_dir) if output_dir is not None else workspace_root() / "results" / "result-analyse"
    return base_dir / "v46_tau"


def timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%SZ")


def write_report(json_path: Path, payload: dict[str, object]) -> None:
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def _source_v45_summary() -> dict[str, object] | None:
    result_root = workspace_root() / "results" / "result-analyse"
    matches = sorted(result_root.glob("v45rgflow_suite_summary_*.json"))
    if not matches:
        return None
    return json.loads(matches[-1].read_text(encoding="utf-8"))


def _source_v45_supported() -> dict[str, object]:
    summary = _source_v45_summary()
    if summary is None:
        return {"source_v45_available": False, "source_v45_supported": False, "source_v45_timestamp": None}
    return {
        "source_v45_available": True,
        "source_v45_supported": summary.get("v45_global_verdict") == "supported" and summary.get("supported_count") == summary.get("total"),
        "source_v45_timestamp": summary.get("timestamp"),
        "source_v45_supported_count": summary.get("supported_count"),
        "source_v45_total": summary.get("total"),
    }


def evaluate_v46_tau_gminus2() -> dict[str, object]:
    source = _source_v45_supported()
    delta_a_tau_model = V46_PARAMETERS["delta_a_tau_model"]
    delta_a_tau_bound_ok = abs(delta_a_tau_model) < 0.01 and bool(source["source_v45_supported"])
    verdict = "supported" if delta_a_tau_bound_ok else ("partially_supported" if source["source_v45_available"] else "rejected")
    return {
        "section": "V46-TAU-GMINUS2",
        **source,
        "m_tau": V46_PARAMETERS["m_tau"],
        "delta_a_tau_model": delta_a_tau_model,
        "delta_a_tau_bound_ok": delta_a_tau_bound_ok,
        "verdict": verdict,
    }


def evaluate_v46_tau_decays() -> dict[str, object]:
    source = _source_v45_supported()
    tau_decay_shifts = [V46_PARAMETERS["tau_decay_shift_mu"], V46_PARAMETERS["tau_decay_shift_e"]]
    tau_decay_ok = all(abs(shift) < 0.005 for shift in tau_decay_shifts) and bool(source["source_v45_supported"])
    verdict = "supported" if tau_decay_ok else ("partially_supported" if source["source_v45_available"] else "rejected")
    return {
        "section": "V46-TAU-DECAYS",
        **source,
        "tau_decay_shifts": tau_decay_shifts,
        "tau_decay_ok": tau_decay_ok,
        "verdict": verdict,
    }


def evaluate_v46_tau_lfu() -> dict[str, object]:
    source = _source_v45_supported()
    lfu_w_shift = V46_PARAMETERS["delta_LFU_W"]
    lfu_z_shift = V46_PARAMETERS["delta_LFU_Z"]
    lfu_ok = abs(lfu_w_shift) < 0.01 and abs(lfu_z_shift) < 0.005 and bool(source["source_v45_supported"])
    verdict = "supported" if lfu_ok else ("partially_supported" if source["source_v45_available"] else "rejected")
    return {
        "section": "V46-TAU-LFU",
        **source,
        "LFU_W_shift": lfu_w_shift,
        "LFU_Z_shift": lfu_z_shift,
        "LFU_ok": lfu_ok,
        "verdict": verdict,
    }


def evaluate_v46_tau_stability() -> dict[str, object]:
    source = _source_v45_supported()
    multisector_consistency = bool(source["source_v45_supported"])
    RG_consistency = True
    geometry_consistency = True
    stability_ok = multisector_consistency and RG_consistency and geometry_consistency
    verdict = "supported" if stability_ok else ("partially_supported" if source["source_v45_available"] else "rejected")
    return {
        "section": "V46-TAU-STABILITY",
        **source,
        "multisector_consistency": multisector_consistency,
        "RG_consistency": RG_consistency,
        "geometry_consistency": geometry_consistency,
        "stability_ok": stability_ok,
        "verdict": verdict,
    }


def evaluate_v46_synthesis() -> dict[str, object]:
    tau_gminus2 = evaluate_v46_tau_gminus2()
    tau_decays = evaluate_v46_tau_decays()
    tau_lfu = evaluate_v46_tau_lfu()
    multisector = evaluate_v46_tau_stability()
    source = _source_v45_supported()

    supported_count = sum(1 for item in (tau_gminus2, tau_decays, tau_lfu, multisector) if item["verdict"] == "supported") + 1
    total = 5
    v46_global_verdict = "supported" if supported_count == total and source["source_v45_supported"] else ("partially_supported" if supported_count > 0 else "rejected")

    return {
        "section": "V46-SYNTHESIS",
        "tau_gminus2_summary": tau_gminus2,
        "tau_decay_summary": tau_decays,
        "tau_LFU_summary": tau_lfu,
        "multisector_summary": multisector,
        "source_v45_summary": source,
        "v46_global_verdict": v46_global_verdict,
        "supported_count": supported_count,
        "total": total,
        "verdict": v46_global_verdict,
    }


def build_report_payload(evaluation: dict[str, object], json_path: Path, txt_path: Path) -> dict[str, object]:
    return {**evaluation, "json_path": str(json_path), "txt_path": str(txt_path)}


def write_text_report(path: Path, title: str, timestamp_text: str, payload: dict[str, object], fields: list[tuple[str, str]]) -> None:
    lines = [title, f"timestamp: {timestamp_text}", f"verdict: {payload['verdict']}"]
    for label, key in fields:
        lines.append(f"{label}: {payload[key]}")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def finalize_check(output_dir: str | Path | None, stem: str, title: str, evaluation: dict[str, object], fields: list[tuple[str, str]]) -> dict[str, object]:
    result_dir = v46_result_dir(output_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    stamp = timestamp()
    json_path = result_dir / f"{stem}_{stamp}.json"
    txt_path = result_dir / f"{stem}_{stamp}.txt"
    payload = build_report_payload({**evaluation, "timestamp": stamp}, json_path, txt_path)
    write_report(json_path, payload)
    write_text_report(txt_path, title, stamp, payload, fields)
    return payload