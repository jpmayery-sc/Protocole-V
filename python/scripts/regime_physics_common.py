"""Shared helpers for the regime-physics test skeleton."""
from __future__ import annotations

import json
import time
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def latest_report(result_dir: Path, stem: str) -> Path:
    matches = sorted(result_dir.glob(f"{stem}_*.json"))
    if not matches:
        raise FileNotFoundError(f"No report found for {stem} in {result_dir}")
    return matches[-1]


def write_report(title: str, stem: str, payload: dict, output_dir: str | Path | None = None) -> tuple[Path, Path]:
    result_dir = Path(output_dir) if output_dir is not None else workspace_root() / "python" / "results" / "regime_physics"
    result_dir.mkdir(parents=True, exist_ok=True)

    timestamp = payload.get("timestamp") or time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"{stem}_{timestamp}.json"
    txt_path = result_dir / f"{stem}_{timestamp}.txt"

    payload = {**payload, "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        title,
        f"timestamp: {timestamp}",
        f"verdict: {payload.get('verdict', 'unknown')}",
    ]
    for key in ("regime", "dominant_grid", "hypothesis", "case_control", "observable"):
        value = payload.get(key)
        if value is not None:
            lines.append(f"{key}: {value}")

    checks = payload.get("checks") or []
    if checks:
        lines.append("")
        lines.append("Checks:")
        lines.extend(f"- {check}" for check in checks)

    cases = payload.get("cases") or []
    if cases:
        lines.append("")
        lines.append("Cases:")
        for case in cases:
            case_label = case.get("symbol") or case.get("label") or "case"
            verdict = case.get("verdict") or case.get("ok")
            lines.append(f"- {case_label}: {verdict}")

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path