"""Check the opening protocol on real datasets.

The script reads three public datasets:
- a mechanical hysteresis loop from ManualLOOP,
- a temperature-dependent resonance table from NQR_Frequency_Temp_Dep,
- ferroelectric loop traces from PySSPFM.

It measures three phenomena:
- hysteresis / memory via loop area and branch separation,
- temperature-dependent threshold shift via the resonance table,
- reduced-variable collapse across two real loop traces.

It writes a timestamped JSON summary and a short text report under results/.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import re
import statistics
import time
import urllib.request
from pathlib import Path


MANUALLOOP_DATA_URL = "https://raw.githubusercontent.com/ZhiweiXu-102307/ManualLOOP/main/outputs/data/1.csv"
TEMPDEP_DATA_URL = "https://raw.githubusercontent.com/shahjahanIqbal/NQR_Frequency_Temp_Dep/main/TempDep.csv"
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

FLOAT_PATTERN = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")
COLLAPSE_GRID = [-2.5 + 5.0 * index / 250.0 for index in range(251)]


@dataclass(frozen=True)
class XYSource:
    name: str
    location: str
    x_index: int
    y_index: int
    delimiter: str | None = None


@dataclass(frozen=True)
class TemperatureSource:
    name: str
    location: str
    temperature_index: int
    frequency_index: int
    delimiter: str | None = ","


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


def load_temperature_points(source: TemperatureSource) -> list[tuple[float, float]]:
    text = read_text(source.location)
    points: list[tuple[float, float]] = []

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if source.delimiter is not None:
            line = line.replace(source.delimiter, " ")

        values = parse_numeric_tokens(line)
        if len(values) <= max(source.temperature_index, source.frequency_index):
            continue

        points.append((values[source.temperature_index], values[source.frequency_index]))

    if len(points) < 8:
        raise ValueError(f"{source.name}: not enough numeric points found")

    return sorted(points)


def polyfit_line(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    covariance = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    variance = sum((x - x_mean) ** 2 for x in xs)
    slope = covariance / variance if variance else 0.0
    intercept = y_mean - slope * x_mean
    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    rmse = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    return slope, intercept, rmse


def normalize_curve(points: list[tuple[float, float]]) -> dict:
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


def loop_area(points: list[tuple[float, float]]) -> float:
    if len(points) < 3:
        return float("nan")

    closed = points + [points[0]]
    area = 0.0
    for index in range(len(points)):
        x0, y0 = closed[index]
        x1, y1 = closed[index + 1]
        area += x0 * y1 - x1 * y0

    return abs(area) * 0.5


def branch_gap(points: list[tuple[float, float]]) -> float:
    half = len(points) // 2
    forward = sorted(points[:half])
    reverse = sorted(points[half:])
    if len(forward) < 2 or len(reverse) < 2:
        return float("nan")

    lower = max(forward[0][0], reverse[0][0])
    upper = min(forward[-1][0], reverse[-1][0])
    if upper <= lower:
        return float("nan")

    probes = [lower + (upper - lower) * index / 12.0 for index in range(13)]
    gaps = []
    forward_xs = [x for x, _ in forward]
    forward_ys = [y for _, y in forward]
    reverse_xs = [x for x, _ in reverse]
    reverse_ys = [y for _, y in reverse]

    for probe in probes:
        y_forward = interpolate_curve(forward_xs, forward_ys, probe)
        y_reverse = interpolate_curve(reverse_xs, reverse_ys, probe)
        gaps.append(abs(y_forward - y_reverse))

    return statistics.mean(gaps)


def collapse_rmse(curve_a: dict, curve_b: dict, grid: list[float]) -> float:
    values_a = [interpolate_curve(curve_a["reduced_x"], curve_a["reduced_y"], probe) for probe in grid]
    values_b = [interpolate_curve(curve_b["reduced_x"], curve_b["reduced_y"], probe) for probe in grid]
    return math.sqrt(sum((left - right) ** 2 for left, right in zip(values_a, values_b)) / len(grid))


def analyze_hysteresis(points: list[tuple[float, float]], label: str) -> dict:
    return {
        "label": label,
        "n_points": len(points),
        "loop_area": loop_area(points),
        "branch_gap": branch_gap(points),
        "x_range": [min(x for x, _ in points), max(x for x, _ in points)],
        "y_range": [min(y for _, y in points), max(y for _, y in points)],
    }


def analyze_temperature_dependency(points: list[tuple[float, float]], label: str) -> dict:
    temperatures = [temperature for temperature, _ in points]
    frequencies = [frequency for _, frequency in points]

    slope, intercept, rmse = polyfit_line(temperatures, frequencies)
    diffs = [frequencies[index + 1] - frequencies[index] for index in range(len(frequencies) - 1)]
    negative_steps = sum(1 for diff in diffs if diff <= 0.0)
    monotonic_fraction = negative_steps / max(len(diffs), 1)
    total_span = frequencies[0] - frequencies[-1]
    midpoint_frequency = (frequencies[0] + frequencies[-1]) / 2.0

    midpoint_temperature = float("nan")
    for index in range(1, len(points)):
        low_temperature, low_frequency = points[index - 1]
        high_temperature, high_frequency = points[index]
        crosses_midpoint = (low_frequency - midpoint_frequency) * (high_frequency - midpoint_frequency) <= 0.0
        if crosses_midpoint and high_temperature != low_temperature:
            weight = (midpoint_frequency - low_frequency) / (high_frequency - low_frequency)
            midpoint_temperature = low_temperature + weight * (high_temperature - low_temperature)
            break

    return {
        "label": label,
        "n_points": len(points),
        "temperature_range": [min(temperatures), max(temperatures)],
        "frequency_range": [min(frequencies), max(frequencies)],
        "temperature_slope": slope,
        "fit_intercept": intercept,
        "fit_rmse": rmse,
        "monotonic_fraction": monotonic_fraction,
        "frequency_span": total_span,
        "midpoint_temperature": midpoint_temperature,
    }


def classify_opening_protocol() -> dict:
    manualloop_source = XYSource(
        name="ManualLOOP CSV",
        location=MANUALLOOP_DATA_URL,
        x_index=0,
        y_index=1,
        delimiter=",",
    )
    tempdep_source = TemperatureSource(
        name="TempDep CSV",
        location=TEMPDEP_DATA_URL,
        temperature_index=0,
        frequency_index=1,
        delimiter=",",
    )
    pysspfm_off_source = XYSource(
        name="PySSPFM off_f loop",
        location=PYSSPFM_OFF_URL,
        x_index=2,
        y_index=3,
    )
    pysspfm_on_source = XYSource(
        name="PySSPFM on_f loop",
        location=PYSSPFM_ON_URL,
        x_index=2,
        y_index=3,
    )

    manualloop_points = load_xy_points(manualloop_source)
    tempdep_points = load_temperature_points(tempdep_source)
    pysspfm_off_points = load_xy_points(pysspfm_off_source)
    pysspfm_on_points = load_xy_points(pysspfm_on_source)

    hysteresis_manual = analyze_hysteresis(manualloop_points, manualloop_source.name)
    hysteresis_off = analyze_hysteresis(pysspfm_off_points, pysspfm_off_source.name)
    hysteresis_on = analyze_hysteresis(pysspfm_on_points, pysspfm_on_source.name)

    hysteresis_area_ok = hysteresis_manual["loop_area"] > 0.0 and hysteresis_off["loop_area"] > 0.0 and hysteresis_on["loop_area"] > 0.0
    hysteresis_gap_ok = (
        math.isfinite(hysteresis_manual["branch_gap"]) and hysteresis_manual["branch_gap"] > 0.0
        and math.isfinite(hysteresis_off["branch_gap"]) and hysteresis_off["branch_gap"] > 0.0
        and math.isfinite(hysteresis_on["branch_gap"]) and hysteresis_on["branch_gap"] > 0.0
    )

    temperature_response = analyze_temperature_dependency(tempdep_points, tempdep_source.name)
    temp_shift_ok = temperature_response["frequency_span"] > 0.5 and temperature_response["monotonic_fraction"] > 0.8

    manualloop_curve = normalize_curve(manualloop_points)
    pysspfm_off_curve = normalize_curve(pysspfm_off_points)
    pysspfm_on_curve = normalize_curve(pysspfm_on_points)

    collapse_off_on = collapse_rmse(pysspfm_off_curve, pysspfm_on_curve, COLLAPSE_GRID)
    control_manual_off = collapse_rmse(manualloop_curve, pysspfm_off_curve, COLLAPSE_GRID)
    control_manual_on = collapse_rmse(manualloop_curve, pysspfm_on_curve, COLLAPSE_GRID)

    collapse_mean = collapse_off_on
    control_mean = statistics.mean([control_manual_off, control_manual_on])

    collapse_ok = collapse_mean < 0.50
    control_ok = control_mean > collapse_mean

    results = {
        "hysteresis": {
            "manualloop": hysteresis_manual,
            "pysspfm_off": hysteresis_off,
            "pysspfm_on": hysteresis_on,
            "area_status": "conforme strict" if hysteresis_area_ok else "falsifie",
            "gap_status": "conforme strict" if hysteresis_gap_ok else "falsifie",
        },
        "threshold": {
            "source": tempdep_source.name,
            "response": temperature_response,
            "temp_shift_status": "conforme strict" if temp_shift_ok else "falsifie",
        },
        "collapse": {
            "manualloop": manualloop_curve,
            "pysspfm_off": pysspfm_off_curve,
            "pysspfm_on": pysspfm_on_curve,
            "pairwise_rmse": {
                "off_on": collapse_off_on,
                "manual_off": control_manual_off,
                "manual_on": control_manual_on,
            },
            "mean_rmse": collapse_mean,
            "mean_control_rmse": control_mean,
            "collapse_status": "conforme strict" if collapse_ok else "falsifie",
            "control_status": "conforme strict" if control_ok else "falsifie",
        },
    }

    results["overall_verdict"] = "conforme strict" if (hysteresis_area_ok and hysteresis_gap_ok and temp_shift_ok and collapse_ok and control_ok) else "falsifie"
    results["falsifiers"] = [
        "les boucles réelles ne ferment pas ou perdent leur séparation de branches",
        "la fréquence de résonance ne décroît pas assez nettement avec la température",
        "les deux boucles PySSPFM ne se superposent pas après réduction",
        "le contrôle ManualLOOP ne reste pas séparé du couple PySSPFM après réduction",
    ]
    return results


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    outdir = Path("results")
    outdir.mkdir(exist_ok=True)

    results = classify_opening_protocol()

    json_path = outdir / f"opening_protocol_check_{timestamp}.json"
    txt_path = outdir / f"opening_protocol_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle de protocole d’ouverture\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Hystérésis: {results['hysteresis']['area_status']}\n")
        handle.write(f"- Mémoire / séparation de branches: {results['hysteresis']['gap_status']}\n")
        handle.write(f"- Dépendance température / fréquence: {results['threshold']['temp_shift_status']}\n")
        handle.write(f"- Effondrement réduit inter-systèmes: {results['collapse']['collapse_status']}\n")
        handle.write(f"- Contrôle négatif séparé: {results['collapse']['control_status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()