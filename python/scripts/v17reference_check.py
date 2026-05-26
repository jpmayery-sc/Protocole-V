"""Load the external reference set used to validate V16 predictions."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v17validation_core import load_reference, v17_result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = v17_result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    reference = load_reference()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "un referentiel externe minimal peut servir de base de validation pour V16",
        "case_control": "bornes theoriques minimales",
        "observable": ", ".join(reference["order"]),
        "expected": "bornes et cibles de reference disponibles",
        "measured": {
            "locked_names": reference["locked_names"],
            "frozen_names": reference["frozen_names"],
            "reference_source": reference["source"],
        },
        "reference": reference,
        "verdict": "supported",
        "reference_label": "V17 reference gate",
    }

    json_path = outdir / f"v17reference_check_{timestamp}.json"
    txt_path = outdir / f"v17reference_check_{timestamp}.txt"
    write_report(json_path, payload)

    txt_lines = [
        "V17 reference check",
        f"timestamp: {timestamp}",
        "verdict: supported",
        f"source: {reference['source']}",
        f"targets: {', '.join(reference['targets'].keys())}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the external reference set used to validate V16 predictions.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()