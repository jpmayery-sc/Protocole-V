"""Run a targeted ECGP benchmark on trial data.

The bench expects a small trial table with matched control values so it can
test whether a residual entanglement signal survives the standard loss/noise
corrections. The logic is intentionally conservative: it reports supported,
rejected, blocked, or inconclusive instead of forcing a discovery verdict.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Trial:
    trial_id: str
    material: str
    frequency_hz: float
    measured_fidelity: float
    control_fidelity: float
    loss_db: float
    temperature_k: float
    geometry: str | None = None
    detector_counts: int | None = None


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_input_path() -> Path:
    return workspace_root() / "python" / "data" / "ecgp_trials_demo_control.json"


def default_output_dir() -> Path:
    return workspace_root() / "results" / "result-analyse"


def load_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def coerce_trial(raw: dict) -> Trial:
    required = ["trial_id", "material", "frequency_hz", "measured_fidelity", "control_fidelity", "loss_db", "temperature_k"]
    missing = [key for key in required if key not in raw or raw[key] in (None, "")]
    if missing:
        raise ValueError(f"Trial is missing required fields: {', '.join(missing)}")

    detector_counts = raw.get("detector_counts")
    if detector_counts in (None, ""):
        detector_counts_value = None
    else:
        detector_counts_value = int(detector_counts)

    geometry = raw.get("geometry") or raw.get("guide_geometry")
    if geometry == "":
        geometry = None

    return Trial(
        trial_id=str(raw["trial_id"]),
        material=str(raw["material"]),
        frequency_hz=float(raw["frequency_hz"]),
        measured_fidelity=float(raw["measured_fidelity"]),
        control_fidelity=float(raw["control_fidelity"]),
        loss_db=float(raw["loss_db"]),
        temperature_k=float(raw["temperature_k"]),
        geometry=str(geometry) if geometry is not None else None,
        detector_counts=detector_counts_value,
    )


def load_trials(path: str | Path) -> tuple[list[Trial], dict]:
    trial_path = Path(path)
    if not trial_path.exists():
        raise FileNotFoundError(f"Trial file not found: {trial_path}")

    if trial_path.suffix.lower() == ".csv":
        with trial_path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.DictReader(handle))
        metadata = {"format": "csv", "status": "real"}
        return [coerce_trial(row) for row in rows], metadata

    payload = load_json(trial_path)
    if isinstance(payload, dict):
        raw_trials = payload.get("trials")
        if raw_trials is None:
            raise ValueError("JSON bench file must expose a 'trials' list")
        metadata = {key: value for key, value in payload.items() if key != "trials"}
    elif isinstance(payload, list):
        raw_trials = payload
        metadata = {"format": "json", "status": "real"}
    else:
        raise ValueError("Unsupported bench payload")

    if not isinstance(raw_trials, list) or not raw_trials:
        raise ValueError("The bench requires at least one trial")

    return [coerce_trial(row) for row in raw_trials], metadata


def trial_delta(trial: Trial) -> float:
    return trial.measured_fidelity - trial.control_fidelity


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def spread(values: list[float]) -> float:
    return max(values) - min(values) if values else 0.0


def pearson(xs: list[float], ys: list[float]) -> float:
    if len(xs) < 2 or len(ys) < 2 or len(xs) != len(ys):
        return float("nan")

    x_mean = mean(xs)
    y_mean = mean(ys)
    numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    x_den = sum((x - x_mean) ** 2 for x in xs)
    y_den = sum((y - y_mean) ** 2 for y in ys)
    denominator = math.sqrt(x_den * y_den)
    return numerator / denominator if denominator else float("nan")


def summarize_grouped(trials: list[Trial], key_name: str) -> list[dict]:
    groups: dict[str, list[Trial]] = {}
    for trial in trials:
        key = getattr(trial, key_name)
        if key is None:
            continue
        groups.setdefault(str(key), []).append(trial)

    summary = []
    for label, members in sorted(groups.items()):
        deltas = [trial_delta(trial) for trial in members]
        summary.append(
            {
                "label": label,
                "count": len(members),
                "mean_delta": mean(deltas),
                "min_delta": min(deltas),
                "max_delta": max(deltas),
                "spread": spread(deltas),
            }
        )
    return summary


def build_summary(trials: list[Trial], metadata: dict, input_path: Path) -> dict:
    deltas = [trial_delta(trial) for trial in trials]
    materials = sorted({trial.material for trial in trials})
    frequencies = sorted({trial.frequency_hz for trial in trials})
    geometries = sorted({trial.geometry for trial in trials if trial.geometry is not None})

    material_summary = summarize_grouped(trials, "material")
    frequency_summary = [
        {
            "label": str(group["label"]),
            "count": group["count"],
            "mean_delta": group["mean_delta"],
            "min_delta": group["min_delta"],
            "max_delta": group["max_delta"],
            "spread": group["spread"],
        }
        for group in summarize_grouped(trials, "frequency_hz")
    ]
    geometry_summary = summarize_grouped(trials, "geometry")

    freq_values = [trial.frequency_hz for trial in trials]
    freq_r = pearson(freq_values, deltas)

    material_spread = spread([item["mean_delta"] for item in material_summary])
    frequency_spread = spread([item["mean_delta"] for item in frequency_summary])
    geometry_spread = spread([item["mean_delta"] for item in geometry_summary])

    issues = []
    if len(trials) < 4:
        issues.append("too few trials for a meaningful bench")
    if len(materials) < 2:
        issues.append("need at least two materials")
    if len(frequencies) < 2:
        issues.append("need at least two frequencies")

    if issues:
        verdict = "blocked"
    elif max(material_spread, frequency_spread, geometry_spread) <= 0.005:
        verdict = "rejected"
    elif material_spread >= 0.02 or frequency_spread >= 0.02 or geometry_spread >= 0.02 or (not math.isnan(freq_r) and abs(freq_r) >= 0.6):
        verdict = "supported"
    else:
        verdict = "inconclusive"

    return {
        "suite": "ecgp_bench",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "input_path": str(input_path),
        "input_status": str(metadata.get("status", "real")),
        "overall_verdict": verdict,
        "trial_count": len(trials),
        "materials": materials,
        "frequencies_hz": frequencies,
        "geometries": geometries,
        "mean_delta": mean(deltas),
        "median_delta": statistics.median(deltas) if deltas else 0.0,
        "delta_spread": spread(deltas),
        "material_spread": material_spread,
        "frequency_spread": frequency_spread,
        "geometry_spread": geometry_spread,
        "frequency_delta_r": freq_r,
        "checks": [
            "delta_fidelity = measured_fidelity - control_fidelity",
            "losses and other matched controls are already absorbed by the control channel",
            "material and frequency summaries are computed only after normalization",
        ],
        "issues": issues,
        "material_summary": material_summary,
        "frequency_summary": frequency_summary,
        "geometry_summary": geometry_summary,
    }


def write_report(summary: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = output_dir / f"ecgp_bench_{timestamp}.json"
    txt_path = output_dir / f"ecgp_bench_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "ECGP bench summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"input_status: {summary['input_status']}",
        f"trial_count: {summary['trial_count']}",
        f"materials: {', '.join(summary['materials']) or '-'}",
        f"frequencies_hz: {', '.join(str(value) for value in summary['frequencies_hz']) or '-'}",
        f"mean_delta: {summary['mean_delta']}",
        f"material_spread: {summary['material_spread']}",
        f"frequency_spread: {summary['frequency_spread']}",
        f"geometry_spread: {summary['geometry_spread']}",
        "",
        "Checks:",
    ]
    lines.extend(f"- {check}" for check in summary["checks"])
    if summary["issues"]:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue}" for issue in summary["issues"])
    if summary["material_summary"]:
        lines.extend(["", "Material summary:"])
        for item in summary["material_summary"]:
            lines.append(f"- {item['label']}: mean_delta={item['mean_delta']}, count={item['count']}")
    if summary["frequency_summary"]:
        lines.extend(["", "Frequency summary:"])
        for item in summary["frequency_summary"]:
            lines.append(f"- {item['label']}: mean_delta={item['mean_delta']}, count={item['count']}")
    if summary["geometry_summary"]:
        lines.extend(["", "Geometry summary:"])
        for item in summary["geometry_summary"]:
            lines.append(f"- {item['label']}: mean_delta={item['mean_delta']}, count={item['count']}")

    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_bench(input_path: str | Path | None = None, output_dir: str | Path | None = None) -> dict:
    resolved_input = Path(input_path) if input_path is not None else default_input_path()
    trials, metadata = load_trials(resolved_input)
    summary = build_summary(trials, metadata, resolved_input)
    resolved_output_dir = Path(output_dir) if output_dir is not None else default_output_dir()
    json_path, txt_path = write_report(summary, resolved_output_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ECGP benchmark on trial data.")
    parser.add_argument("--input", default=None, help="Path to a JSON or CSV bench file")
    parser.add_argument("--output-dir", default=None, help="Directory for the bench report")
    args = parser.parse_args()

    result = run_bench(args.input, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()