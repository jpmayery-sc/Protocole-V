"""Leave-one-system-out collapse check for the opening protocol.

The script uses three PySSPFM loops as the collapse family and ManualLOOP as
the negative control. It holds one family member out, builds the reduced master
curve from the remaining family members, and checks whether the held-out curve
still stays closer to the family than to the control.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import json
import math
import statistics
import time
import urllib.request
from pathlib import Path
import re


MANUALLOOP_DATA_URL = "https://raw.githubusercontent.com/ZhiweiXu-102307/ManualLOOP/main/outputs/data/1.csv"
PYSSPFM_OFF_URL = (
    "https://raw.githubusercontent.com/CEA-MetroCarac/PySSPFM/main/examples/data/"
    "PySSPFM_example_in/KNN500n_2023-11-20-16h18m_out_dfrt/nanoloops/"
    "off_f_KNN500n_SSPFM.0_00056.txt"
)
PYSSPFM_ON_URL = (
    "https://raw.githubusercontent.com/CEA-MetroCarac/PySSPFM/main/examples/data/"
    "PySSPFM_example_in/KNN500n_2023-11-20-16h18m_out_dfrt/nanoloops/"
    "on_f_KNN500n_SSPFM.0_00056.txt"
)
PYSSPFM_THIRD_URL = (
    "https://raw.githubusercontent.com/CEA-MetroCarac/PySSPFM/main/examples/data/"
    "PySSPFM_example_in/KNN500n_2023-11-20-16h18m_out_dfrt/nanoloops/"
    "off_f_KNN500n_SSPFM.0_00058.txt"
)

FLOAT_PATTERN = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
COLLAPSE_GRID = [-2.5 + 5.0 * index / 250.0 for index in range(251)]


@dataclass(frozen=True)
class XYSource:
    name: str
    location: str
    x_index: int
    y_index: int
    delimiter: str | None = None


def read_text(location: str) -> str:
    request = urllib.request.Request(location, headers={"User-Agent": "Mozilla/5.0"}) if location.startswith(("http://", "https://")) else None
    if request is not None:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")

    return Path(location).read_text(encoding="utf-8")


def parse_numeric_tokens(line: str) -> list[float]:
    return [float(token) for token in FLOAT_PATTERN.findall(line)]


def load_xy_points(source: XYSource) -> list[tuple[float, float]]:
    text = read_text(source.location)
    points: list[tuple[float, float]] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if source.delimiter is not None:
            line = line.replace(source.delimiter, " ")

        values = parse_numeric_tokens(line)
        if len(values) <= max(source.x_index, source.y_index):
            continue

        points.append((values[source.x_index], values[source.y_index]))

    if len(points) < 8:
        raise ValueError(f"{source.name}: not enough numeric points found")

    return points


def interpolate_curve(xs: list[float], ys: list[float], probe: float) -> float:
    if probe <= xs[0]:
        return ys[0]
    if probe >= xs[-1]:
        return ys[-1]

    lower = 0
    upper = len(xs) - 1
    while upper - lower > 1:
        middle = (lower + upper) // 2
        if xs[middle] <= probe:
            lower = middle
        else:
            upper = middle

    x0 = xs[lower]
    x1 = xs[upper]
    y0 = ys[lower]
    y1 = ys[upper]
    if x1 == x0:
        return y0

    weight = (probe - x0) / (x1 - x0)
    return y0 + weight * (y1 - y0)


def normalize_curve(points: list[tuple[float, float]]) -> dict[str, list[float] | dict[str, float]]:
    xs = [x for x, _ in points]
    ys = [y for _, y in points]

    x_center = statistics.mean(xs)
    y_center = statistics.mean(ys)
    x_span = max(xs) - min(xs)
    y_span = max(ys) - min(ys)
    x_scale = max(x_span / 2.0, 1.0e-9)
    y_scale = max(y_span / 2.0, 1.0e-9)

    return {
        "reduced_x": [(x - x_center) / x_scale for x in xs],
        "reduced_y": [(y - y_center) / y_scale for y in ys],
        "center": {"x": x_center, "y": y_center},
        "scale": {"x": x_scale, "y": y_scale},
    }


def collapse_rmse(curve_a: dict, curve_b: dict, grid: list[float]) -> float:
    values_a = [interpolate_curve(curve_a["reduced_x"], curve_a["reduced_y"], probe) for probe in grid]
    values_b = [interpolate_curve(curve_b["reduced_x"], curve_b["reduced_y"], probe) for probe in grid]
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(values_a, values_b)) / len(grid))


def average_master(curves: list[dict]) -> dict:
    averaged_y = []
    for probe in COLLAPSE_GRID:
        values = [interpolate_curve(curve["reduced_x"], curve["reduced_y"], probe) for curve in curves]
        averaged_y.append(statistics.mean(values))
    return {"reduced_x": COLLAPSE_GRID[:], "reduced_y": averaged_y}


def build_sources() -> tuple[XYSource, XYSource, XYSource, XYSource]:
    return (
        XYSource(name="ManualLOOP CSV", location=MANUALLOOP_DATA_URL, x_index=0, y_index=1, delimiter=","),
        XYSource(name="PySSPFM off_f loop", location=PYSSPFM_OFF_URL, x_index=2, y_index=3),
        XYSource(name="PySSPFM on_f loop", location=PYSSPFM_ON_URL, x_index=2, y_index=3),
        XYSource(name="PySSPFM third off_f loop", location=PYSSPFM_THIRD_URL, x_index=2, y_index=3),
    )


def run_leave_one_out() -> dict:
    manualloop_source, pysspfm_off_source, pysspfm_on_source, pysspfm_third_source = build_sources()

    manualloop_curve = normalize_curve(load_xy_points(manualloop_source))
    pysspfm_off_curve = normalize_curve(load_xy_points(pysspfm_off_source))
    pysspfm_on_curve = normalize_curve(load_xy_points(pysspfm_on_source))
    pysspfm_third_curve = normalize_curve(load_xy_points(pysspfm_third_source))

    family_curves = {
        "pysspfm_off": pysspfm_off_curve,
        "pysspfm_on": pysspfm_on_curve,
        "pysspfm_third": pysspfm_third_curve,
    }
    control_curve = manualloop_curve

    fold_results = []
    for held_out_name, held_out_curve in family_curves.items():
        train_curves = [curve for name, curve in family_curves.items() if name != held_out_name]
        master_curve = average_master(train_curves)
        held_out_rmse = collapse_rmse(held_out_curve, master_curve, COLLAPSE_GRID)
        control_rmse = collapse_rmse(held_out_curve, control_curve, COLLAPSE_GRID)
        train_rmse = collapse_rmse(train_curves[0], master_curve, COLLAPSE_GRID)

        fold_results.append(
            {
                "held_out": held_out_name,
                "train_family": [name for name in family_curves if name != held_out_name],
                "train_rmse": train_rmse,
                "held_out_rmse": held_out_rmse,
                "control_rmse": control_rmse,
                "margin_vs_control": control_rmse - held_out_rmse,
                "generalization_ok": held_out_rmse < control_rmse,
            }
        )

    overall_ok = all(fold["generalization_ok"] for fold in fold_results)
    return {
        "overall_verdict": "conforme strict" if overall_ok else "falsifie",
        "control": "ManualLOOP",
        "folds": fold_results,
        "summary": {
            "mean_held_out_rmse": statistics.mean(fold["held_out_rmse"] for fold in fold_results),
            "mean_control_rmse": statistics.mean(fold["control_rmse"] for fold in fold_results),
            "mean_margin": statistics.mean(fold["margin_vs_control"] for fold in fold_results),
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Leave-one-system-out collapse check for the opening protocol.")
    _ = parser.parse_args()

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    results = run_leave_one_out()

    json_path = results_dir / f"leave_one_out_collapse_{timestamp}.json"
    txt_path = results_dir / f"leave_one_out_collapse_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Leave-one-system-out collapse check\n")
        handle.write(f"Timestamp: {timestamp}\n")
        handle.write(f"Control: {results['control']}\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n")
        handle.write(f"Mean held-out RMSE: {results['summary']['mean_held_out_rmse']:.6f}\n")
        handle.write(f"Mean control RMSE: {results['summary']['mean_control_rmse']:.6f}\n")
        handle.write(f"Mean margin: {results['summary']['mean_margin']:.6f}\n\n")
        for fold in results["folds"]:
            handle.write(f"Held out: {fold['held_out']}\n")
            handle.write(f"  train family: {', '.join(fold['train_family'])}\n")
            handle.write(f"  train RMSE: {fold['train_rmse']:.6f}\n")
            handle.write(f"  held-out RMSE: {fold['held_out_rmse']:.6f}\n")
            handle.write(f"  control RMSE: {fold['control_rmse']:.6f}\n")
            handle.write(f"  margin vs control: {fold['margin_vs_control']:.6f}\n")
            handle.write(f"  generalization: {'ok' if fold['generalization_ok'] else 'falsifie'}\n\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()