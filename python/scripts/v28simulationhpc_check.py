from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v28completephysics_core import evaluate_simulation_hpc, v28_result_dir, write_report


def run_check(output_dir: str | Path | None = None) -> dict[str, object]:
    result_dir = v28_result_dir(output_dir)
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    json_path = result_dir / f"v28simulationhpc_check_{timestamp}.json"
    txt_path = result_dir / f"v28simulationhpc_check_{timestamp}.txt"

    payload = {**evaluate_simulation_hpc(), "timestamp": timestamp, "json_path": str(json_path), "txt_path": str(txt_path)}
    write_report(json_path, payload)
    txt_path.write_text("V28 simulation HPC check\n" + json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V28 simulation HPC check.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()
    print(json.dumps(run_check(args.output_dir), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()