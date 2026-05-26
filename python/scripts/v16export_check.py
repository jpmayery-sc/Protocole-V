"""Export the V16 prediction package."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v16prediction_core import export_prediction, result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    payload_body = export_prediction()
    payload = {
        "timestamp": timestamp,
        "hypothesis": "la prediction V16 peut etre exportee proprement en structure claire",
        "case_control": "package final interne + externe",
        "observable": "dict, json, table",
        "expected": "structure exportee stable et verifiee",
        "measured": {
            "export_keys": list(payload_body.keys()),
        },
        **payload_body,
        "verdict": payload_body["verdict"],
        "reference": "V16 export package",
    }

    json_path = outdir / f"v16export_check_{timestamp}.json"
    txt_path = outdir / f"v16export_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V16 export check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"export_keys: {', '.join(payload['measured']['export_keys'])}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Export the V16 prediction package.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()