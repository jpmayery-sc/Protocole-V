"""Download and prepare the public datasets used for V29 test 1.

This preparer focuses on the most direct expansion-history probes:
- cosmic chronometers H(z) measurements,
- DESI DR1 BAO combined GC likelihood data,
- Pantheon+SH0ES supernova distance measurements.

It stores the raw downloads and writes compact, analysis-ready tables plus a
manifest that records where the data came from.
"""

from __future__ import annotations

import csv
import json
import re
import time
import urllib.request
from pathlib import Path

import numpy as np


COSMIC_CHRONOMETER_URL = (
    "https://github.com/Ahmadmehrabi/Cosmic_chronometer_data/raw/refs/heads/main/HzTable_MM_BC32.txt"
)
DESI_BAO_MEAN_URL = (
    "https://github.com/CobayaSampler/bao_data/raw/refs/heads/master/"
    "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"
)
DESI_BAO_COV_URL = (
    "https://github.com/CobayaSampler/bao_data/raw/refs/heads/master/"
    "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"
)
PANTHEON_DATA_URL = (
    "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/"
    "Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat"
)
PANTHEON_STATONLY_COV_URL = (
    "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/"
    "Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STATONLY.cov"
)
PANTHEON_STATSYS_COV_URL = (
    "https://raw.githubusercontent.com/PantheonPlusSH0ES/DataRelease/main/"
    "Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov"
)


FLOAT_PATTERN = re.compile(r"[-+]?(?:\d*\.\d+|\d+\.?)(?:[eE][-+]?\d+)?")


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def read_text(location: str) -> str:
    request = urllib.request.Request(location, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.read().decode("utf-8", errors="replace")


def download_file(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    text = read_text(url)
    destination.write_text(text, encoding="utf-8")


def parse_numeric_tokens(line: str) -> list[float]:
    return [float(token) for token in FLOAT_PATTERN.findall(line)]


def prepare_chronometer_table(raw_path: Path, prepared_path: Path) -> dict:
    rows: list[dict[str, float | str]] = []
    text = raw_path.read_text(encoding="utf-8")

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        numeric = parse_numeric_tokens(line)
        if len(numeric) < 3:
            continue

        rows.append(
            {
                "z": numeric[0],
                "Hz_km_s_Mpc": numeric[1],
                "sigma_H_km_s_Mpc": numeric[2],
                "source_line": line,
            }
        )

    if len(rows) < 8:
        raise ValueError("Chronometer table did not yield enough rows")

    prepared_path.parent.mkdir(parents=True, exist_ok=True)
    with prepared_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["z", "Hz_km_s_Mpc", "sigma_H_km_s_Mpc", "source_line"],
        )
        writer.writeheader()
        writer.writerows(rows)

    zs = [row["z"] for row in rows]
    hs = [row["Hz_km_s_Mpc"] for row in rows]
    sigmas = [row["sigma_H_km_s_Mpc"] for row in rows]
    return {
        "rows": len(rows),
        "z_min": min(zs),
        "z_max": max(zs),
        "H_min": min(hs),
        "H_max": max(hs),
        "sigma_min": min(sigmas),
        "sigma_max": max(sigmas),
        "prepared_file": str(prepared_path),
    }


def prepare_bao_mean_table(raw_path: Path, prepared_path: Path) -> dict:
    text = raw_path.read_text(encoding="utf-8")
    tokens = text.replace("#", " ").split()

    points: list[dict[str, str | float]] = []
    index = 0
    while index + 2 < len(tokens):
        maybe_z = tokens[index]
        maybe_value = tokens[index + 1]
        maybe_quantity = tokens[index + 2]
        try:
            z_value = float(maybe_z)
            observed_value = float(maybe_value)
        except ValueError:
            index += 1
            continue

        points.append(
            {
                "z": z_value,
                "value_at_z": observed_value,
                "quantity": maybe_quantity,
            }
        )
        index += 3

    if len(points) < 4:
        raise ValueError("BAO mean file did not yield enough points")

    prepared_path.parent.mkdir(parents=True, exist_ok=True)
    with prepared_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["z", "value_at_z", "quantity"])
        writer.writeheader()
        writer.writerows(points)

    quantities = sorted({str(point["quantity"]) for point in points})
    return {
        "rows": len(points),
        "z_min": min(point["z"] for point in points),
        "z_max": max(point["z"] for point in points),
        "quantities": quantities,
        "prepared_file": str(prepared_path),
    }


def prepare_covariance_matrix(raw_path: Path, prepared_path: Path) -> dict:
    matrix: list[list[float]] = []
    text = raw_path.read_text(encoding="utf-8")

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        values = parse_numeric_tokens(line)
        if values:
            matrix.append(values)

    if len(matrix) < 4:
        raise ValueError("Covariance file did not yield enough numeric rows")

    prepared_path.parent.mkdir(parents=True, exist_ok=True)
    with prepared_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        for row in matrix:
            writer.writerow(row)

    width = max(len(row) for row in matrix)
    return {
        "rows": len(matrix),
        "columns_max": width,
        "prepared_file": str(prepared_path),
    }


def prepare_pantheon_table(raw_path: Path, prepared_path: Path) -> dict:
    rows: list[dict[str, str | float]] = []
    text = raw_path.read_text(encoding="utf-8")
    header: list[str] | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue

        if header is None:
            header = line.split()
            continue

        parts = line.split()
        if len(parts) < len(header):
            continue

        values = dict(zip(header, parts, strict=False))
        try:
            z_hd = float(values["zHD"])
            mu_shoes = float(values["MU_SH0ES"])
            mu_err = float(values["MU_SH0ES_ERR_DIAG"])
        except (KeyError, ValueError):
            continue

        rows.append(
            {
                "CID": values.get("CID", ""),
                "IDSURVEY": values.get("IDSURVEY", ""),
                "zHD": z_hd,
                "MU_SH0ES": mu_shoes,
                "MU_SH0ES_ERR_DIAG": mu_err,
                "IS_CALIBRATOR": values.get("IS_CALIBRATOR", ""),
                "USED_IN_SH0ES_HF": values.get("USED_IN_SH0ES_HF", ""),
                "source_line": line,
            }
        )

    if len(rows) < 100:
        raise ValueError("Pantheon+ table did not yield enough rows")

    prepared_path.parent.mkdir(parents=True, exist_ok=True)
    with prepared_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "CID",
                "IDSURVEY",
                "zHD",
                "MU_SH0ES",
                "MU_SH0ES_ERR_DIAG",
                "IS_CALIBRATOR",
                "USED_IN_SH0ES_HF",
                "source_line",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    zs = [row["zHD"] for row in rows]
    mu_values = [row["MU_SH0ES"] for row in rows]
    return {
        "rows": len(rows),
        "z_min": min(zs),
        "z_max": max(zs),
        "mu_min": min(mu_values),
        "mu_max": max(mu_values),
        "prepared_file": str(prepared_path),
    }


def prepare_pantheon_covariance(raw_path: Path, prepared_path: Path) -> dict:
    text = raw_path.read_text(encoding="utf-8")
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        raise ValueError("Pantheon covariance file is empty")

    try:
        size = int(lines[0].split()[0])
    except ValueError as exc:
        raise ValueError("Pantheon covariance file does not start with a matrix size") from exc

    payload = " ".join(lines[1:])
    values = np.fromstring(payload, sep=" ", dtype=float)
    expected = size * size
    if values.size != expected:
        raise ValueError(
            f"Pantheon covariance value count mismatch: expected {expected}, got {values.size}"
        )

    matrix = values.reshape((size, size))
    prepared_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(prepared_path, matrix)

    return {
        "rows": size,
        "columns_max": size,
        "values": int(values.size),
        "prepared_file": str(prepared_path.with_suffix(prepared_path.suffix + ".npy")),
    }


def main() -> None:
    root = project_root()
    output_dir = root / "results" / "result-analyse" / "v29_test1_data"
    raw_dir = output_dir / "raw"
    prepared_dir = output_dir / "prepared"
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_sources = {
        "cosmic_chronometers_raw": (COSMIC_CHRONOMETER_URL, raw_dir / "HzTable_MM_BC32.txt"),
        "bao_mean_raw": (DESI_BAO_MEAN_URL, raw_dir / "desi_2024_gaussian_bao_ALL_GCcomb_mean.txt"),
        "bao_cov_raw": (DESI_BAO_COV_URL, raw_dir / "desi_2024_gaussian_bao_ALL_GCcomb_cov.txt"),
        "pantheon_data_raw": (PANTHEON_DATA_URL, raw_dir / "Pantheon+SH0ES.dat"),
        "pantheon_statonly_cov_raw": (
            PANTHEON_STATONLY_COV_URL,
            raw_dir / "Pantheon+SH0ES_STATONLY.cov",
        ),
        "pantheon_statsys_cov_raw": (
            PANTHEON_STATSYS_COV_URL,
            raw_dir / "Pantheon+SH0ES_STAT+SYS.cov",
        ),
    }

    raw_downloads: dict[str, dict[str, str | int]] = {}
    for label, (url, path) in raw_sources.items():
        download_file(url, path)
        raw_downloads[label] = {
            "source_url": url,
            "local_path": str(path),
            "bytes": path.stat().st_size,
        }

    chronometer_summary = prepare_chronometer_table(
        raw_sources["cosmic_chronometers_raw"][1],
        prepared_dir / "cosmic_chronometers_hz.csv",
    )
    bao_mean_summary = prepare_bao_mean_table(
        raw_sources["bao_mean_raw"][1],
        prepared_dir / "desi_bao_all_gccomb_mean.csv",
    )
    bao_cov_summary = prepare_covariance_matrix(
        raw_sources["bao_cov_raw"][1],
        prepared_dir / "desi_bao_all_gccomb_cov.csv",
    )
    pantheon_summary = prepare_pantheon_table(
        raw_sources["pantheon_data_raw"][1],
        prepared_dir / "pantheon_plus_shoes.csv",
    )
    pantheon_statonly_summary = prepare_pantheon_covariance(
        raw_sources["pantheon_statonly_cov_raw"][1],
        prepared_dir / "pantheon_plus_shoes_statonly_cov",
    )
    pantheon_statsys_summary = prepare_pantheon_covariance(
        raw_sources["pantheon_statsys_cov_raw"][1],
        prepared_dir / "pantheon_plus_shoes_statsys_cov",
    )

    manifest = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ"),
        "output_dir": str(output_dir),
        "raw_downloads": raw_downloads,
        "prepared": {
            "cosmic_chronometers": chronometer_summary,
            "desi_bao_mean": bao_mean_summary,
            "desi_bao_covariance": bao_cov_summary,
            "pantheon_plus_shoes": pantheon_summary,
            "pantheon_plus_shoes_statonly_covariance": pantheon_statonly_summary,
            "pantheon_plus_shoes_statsys_covariance": pantheon_statsys_summary,
        },
        "test_1_use": [
            "direct H(z) points from cosmic chronometers",
            "BAO distance-scale constraints from DESI DR1",
            "supernova distance moduli from Pantheon+SH0ES",
        ],
    }

    (output_dir / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        "V29 test 1 data preparation",
        f"timestamp: {manifest['timestamp']}",
        "",
        "Downloaded sources:",
    ]
    for label, info in raw_downloads.items():
        lines.append(f"- {label}: {info['local_path']}")
    lines.extend(
        [
            "",
            f"Chronometers rows: {chronometer_summary['rows']}",
            f"Chronometer z range: {chronometer_summary['z_min']} to {chronometer_summary['z_max']}",
            f"BAO mean points: {bao_mean_summary['rows']}",
            f"BAO quantities: {', '.join(bao_mean_summary['quantities'])}",
            f"BAO covariance rows: {bao_cov_summary['rows']}",
            f"BAO covariance max width: {bao_cov_summary['columns_max']}",
            f"Pantheon+ rows: {pantheon_summary['rows']}",
            f"Pantheon+ z range: {pantheon_summary['z_min']} to {pantheon_summary['z_max']}",
            f"Pantheon+ stat-only covariance rows: {pantheon_statonly_summary['rows']}",
            f"Pantheon+ stat+sys covariance rows: {pantheon_statsys_summary['rows']}",
            "",
            "Prepared files:",
            f"- {chronometer_summary['prepared_file']}",
            f"- {bao_mean_summary['prepared_file']}",
            f"- {bao_cov_summary['prepared_file']}",
            f"- {pantheon_summary['prepared_file']}",
            f"- {pantheon_statonly_summary['prepared_file']}",
            f"- {pantheon_statsys_summary['prepared_file']}",
            "",
        ]
    )
    (output_dir / "summary.txt").write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()