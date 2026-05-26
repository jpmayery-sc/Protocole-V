"""Build figure-by-figure MOESM comparison files and calculation-ready CSV subsets.

This script consumes the raw workbook exports already generated under
results/result-analyse/moesm_exports/ and creates:
- a figure-by-figure comparison report,
- a master long-form CSV for calculations,
- one calculation-ready CSV per figure,
- a compact MOESM3 surface manifest.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def export_root(root: Path) -> Path:
    return root / "results" / "result-analyse" / "moesm_exports"


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def as_float(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def as_int(value: str | None) -> int | None:
    if value is None or value == "":
        return None
    return int(float(value))


def add_point(
    rows: list[dict[str, object]],
    *,
    figure: str,
    source: str,
    series: str,
    x_name: str,
    x_value: float | None,
    y_name: str,
    y_value: float | None,
    y_err_value: float | None = None,
    source_sheet: str,
) -> None:
    rows.append(
        {
            "figure": figure,
            "source": source,
            "series": series,
            "x_name": x_name,
            "x_value": x_value,
            "y_name": y_name,
            "y_value": y_value,
            "y_err_value": y_err_value,
            "source_sheet": source_sheet,
        }
    )


def build_fig2a(root: Path) -> list[dict[str, object]]:
    base = export_root(root) / "MOESM2"
    rows: list[dict[str, object]] = []

    for row in read_csv_rows(base / "Fig2a-Experiment.csv"):
        add_point(
            rows,
            figure="Fig2a",
            source="experiment",
            series=row["series"],
            x_name="t_probe_us",
            x_value=as_float(row["t_probe_us"]),
            y_name="P_down",
            y_value=as_float(row["P_down"]),
            y_err_value=as_float(row["P_down_err"]),
            source_sheet="Fig2a-Experiment",
        )

    for row in read_csv_rows(base / "Fig2a-Fits.csv"):
        add_point(
            rows,
            figure="Fig2a",
            source="fit",
            series="th_fit",
            x_name="t_probe_us",
            x_value=as_float(row["t_probe_us_th_fit"]),
            y_name="P_down",
            y_value=as_float(row["P_down_th_fit"]),
            source_sheet="Fig2a-Fits",
        )
        add_point(
            rows,
            figure="Fig2a",
            source="fit",
            series="ds_fit",
            x_name="t_probe_us",
            x_value=as_float(row["t_probe_us_ds_fit"]),
            y_name="P_down",
            y_value=as_float(row["P_down_ds_fit"]),
            source_sheet="Fig2a-Fits",
        )

    for row in read_csv_rows(base / "Fig2a-Simulation.csv"):
        add_point(
            rows,
            figure="Fig2a",
            source="simulation",
            series="P_up",
            x_name="t_probe_us",
            x_value=as_float(row["t_probe_us"]),
            y_name="P_up",
            y_value=as_float(row["P_up"]),
            source_sheet="Fig2a-Simulation",
        )

    return rows


def build_fig2b(root: Path) -> list[dict[str, object]]:
    base = export_root(root) / "MOESM2"
    rows: list[dict[str, object]] = []

    for row in read_csv_rows(base / "Fig2b-Experimet.csv"):
        add_point(
            rows,
            figure="Fig2b",
            source="experiment",
            series=row["series"],
            x_name="t_sqz_us",
            x_value=as_float(row["t_sqz_us"]),
            y_name="r",
            y_value=as_float(row["r"]),
            y_err_value=as_float(row["r_err"]),
            source_sheet="Fig2b-Experimet",
        )

    for row in read_csv_rows(base / "Fig2b-Theory.csv"):
        add_point(
            rows,
            figure="Fig2b",
            source="theory",
            series="Delta = 50 kHz",
            x_name="t_sqz_us",
            x_value=as_float(row["t_sqz_us"]),
            y_name="r",
            y_value=as_float(row["$\\Delta$ = 50 kHz"]),
            source_sheet="Fig2b-Theory",
        )
        add_point(
            rows,
            figure="Fig2b",
            source="theory",
            series="Delta = 100 kHz",
            x_name="t_sqz_us",
            x_value=as_float(row["t_sqz_us"]),
            y_name="r",
            y_value=as_float(row["$\\Delta$ = 100 kHz"]),
            source_sheet="Fig2b-Theory",
        )
        add_point(
            rows,
            figure="Fig2b",
            source="theory",
            series="eta^2",
            x_name="t_sqz_us",
            x_value=as_float(row["t_sqz_us"]),
            y_name="eta^2",
            y_value=as_float(row["eta^2"]),
            source_sheet="Fig2b-Theory",
        )

    return rows


def build_fig2c(root: Path) -> list[dict[str, object]]:
    base = export_root(root) / "MOESM2"
    rows: list[dict[str, object]] = []

    for row in read_csv_rows(base / "Fig2c-Experiment.csv"):
        add_point(
            rows,
            figure="Fig2c",
            source="experiment",
            series=row["series"],
            x_name="phi_probe_cycles",
            x_value=as_float(row["phi_probe_cycles"]),
            y_name="P_down",
            y_value=as_float(row["P_down"]),
            y_err_value=as_float(row["P_down_err"]),
            source_sheet="Fig2c-Experiment",
        )

    for row in read_csv_rows(base / "Fig2c-Fit.csv"):
        add_point(
            rows,
            figure="Fig2c",
            source="fit",
            series="down_fit",
            x_name="phi_probe_cycles",
            x_value=as_float(row["phi_probe_cycles_down"]),
            y_name="P_down",
            y_value=as_float(row["P_down_fit"]),
            source_sheet="Fig2c-Fit",
        )
        add_point(
            rows,
            figure="Fig2c",
            source="fit",
            series="up_fit",
            x_name="phi_probe_cycles",
            x_value=as_float(row["phi_probe_cycles_up"]),
            y_name="P_up",
            y_value=as_float(row["P_up_fit"]),
            source_sheet="Fig2c-Fit",
        )

    return rows


def build_fig2d(root: Path) -> list[dict[str, object]]:
    base = export_root(root) / "MOESM2"
    rows: list[dict[str, object]] = []

    for row in read_csv_rows(base / "Fig2d-Experiment.csv"):
        series = row.get("series") or "experiment"
        add_point(
            rows,
            figure="Fig2d",
            source="experiment",
            series=series,
            x_name="phase_diff_rad",
            x_value=as_float(row["phase_diff_rad"]),
            y_name="r",
            y_value=as_float(row["r"]),
            y_err_value=as_float(row["r_err"]),
            source_sheet="Fig2d-Experiment",
        )

    for row in read_csv_rows(base / "Fig2d-Fit.csv"):
        add_point(
            rows,
            figure="Fig2d",
            source="fit",
            series="fit",
            x_name="Delta_phi",
            x_value=as_float(row["\\Delta_\\phi"]),
            y_name="r",
            y_value=as_float(row["r_fit"]),
            source_sheet="Fig2d-Fit",
        )

    return rows


def build_moesm3_manifest(root: Path) -> list[dict[str, object]]:
    summary_path = export_root(root) / "MOESM3" / "workbook_summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    rows: list[dict[str, object]] = []
    for sheet in summary["sheets"]:
        rows.append(
            {
                "sheet": sheet["sheet"],
                "data_rows": sheet["data_rows"],
                "columns": sheet["columns"],
                "numeric_min": sheet["numeric_min"],
                "numeric_max": sheet["numeric_max"],
                "csv_path": sheet["csv_path"],
                "first_col_labels": " | ".join(sheet.get("first_col_labels", [])),
            }
        )
    return rows


def summarize_figure(rows: list[dict[str, object]]) -> dict[str, object]:
    sources = sorted({str(row["source"]) for row in rows})
    series = sorted({str(row["series"]) for row in rows})
    x_values = [float(row["x_value"]) for row in rows if row["x_value"] is not None]
    y_values = [float(row["y_value"]) for row in rows if row["y_value"] is not None]
    return {
        "row_count": len(rows),
        "sources": sources,
        "series": series,
        "x_min": min(x_values) if x_values else None,
        "x_max": max(x_values) if x_values else None,
        "y_min": min(y_values) if y_values else None,
        "y_max": max(y_values) if y_values else None,
    }


def write_figure_report(output_dir: Path, figure_data: dict[str, list[dict[str, object]]], moesm3_manifest: list[dict[str, object]]) -> Path:
    lines: list[str] = [
        "MOESM figure-by-figure comparison",
        "",
        "MOESM2 is the figure level source. MOESM3 is the dense surface source.",
        "",
    ]

    for figure in ["Fig2a", "Fig2b", "Fig2c", "Fig2d"]:
        summary = summarize_figure(figure_data[figure])
        lines.extend(
            [
                f"## {figure}",
                f"- rows in calculation-ready CSV: {summary['row_count']}",
                f"- sources: {', '.join(summary['sources'])}",
                f"- series: {', '.join(summary['series'])}",
                f"- x range: {summary['x_min']} to {summary['x_max']}",
                f"- y range: {summary['y_min']} to {summary['y_max']}",
            ]
        )

        if figure == "Fig2a":
            lines.extend(
                [
                    "- comparison: experimental points, two fit branches, and a simulation branch share the same time axis but use different sampling grids.",
                    "- calculation note: interpolate fits or simulation onto the experimental x grid before residuals.",
                ]
            )
        elif figure == "Fig2b":
            lines.extend(
                [
                    "- comparison: experiment is sparse, theory is dense, and eta^2 is kept as a reference curve.",
                    "- calculation note: this figure is best suited to interpolation and slope comparisons.",
                ]
            )
        elif figure == "Fig2c":
            lines.extend(
                [
                    "- comparison: two initial-state branches are measured and fitted on a denser phase grid.",
                    "- calculation note: compare the up/down branches separately before any aggregation.",
                ]
            )
        elif figure == "Fig2d":
            lines.extend(
                [
                    "- comparison: a small set of experimental phase points is matched to a dense fit curve.",
                    "- calculation note: the fit grid is the natural object for smooth derivative or threshold checks.",
                ]
            )
        lines.append("")

    lines.extend(
        [
            "## MOESM3 surface families",
            "- sqz_exp / sqz_sim and trisqz_exp / trisqz_sim share 441 x 441 grids.",
            "- quadsqz_exp / quadsqz_sim share 451 x 451 grids.",
            "- the experimental domains are broader than the simulation domains, so they are not pointwise identical and should be compared by resampling or topology metrics.",
            "",
        ]
    )

    report_path = output_dir / "figure_by_figure_comparison.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    root = project_root()
    base = export_root(root)
    output_dir = base / "figure_packages"
    output_dir.mkdir(parents=True, exist_ok=True)

    figure_builders = {
        "Fig2a": build_fig2a(root),
        "Fig2b": build_fig2b(root),
        "Fig2c": build_fig2c(root),
        "Fig2d": build_fig2d(root),
    }

    master_rows: list[dict[str, object]] = []
    for rows in figure_builders.values():
        master_rows.extend(rows)

    fieldnames = ["figure", "source", "series", "x_name", "x_value", "y_name", "y_value", "y_err_value", "source_sheet"]
    write_csv(output_dir / "moesm2_calculation_ready.csv", master_rows, fieldnames)

    for figure, rows in figure_builders.items():
        write_csv(output_dir / f"{figure}_calculation_ready.csv", rows, fieldnames)

    moesm3_manifest = build_moesm3_manifest(root)
    write_csv(
        output_dir / "moesm3_surface_manifest.csv",
        moesm3_manifest,
        ["sheet", "data_rows", "columns", "numeric_min", "numeric_max", "csv_path", "first_col_labels"],
    )

    report_path = write_figure_report(output_dir, figure_builders, moesm3_manifest)

    manifest = {
        "output_dir": str(output_dir),
        "master_csv": str(output_dir / "moesm2_calculation_ready.csv"),
        "figure_csvs": {figure: str(output_dir / f"{figure}_calculation_ready.csv") for figure in figure_builders},
        "moesm3_manifest": str(output_dir / "moesm3_surface_manifest.csv"),
        "comparison_report": str(report_path),
    }
    (output_dir / "figure_packages_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()