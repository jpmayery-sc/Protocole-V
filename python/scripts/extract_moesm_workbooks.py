"""Export the downloaded MOESM workbooks to CSV and write a comparison report.

This script is intentionally small and data-only:
- it exports every worksheet from MOESM2.xlsx and MOESM3.xlsx to CSV files,
- it writes workbook-level and sheet-level summaries,
- it produces a compact comparison report for downstream theory work.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from collections import defaultdict
from pathlib import Path

from openpyxl import load_workbook


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def workbook_specs(root: Path) -> list[tuple[str, Path]]:
    return [
        ("MOESM2", root / "results" / "downloaded_xlsx" / "MOESM2.xlsx"),
        ("MOESM3", root / "results" / "downloaded_xlsx" / "MOESM3.xlsx"),
    ]


def sanitize_sheet_name(name: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in name)


def as_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value)


def export_sheet_to_csv(ws, csv_path: Path) -> dict:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    data_rows = 0
    numeric_min = None
    numeric_max = None
    first_col_labels: set[str] = set()
    header: tuple[object, ...] = ()

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        for row_index, row in enumerate(ws.iter_rows(values_only=True)):
            if row_index == 0:
                header = row or ()
            else:
                data_rows += 1
                if row and row[0] is not None and isinstance(row[0], str):
                    first_col_labels.add(row[0])
                for value in row:
                    if isinstance(value, (int, float)) and not isinstance(value, bool) and not math.isnan(float(value)):
                        numeric = float(value)
                        numeric_min = numeric if numeric_min is None else min(numeric_min, numeric)
                        numeric_max = numeric if numeric_max is None else max(numeric_max, numeric)
            writer.writerow([as_text(value) for value in row])

    return {
        "sheet": ws.title,
        "rows_including_header": data_rows + (1 if header else 0),
        "data_rows": data_rows,
        "columns": len(header),
        "header": list(header),
        "numeric_min": numeric_min,
        "numeric_max": numeric_max,
        "first_col_labels": sorted(first_col_labels),
    }


def export_workbook(name: str, workbook_path: Path, output_dir: Path) -> dict:
    wb = load_workbook(workbook_path, data_only=True, read_only=True)
    workbook_dir = output_dir / name
    workbook_dir.mkdir(parents=True, exist_ok=True)

    sheet_summaries = []
    for ws in wb.worksheets:
        csv_path = workbook_dir / f"{sanitize_sheet_name(ws.title)}.csv"
        summary = export_sheet_to_csv(ws, csv_path)
        summary["csv_path"] = str(csv_path)
        sheet_summaries.append(summary)

    workbook_summary = {
        "workbook": name,
        "source_path": str(workbook_path),
        "sheet_count": len(sheet_summaries),
        "sheets": sheet_summaries,
    }

    (workbook_dir / "workbook_summary.json").write_text(
        json.dumps(workbook_summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines = [
        f"{name} workbook summary",
        f"source: {workbook_path}",
        f"sheet_count: {len(sheet_summaries)}",
        "",
    ]
    for sheet in sheet_summaries:
        lines.append(
            f"- {sheet['sheet']}: rows={sheet['data_rows']}, cols={sheet['columns']}, "
            f"numeric_min={sheet['numeric_min']}, numeric_max={sheet['numeric_max']}"
        )
        if sheet["first_col_labels"]:
            lines.append(f"  first_col_labels: {', '.join(sheet['first_col_labels'])}")
    (workbook_dir / "workbook_summary.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    return workbook_summary


def compare_workbooks(moesm2: dict, moesm3: dict, output_dir: Path) -> Path:
    lines = [
        "MOESM workbook comparison",
        f"timestamp: {time.strftime('%Y-%m-%d %H:%M:%SZ')}",
        "",
        "1. Role split",
        "- MOESM2 is figure-oriented: compact tabular data, fits, and simulations for Fig2a to Fig2d.",
        "- MOESM3 is grid-oriented: large pcolormesh-ready surfaces with gamma_r, gamma_im, and W.",
        "",
        "2. Sheet-level comparison",
    ]

    lines.append("- MOESM2 sheets:")
    for sheet in moesm2["sheets"]:
        lines.append(
            f"  - {sheet['sheet']}: rows={sheet['data_rows']}, cols={sheet['columns']}, "
            f"numeric_range=[{sheet['numeric_min']}, {sheet['numeric_max']}]"
        )
    lines.append("- MOESM3 sheets:")
    for sheet in moesm3["sheets"]:
        lines.append(
            f"  - {sheet['sheet']}: rows={sheet['data_rows']}, cols={sheet['columns']}, "
            f"numeric_range=[{sheet['numeric_min']}, {sheet['numeric_max']}]"
        )

    lines.extend(
        [
            "",
            "3. Practical reading for theory",
            "- Use MOESM2 for direct figure reconstruction, parameter extraction, and trend checks.",
            "- Use MOESM3 for contour/heatmap reconstruction, grid-sensitive interpolation tests, and surface topology analysis.",
            "- The two files are complementary rather than redundant.",
            "",
        ]
    )

    report_path = output_dir / "moesm_comparison_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Export MOESM workbooks to CSV and create a comparison report.")
    parser.add_argument("--output-dir", default=None, help="Directory for CSV exports and reports.")
    args = parser.parse_args()

    root = project_root()
    output_dir = Path(args.output_dir) if args.output_dir is not None else root / "results" / "result-analyse" / "moesm_exports"
    output_dir.mkdir(parents=True, exist_ok=True)

    workbook_summaries = {}
    for name, workbook_path in workbook_specs(root):
        if not workbook_path.exists():
            raise FileNotFoundError(workbook_path)
        workbook_summaries[name] = export_workbook(name, workbook_path, output_dir)

    report_path = compare_workbooks(workbook_summaries["MOESM2"], workbook_summaries["MOESM3"], output_dir)

    summary = {
        "output_dir": str(output_dir),
        "workbooks": workbook_summaries,
        "comparison_report": str(report_path),
    }
    (output_dir / "run_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()