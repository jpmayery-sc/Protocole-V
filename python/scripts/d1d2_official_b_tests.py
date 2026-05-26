"""Run the official D1/D2 suite B: inter-family comparisons."""
from __future__ import annotations

import json

from official_d1d2_verdict import project_root, run_suite


def main() -> None:
    manifest = project_root() / "data" / "d1d2" / "official_b_tests.json"
    result = run_suite(manifest)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
