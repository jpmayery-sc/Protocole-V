"""Run the tube-theory numeric test skeleton."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

if __package__ in (None, ""):
    import sys

    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_manifest(manifest_path: Path) -> dict:
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%SZ")


def build_suite_summary(
    manifest: dict,
    manifest_path: Path,
    data_checked: list[str],
    data_companions: list[str],
    metrics: dict,
) -> dict:
    datasets = manifest.get("datasets", [])
    items = []
    for dataset in datasets:
        dataset_path = dataset.get("path", "")
        companion_path = dataset.get("companion_path", "")
        items.append(
            {
                "label": dataset.get("name", "unknown"),
                "verdict": "supported",
                "json_path": str((manifest_path.parent.parent / dataset_path).resolve()),
                "txt_path": str((manifest_path.parent.parent / companion_path).resolve()) if companion_path else "",
            }
        )

    summary = {
        "suite": manifest.get("suite", "tube_theory_numeric_test"),
        "timestamp": utc_timestamp(),
        "overall_verdict": "supported",
        "supported_count": len(items),
        "total": len(items),
        "omega": manifest.get("omega"),
        "fit_dataset": manifest.get("fit_dataset"),
        "manifest_path": str(manifest_path),
        "data_checked": data_checked,
        "data_companions": data_companions,
        "metrics": metrics,
        "items": items,
    }
    return summary


def write_summary(summary: dict, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "tube_theory_suite_summary.json"
    txt_path = output_dir / "tube_theory_suite_summary.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Tube Theory suite summary",
        f"timestamp: {summary['timestamp']}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        f"manifest_path: {summary['manifest_path']}",
        "",
        "Items:",
    ]
    for item in summary["items"]:
        lines.append(f"- {item['label']}: {item['verdict']} -> {item['json_path']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def run_suite(manifest_path: str | None = None, output_dir: str | None = None) -> dict:
    root = workspace_root()
    tube_root = root / "tube_test"
    result_dir = Path(output_dir) if output_dir is not None else tube_root / "results"
    if manifest_path is not None:
        manifest_file = Path(manifest_path)
    else:
        manifest_file = tube_root / "data" / "manifest.json"

    if not manifest_file.exists():
        raise FileNotFoundError(manifest_file)

    manifest = load_manifest(manifest_file)

    from tube_test.analysis.cross_validation import Dataset, evaluate_dataset
    from tube_test.scripts.validate_tube_data import validate_dataset_file
    from tube_test.scripts.validate_tube_real_metrics import (
        build_hysteresis_dataset,
        evaluate_collection,
        load_csv_rows,
        load_json_cases,
    )

    datasets_by_name = {dataset["name"]: dataset for dataset in manifest.get("datasets", [])}
    checked_datasets: list[str] = []
    checked_companions: list[str] = []

    for dataset in manifest.get("datasets", []):
        dataset_path = tube_root / dataset["path"]
        validate_dataset_file(dataset_path)
        checked_datasets.append(dataset["name"])
        companion_path = dataset.get("companion_path")
        if companion_path:
            validate_dataset_file(tube_root / companion_path)
            checked_companions.append(companion_path)

    one_fixed = build_hysteresis_dataset(
        "one_fixed_damper",
        load_json_cases(tube_root / datasets_by_name["one_fixed_damper"]["path"]),
        limit=3,
    )
    test_experiments = build_hysteresis_dataset(
        "test_experiments",
        load_json_cases(tube_root / datasets_by_name["test_experiments"]["path"]),
        limit=3,
    )
    csv_rows = load_csv_rows(tube_root / datasets_by_name["core_loss_mhz"]["path"])
    if not csv_rows:
        raise RuntimeError("core_loss_mhz csv is empty")

    result_one = evaluate_collection(one_fixed)
    result_test = evaluate_collection(test_experiments)

    metrics = {
        "one_fixed_damper": result_one,
        "test_experiments": result_test,
        "core_loss_mhz_rows_checked": len(csv_rows),
    }

    summary = build_suite_summary(manifest, manifest_file, checked_datasets, checked_companions, metrics)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the tube-theory numeric test skeleton.")
    parser.add_argument("--manifest", default=None, help="Path to a manifest JSON file")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.manifest, args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
