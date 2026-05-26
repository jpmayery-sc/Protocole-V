"""Run the V90 time / speed / information / geometry toy calculation.

The script follows the V90 appendix as a local calculation scaffold:
it defines a smooth geometric factor g(z), a photon factor f_photon(z),
derives tau(z), v_info(z), v_eff(z), and reports the implied redshift
relation on a user-supplied redshift grid.

The model is intentionally phenomenological. It is meant to be a small,
testable calculation chain, not a full cosmology solver.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def linspace(start: float, stop: float, count: int) -> list[float]:
    if count <= 1:
        return [start]
    step = (stop - start) / (count - 1)
    return [start + index * step for index in range(count)]


def parse_z_values(text: str) -> list[float]:
    values: list[float] = []
    for token in text.split(","):
        token = token.strip()
        if token:
            values.append(float(token))
    return values


def sigmoid(z: float, center: float, width: float) -> float:
    width = max(width, 1.0e-12)
    return 1.0 / (1.0 + math.exp(-(z - center) / width))


def hubble_standard(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float) -> float:
    return h0 * math.sqrt(max(0.0, omega_r * (1.0 + z) ** 4 + omega_m * (1.0 + z) ** 3 + omega_l))


def comoving_distance(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float) -> float:
    steps = max(64, int(200 * max(1.0, z)))
    dz = z / steps if steps > 0 else 0.0
    integral = 0.0
    for index in range(steps):
        z_i = (index + 0.5) * dz
        h_i = hubble_standard(z_i, h0, omega_m, omega_r, omega_l)
        integral += 1.0 / max(h_i, 1.0e-12)
    c_km_s = 299792.458
    return c_km_s * dz * integral


def geometry_factor(z: float, center: float, width: float, amplitude: float) -> float:
    transition = sigmoid(z, center, width)
    return 1.0 + amplitude * transition


def distance_factor(z: float, center: float, width: float, amplitude: float) -> float:
    transition = sigmoid(z, center, width)
    return 1.0 / (1.0 + amplitude * transition)


def analyse_row(
    z: float,
    *,
    tau0: float,
    z_center: float,
    width: float,
    geometry_amplitude: float,
    distance_amplitude: float,
    distance_scale: float,
    h0: float,
    omega_m: float,
    omega_r: float,
    omega_l: float,
) -> dict[str, float]:
    transition = sigmoid(z, z_center, width)
    g_z = geometry_factor(z, z_center, width, geometry_amplitude)
    f_photon_z = (1.0 + z) / max(g_z, 1.0e-12)
    tau_z = tau0 * g_z
    d_std = comoving_distance(z, h0, omega_m, omega_r, omega_l) * distance_scale
    d_eff = d_std * distance_factor(z, z_center, width, distance_amplitude) / max(1.0 + z, 1.0e-12)
    v_info_z = d_eff / max(tau_z, 1.0e-12)
    v_eff_z = v_info_z * f_photon_z
    z_model = g_z * f_photon_z - 1.0
    residual = z_model - z
    baseline_v_info = d_std / max(tau0, 1.0e-12)
    speed_ratio = v_eff_z / max(baseline_v_info, 1.0e-12)

    return {
        "z": z,
        "transition": transition,
        "g_z": g_z,
        "f_photon_z": f_photon_z,
        "tau_z": tau_z,
        "d_std": d_std,
        "d_eff": d_eff,
        "v_info_z": v_info_z,
        "v_eff_z": v_eff_z,
        "z_model": z_model,
        "redshift_residual": residual,
        "speed_ratio": speed_ratio,
        "tau_over_tau0": tau_z / max(tau0, 1.0e-12),
        "distance_suppression": d_eff / max(d_std, 1.0e-12),
    }


def summarize(rows: list[dict[str, float]], *, parameters: dict[str, float], z_values: list[float]) -> dict[str, object]:
    max_abs_residual = max(abs(row["redshift_residual"]) for row in rows)
    z_model_values = [row["z_model"] for row in rows]
    v_info_values = [row["v_info_z"] for row in rows]
    tau_values = [row["tau_z"] for row in rows]

    center_index = min(range(len(z_values)), key=lambda index: abs(z_values[index] - parameters["z_center"]))
    left_index = max(0, center_index - 1)
    right_index = min(len(z_values) - 1, center_index + 1)

    monotonic_z_model = all(current >= previous for previous, current in zip(z_model_values, z_model_values[1:]))
    tau_increasing = all(current >= previous for previous, current in zip(tau_values, tau_values[1:]))
    info_drop_at_center = v_info_values[right_index] <= v_info_values[left_index]

    if monotonic_z_model and tau_increasing and info_drop_at_center:
        verdict = "v90_calculation_scaffold_confirmed"
    else:
        verdict = "v90_calculation_scaffold_partial"

    return {
        "suite": "v90_dynamics",
        "timestamp": parameters["timestamp"],
        "verdict": verdict,
        "parameters": parameters,
        "sample_count": len(rows),
        "z_min": min(z_values),
        "z_max": max(z_values),
        "max_abs_redshift_residual": max_abs_residual,
        "min_v_info": min(v_info_values),
        "max_v_info": max(v_info_values),
        "min_tau": min(tau_values),
        "max_tau": max(tau_values),
        "monotonic_z_model": monotonic_z_model,
        "tau_increasing": tau_increasing,
        "info_drop_at_center": info_drop_at_center,
        "rows": rows,
        "notes": [
            "The script is phenomenological: g(z) and f_photon(z) are smooth calibration functions.",
            "The redshift identity 1 + z = g(z) * f_photon(z) is used as the V90 consistency relation.",
            "The distance proxy is normalized from the standard comoving distance so the calculation stays dimensionless and testable.",
        ],
    }


def write_outputs(rows: list[dict[str, float]], summary: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    csv_path = output_dir / f"v90_dynamics_{timestamp}.csv"
    json_path = output_dir / f"v90_dynamics_{timestamp}.json"
    txt_path = output_dir / f"v90_dynamics_{timestamp}.txt"

    fieldnames = list(rows[0].keys()) if rows else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    payload = {**summary, "csv_path": str(csv_path), "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V90 dynamics summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"sample_count: {summary['sample_count']}",
        f"z_min: {summary['z_min']}",
        f"z_max: {summary['z_max']}",
        f"max_abs_redshift_residual: {summary['max_abs_redshift_residual']}",
        f"min_v_info: {summary['min_v_info']}",
        f"max_v_info: {summary['max_v_info']}",
        f"min_tau: {summary['min_tau']}",
        f"max_tau: {summary['max_tau']}",
        f"monotonic_z_model: {summary['monotonic_z_model']}",
        f"tau_increasing: {summary['tau_increasing']}",
        f"info_drop_at_center: {summary['info_drop_at_center']}",
        "",
        "Parameters:",
    ]
    for key, value in summary["parameters"].items():
        if key != "timestamp":
            lines.append(f"- {key}: {value}")
    lines.extend(["", "Notes:"])
    for note in summary["notes"]:
        lines.append(f"- {note}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return csv_path, json_path, txt_path


def run_v90_dynamics(
    *,
    z_values: list[float] | None = None,
    output_dir: str | Path | None = None,
    tau0: float = 1.0,
    z_center: float = 0.46,
    width: float = 0.16,
    geometry_amplitude: float = 0.18,
    photon_amplitude: float = 0.24,
    distance_amplitude: float = 2.5,
    h0: float = 67.4,
    omega_m: float = 0.315,
    omega_r: float = 9.0e-5,
    omega_l: float = 0.685,
) -> dict[str, object]:
    if z_values is None:
        z_values = [0.0, 0.23, 0.46, 0.69, 1.0, 2.0, 3.0]

    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v90_dynamics"

    z_max = max(z_values) if z_values else 1.0
    distance_scale = 1.0 / max(comoving_distance(z_max, h0, omega_m, omega_r, omega_l), 1.0e-12)

    rows = [
        analyse_row(
            z,
            tau0=tau0,
            z_center=z_center,
            width=width,
            geometry_amplitude=geometry_amplitude,
            distance_amplitude=distance_amplitude,
            distance_scale=distance_scale,
            h0=h0,
            omega_m=omega_m,
            omega_r=omega_r,
            omega_l=omega_l,
        )
        for z in z_values
    ]

    parameters = {
        "timestamp": "pending",
        "tau0": tau0,
        "z_center": z_center,
        "width": width,
        "geometry_amplitude": geometry_amplitude,
        "distance_amplitude": distance_amplitude,
        "distance_scale": distance_scale,
        "h0": h0,
        "omega_m": omega_m,
        "omega_r": omega_r,
        "omega_l": omega_l,
    }
    # Use a deterministic timestamp-free summary during computation, then patch it with filenames.
    summary = summarize(rows, parameters=parameters, z_values=z_values)

    import time

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    summary["timestamp"] = timestamp
    summary["parameters"]["timestamp"] = timestamp

    csv_path, json_path, txt_path = write_outputs(rows, summary, result_dir)
    summary.update({"csv_path": str(csv_path), "json_path": str(json_path), "txt_path": str(txt_path)})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V90 dynamics toy calculation.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--z-values", default="0.0,0.23,0.46,0.69,1.0,2.0,3.0", help="Comma-separated redshift values")
    parser.add_argument("--tau0", type=float, default=1.0, help="Baseline proper-time scale")
    parser.add_argument("--z-center", type=float, default=0.46, help="Transition redshift")
    parser.add_argument("--width", type=float, default=0.16, help="Transition width")
    parser.add_argument("--geometry-amplitude", type=float, default=0.18, help="Amplitude of g(z)")
    parser.add_argument("--distance-amplitude", type=float, default=2.5, help="Suppression amplitude for the distance proxy")
    parser.add_argument("--h0", type=float, default=67.4, help="Baseline H0 used for the distance proxy")
    parser.add_argument("--omega-m", type=float, default=0.315, dest="omega_m", help="Matter density parameter")
    parser.add_argument("--omega-r", type=float, default=9.0e-5, dest="omega_r", help="Radiation density parameter")
    parser.add_argument("--omega-l", type=float, default=0.685, dest="omega_l", help="Dark-energy density parameter")
    args = parser.parse_args()

    result = run_v90_dynamics(
        z_values=parse_z_values(args.z_values),
        output_dir=args.output_dir,
        tau0=args.tau0,
        z_center=args.z_center,
        width=args.width,
        geometry_amplitude=args.geometry_amplitude,
        distance_amplitude=args.distance_amplitude,
        h0=args.h0,
        omega_m=args.omega_m,
        omega_r=args.omega_r,
        omega_l=args.omega_l,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()