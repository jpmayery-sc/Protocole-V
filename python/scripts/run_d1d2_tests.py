"""Run the standardized D1/D2 series for the atom pipeline."""
from __future__ import annotations

import json
from pathlib import Path

from d1d2_pipeline import analyze_file, project_root


def main() -> None:
    root = project_root()
    data_dir = root / "data" / "d1d2"
    output_dir = root / "results" / "d1d2"

    family_files = [
        data_dir / "tetrel_d1d2_test.json",
        data_dir / "halogen_d1d2_test.json",
        data_dir / "lanthanide_d1d2_test.json",
    ]

    results = []
    for family_file in family_files:
        result = analyze_file(family_file, output_dir)
        results.append(result)
        print(f"Test done: {family_file.name} -> {result['verdict']}")

    summary = {
        "timestamp": results[0]["json_path"].split("_")[-1].split(".")[0] if results else None,
        "series": [
            {
                "familyname": result["familyname"],
                "verdict": result["verdict"],
                "family_regime": result["observables"]["family_regime"],
                "json_path": result["json_path"],
                "txt_path": result["txt_path"],
            }
            for result in results
        ],
    }

    summary_path = output_dir / "d1d2_series_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote series summary to {summary_path}")


if __name__ == "__main__":
    main()