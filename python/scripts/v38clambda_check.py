from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v29finaltheory_core import v29_result_dir, write_report
from v38lambda_check import evaluate_v38_lambda


def evaluate_v38c_lambda() -> dict[str, object]:
    payload = evaluate_v38_lambda()
    payload["section"] = "V38c-LAMBDA"
    payload["verdict"] = payload["v38_lambda_verdict"]
    return payload


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v29_result_dir(output_dir) / "v38c_cosmology"
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v38clambda_check_{timestamp}.json"
    txt_path = result_dir / f"v38clambda_check_{timestamp}.txt"

    payload = {**evaluate_v38c_lambda(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text(
        "\n".join(
            [
                "V38c lambda check",
                f"timestamp: {timestamp}",
                f"verdict: {payload['verdict']}",
                f"lambda_match_ok: {payload['lambda_match_ok']}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V38c Lambda check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()