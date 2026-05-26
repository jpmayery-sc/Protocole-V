"""Run the V91 V90-vs-LambdaCDM confrontation.

V91 makes the V90 definitions explicit and compares the local information
speed, geometric compression, and calibrated photon factor against the
standard LambdaCDM distance reference.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from pathlib import Path


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


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


def hubble_lcdm(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float) -> float:
    return h0 * math.sqrt(max(0.0, omega_r * (1.0 + z) ** 4 + omega_m * (1.0 + z) ** 3 + omega_l))


def comoving_distance_lcdm(z: float, h0: float, omega_m: float, omega_r: float, omega_l: float) -> float:
    steps = max(64, int(200 * max(1.0, z)))
    dz = z / steps if steps > 0 else 0.0
    integral = 0.0
    for index in range(steps):
        z_i = (index + 0.5) * dz
        h_i = hubble_lcdm(z_i, h0, omega_m, omega_r, omega_l)
        integral += 1.0 / max(h_i, 1.0e-12)
    c_km_s = 299792.458
    return c_km_s * dz * integral


def geometry_factor(z: float, center: float, width: float, amplitude: float) -> float:
    return 1.0 + amplitude * sigmoid(z, center, width)


def suppression_factor(z: float, center: float, width: float, amplitude: float) -> float:
    return 1.0 / (1.0 + amplitude * sigmoid(z, center, width))


def analyse_row(
    z: float,
    *,
    tau0: float,
    z_center: float,
    width: float,
    geometry_amplitude: float,
    distance_amplitude: float,
    h0: float,
    omega_m: float,
    omega_r: float,
    omega_l: float,
) -> dict[str, float]:
    transition = sigmoid(z, z_center, width)
    g_z = geometry_factor(z, z_center, width, geometry_amplitude)
    tau_z = tau0 * g_z
    d_lcdm = comoving_distance_lcdm(z, h0, omega_m, omega_r, omega_l)
    d_v90 = d_lcdm * suppression_factor(z, z_center, width, distance_amplitude) / max(1.0 + z, 1.0e-12)
    f_photon_z = (1.0 + z) / max(g_z, 1.0e-12)
    v_info_v90 = d_v90 / max(tau_z, 1.0e-12)
    v_info_lcdm = d_lcdm / max(tau0, 1.0e-12)
    v_ratio = v_info_v90 / max(v_info_lcdm, 1.0e-12)
    distance_ratio = d_v90 / max(d_lcdm, 1.0e-12)
    z_model = g_z * f_photon_z - 1.0

    return {
        "z": z,
        "transition": transition,
        "g_z": g_z,
        "tau_z": tau_z,
        "d_lcdm": d_lcdm,
        "d_v90": d_v90,
        "distance_ratio": distance_ratio,
        "v_info_lcdm": v_info_lcdm,
        "v_info_v90": v_info_v90,
        "v_ratio": v_ratio,
        "f_photon_z": f_photon_z,
        "z_model": z_model,
        "redshift_residual": z_model - z,
        "tau_over_tau0": tau_z / max(tau0, 1.0e-12),
    }


def summarize(rows: list[dict[str, float]], *, parameters: dict[str, float], z_values: list[float]) -> dict[str, object]:
    max_abs_residual = max(abs(row["redshift_residual"]) for row in rows)
    center_index = min(range(len(z_values)), key=lambda index: abs(z_values[index] - parameters["z_center"]))
    left_index = max(0, center_index - 1)
    right_index = min(len(z_values) - 1, center_index + 1)

    v_info_values = [row["v_info_v90"] for row in rows]
    tau_values = [row["tau_z"] for row in rows]
    distance_ratios = [row["distance_ratio"] for row in rows]
    v_ratios = [row["v_ratio"] for row in rows]

    monotonic_tau = all(current >= previous for previous, current in zip(tau_values, tau_values[1:]))
    info_drop_at_center = v_info_values[right_index] <= v_info_values[left_index]
    distance_suppression = max(distance_ratios) < 1.0
    lcdm_contrast = sum(abs(1.0 - ratio) for ratio in distance_ratios) + sum(abs(1.0 - ratio) for ratio in v_ratios)

    if max_abs_residual <= 1.0e-12 and monotonic_tau and info_drop_at_center and distance_suppression:
        verdict = "v91_lcdm_confrontation_confirmed"
    else:
        verdict = "v91_lcdm_confrontation_partial"

    return {
        "suite": "v91_lcdm_compare",
        "timestamp": parameters["timestamp"],
        "verdict": verdict,
        "parameters": parameters,
        "sample_count": len(rows),
        "z_min": min(z_values),
        "z_max": max(z_values),
        "max_abs_redshift_residual": max_abs_residual,
        "min_distance_ratio": min(distance_ratios),
        "max_distance_ratio": max(distance_ratios),
        "min_v_ratio": min(v_ratios),
        "max_v_ratio": max(v_ratios),
        "monotonic_tau": monotonic_tau,
        "info_drop_at_center": info_drop_at_center,
        "distance_suppression": distance_suppression,
        "lcdm_contrast": lcdm_contrast,
        "rows": rows,
        "notes": [
            "LCDM is used as the explicit distance reference, not as a deformation target.",
            "The redshift constraint is enforced explicitly through f_photon(z) = (1 + z) / g(z).",
            "The comparison is carried by distance_ratio and v_ratio relative to the LCDM reference.",
        ],
    }


def write_outputs(rows: list[dict[str, float]], summary: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    csv_path = output_dir / f"v91_lcdm_compare_{timestamp}.csv"
    json_path = output_dir / f"v91_lcdm_compare_{timestamp}.json"
    txt_path = output_dir / f"v91_lcdm_compare_{timestamp}.txt"

    fieldnames = list(rows[0].keys()) if rows else []
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    payload = {**summary, "csv_path": str(csv_path), "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V91 LCDM comparison summary",
        f"timestamp: {timestamp}",
        f"verdict: {summary['verdict']}",
        f"sample_count: {summary['sample_count']}",
        f"z_min: {summary['z_min']}",
        f"z_max: {summary['z_max']}",
        f"max_abs_redshift_residual: {summary['max_abs_redshift_residual']}",
        f"min_distance_ratio: {summary['min_distance_ratio']}",
        f"max_distance_ratio: {summary['max_distance_ratio']}",
        f"min_v_ratio: {summary['min_v_ratio']}",
        f"max_v_ratio: {summary['max_v_ratio']}",
        f"monotonic_tau: {summary['monotonic_tau']}",
        f"info_drop_at_center: {summary['info_drop_at_center']}",
        f"distance_suppression: {summary['distance_suppression']}",
        f"lcdm_contrast: {summary['lcdm_contrast']}",
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


def run_v91_lcdm_compare(
    *,
    z_values: list[float] | None = None,
    output_dir: str | Path | None = None,
    tau0: float = 1.0,
    z_center: float = 0.46,
    width: float = 0.16,
    geometry_amplitude: float = 0.18,
    distance_amplitude: float = 2.5,
    h0: float = 67.4,
    omega_m: float = 0.315,
    omega_r: float = 9.0e-5,
    omega_l: float = 0.685,
) -> dict[str, object]:
    if z_values is None:
        z_values = [0.0, 0.23, 0.46, 0.69, 1.0, 2.0, 3.0]

    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v91_lcdm_compare"

    rows = [
        analyse_row(
            z,
            tau0=tau0,
            z_center=z_center,
            width=width,
            geometry_amplitude=geometry_amplitude,
            distance_amplitude=distance_amplitude,
            h0=h0,
            omega_m=omega_m,
            omega_r=omega_r,
            omega_l=omega_l,
        )
        for z in z_values
    ]

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    parameters = {
        "timestamp": timestamp,
        "tau0": tau0,
        "z_center": z_center,
        "width": width,
        "geometry_amplitude": geometry_amplitude,
        "distance_amplitude": distance_amplitude,
        "h0": h0,
        "omega_m": omega_m,
        "omega_r": omega_r,
        "omega_l": omega_l,
    }

    summary = summarize(rows, parameters=parameters, z_values=z_values)
    csv_path, json_path, txt_path = write_outputs(rows, summary, result_dir)
    summary.update({"csv_path": str(csv_path), "json_path": str(json_path), "txt_path": str(txt_path)})
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V91 V90-vs-LCDM comparison.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    parser.add_argument("--z-values", default="0.0,0.23,0.46,0.69,1.0,2.0,3.0", help="Comma-separated redshift values")
    parser.add_argument("--tau0", type=float, default=1.0, help="Reference proper-time scale")
    parser.add_argument("--z-center", type=float, default=0.46, help="Transition redshift")
    parser.add_argument("--width", type=float, default=0.16, help="Transition width")
    parser.add_argument("--geometry-amplitude", type=float, default=0.18, help="Amplitude of g(z)")
    parser.add_argument("--distance-amplitude", type=float, default=2.5, help="Suppression amplitude for the distance proxy")
    parser.add_argument("--h0", type=float, default=67.4, help="Reference H0 used for the distance proxy")
    parser.add_argument("--omega-m", type=float, default=0.315, dest="omega_m", help="Matter density parameter")
    parser.add_argument("--omega-r", type=float, default=9.0e-5, dest="omega_r", help="Radiation density parameter")
    parser.add_argument("--omega-l", type=float, default=0.685, dest="omega_l", help="Dark-energy density parameter")
    args = parser.parse_args()

    result = run_v91_lcdm_compare(
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