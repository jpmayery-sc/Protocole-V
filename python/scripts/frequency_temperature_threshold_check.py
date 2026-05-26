"""Frequency-temperature threshold check.

This script focuses on the temperature-dependent resonance table and verifies
that the resonance frequency decreases cleanly with temperature, with a stable
threshold crossing between the cold and hot endpoints.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import csv
import json
import math
import statistics
import time
import urllib.request
from pathlib import Path


TEMPDEP_DATA_URL = "https://raw.githubusercontent.com/shahjahanIqbal/NQR_Frequency_Temp_Dep/main/TempDep.csv"


@dataclass(frozen=True)
class TemperatureSource:
    name: str
    location: str


def read_text(location: str) -> str:
    request = urllib.request.Request(location, headers={"User-Agent": "Mozilla/5.0"}) if location.startswith(("http://", "https://")) else None
    if request is not None:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode("utf-8", errors="replace")

    return Path(location).read_text(encoding="utf-8")


def load_temperature_points(source: TemperatureSource) -> list[tuple[float, float]]:
    text = read_text(source.location)
    points: list[tuple[float, float]] = []

    for row in csv.reader(text.splitlines()):
        if len(row) < 2:
            continue

        try:
            temperature = float(row[0])
            frequency = float(row[1])
        except ValueError:
            continue

        points.append((temperature, frequency))

    if len(points) < 8:
        raise ValueError(f"{source.name}: not enough numeric points found")

    return sorted(points)


def fit_line(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    x_mean = statistics.mean(xs)
    y_mean = statistics.mean(ys)
    covariance = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
    variance = sum((x - x_mean) ** 2 for x in xs)
    slope = covariance / variance if variance else 0.0
    intercept = y_mean - slope * x_mean
    residuals = [y - (slope * x + intercept) for x, y in zip(xs, ys)]
    rmse = math.sqrt(sum(value * value for value in residuals) / len(residuals))
    return slope, intercept, rmse


def leave_one_out_rmse(points: list[tuple[float, float]]) -> float:
    xs = [temperature for temperature, _ in points]
    ys = [frequency for _, frequency in points]
    residuals = []

    for index in range(len(points)):
        train_points = points[:index] + points[index + 1 :]
        train_xs = [temperature for temperature, _ in train_points]
        train_ys = [frequency for _, frequency in train_points]
        slope, intercept, _ = fit_line(train_xs, train_ys)
        residuals.append(ys[index] - (slope * xs[index] + intercept))

    return math.sqrt(sum(value * value for value in residuals) / len(residuals))


def analyze_threshold(points: list[tuple[float, float]], label: str) -> dict:
    temperatures = [temperature for temperature, _ in points]
    frequencies = [frequency for _, frequency in points]

    slope, intercept, rmse = fit_line(temperatures, frequencies)
    loo_rmse = leave_one_out_rmse(points)
    diffs = [frequencies[index + 1] - frequencies[index] for index in range(len(frequencies) - 1)]
    non_increasing_fraction = sum(1 for diff in diffs if diff <= 0.0) / max(len(diffs), 1)
    frequency_span = frequencies[0] - frequencies[-1]
    midpoint_frequency = (frequencies[0] + frequencies[-1]) / 2.0

    midpoint_temperature = float("nan")
    for index in range(1, len(points)):
        low_temperature, low_frequency = points[index - 1]
        high_temperature, high_frequency = points[index]
        crosses_midpoint = (low_frequency - midpoint_frequency) * (high_frequency - midpoint_frequency) <= 0.0
        if crosses_midpoint and high_temperature != low_temperature and high_frequency != low_frequency:
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
        "loo_rmse": loo_rmse,
        "loo_rmse_ratio": loo_rmse / max(frequency_span, 1.0e-12),
        "non_increasing_fraction": non_increasing_fraction,
        "frequency_span": frequency_span,
        "midpoint_frequency": midpoint_frequency,
        "midpoint_temperature": midpoint_temperature,
    }


def classify_threshold() -> dict:
    source = TemperatureSource(name="TempDep CSV", location=TEMPDEP_DATA_URL)
    points = load_temperature_points(source)
    response = analyze_threshold(points, source.name)

    monotonic_ok = response["non_increasing_fraction"] == 1.0
    span_ok = response["frequency_span"] > 0.5
    fit_ok = response["temperature_slope"] < 0.0 and response["loo_rmse_ratio"] < 0.05

    return {
        "source": source.name,
        "response": response,
        "threshold_status": "conforme strict" if (monotonic_ok and span_ok and fit_ok) else "falsifie",
        "criteria": {
            "monotonic_ok": monotonic_ok,
            "span_ok": span_ok,
            "fit_ok": fit_ok,
        },
        "overall_verdict": "conforme strict" if (monotonic_ok and span_ok and fit_ok) else "falsifie",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Frequency-temperature threshold check.")
    _ = parser.parse_args()

    results_dir = Path("results")
    results_dir.mkdir(exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    results = classify_threshold()

    json_path = results_dir / f"frequency_temperature_threshold_{timestamp}.json"
    txt_path = results_dir / f"frequency_temperature_threshold_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Frequency-temperature threshold check\n")
        handle.write(f"Timestamp: {timestamp}\n")
        handle.write(f"Source: {results['source']}\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n")
        handle.write(f"Threshold status: {results['threshold_status']}\n")
        handle.write(f"Points: {results['response']['n_points']}\n")
        handle.write(f"Temperature range: {results['response']['temperature_range'][0]:.1f} -> {results['response']['temperature_range'][1]:.1f}\n")
        handle.write(f"Frequency range: {results['response']['frequency_range'][0]:.6f} -> {results['response']['frequency_range'][1]:.6f}\n")
        handle.write(f"Frequency span: {results['response']['frequency_span']:.6f}\n")
        handle.write(f"Slope: {results['response']['temperature_slope']:.9f}\n")
        handle.write(f"Fit RMSE: {results['response']['fit_rmse']:.6f}\n")
        handle.write(f"LOO RMSE: {results['response']['loo_rmse']:.6f}\n")
        handle.write(f"LOO RMSE ratio: {results['response']['loo_rmse_ratio']:.6f}\n")
        handle.write(f"Midpoint temperature: {results['response']['midpoint_temperature']:.6f}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()