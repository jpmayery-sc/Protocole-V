"""Check internal and external consistency for V16 predictions."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v16prediction_core import evaluate_consistency, result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict:
    outdir = result_dir(output_dir)
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    evaluation = evaluate_consistency()

    payload = {
        "timestamp": timestamp,
        "hypothesis": "la coherence interne et la coherence interne vers externe restent compatibles",
        "case_control": "V16 internal + external",
        "observable": "internal_ok, external_ok, consistency_ok",
        "expected": "les trois verifications passent",
        "measured": {
            "internal_ok": evaluation["internal_ok"],
            "external_ok": evaluation["external_ok"],
            "consistency_ok": evaluation["consistency_ok"],
        },
        "internal": evaluation["internal"],
        "external": evaluation["external"],
        "verdict": evaluation["verdict"],
        "reference": "V16 consistency gate",
    }

    json_path = outdir / f"v16check_check_{timestamp}.json"
    txt_path = outdir / f"v16check_check_{timestamp}.txt"
    write_report(json_path, payload)
    txt_lines = [
        "V16 check",
        f"timestamp: {timestamp}",
        f"verdict: {payload['verdict']}",
        f"internal_ok: {evaluation['internal_ok']}",
        f"external_ok: {evaluation['external_ok']}",
        f"consistency_ok: {evaluation['consistency_ok']}",
    ]
    txt_path.write_text("\n".join(txt_lines) + "\n", encoding="utf-8")
    payload["json_path"] = str(json_path)
    payload["txt_path"] = str(txt_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Check internal and external consistency for V16 predictions.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()