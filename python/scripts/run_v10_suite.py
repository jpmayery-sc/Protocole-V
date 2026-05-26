"""Run the V10 source-base summary and write a compact report."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from v10_sources import summarize_v10_sources, workspace_root


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"v10_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"v10_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V10 suite summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        f"manifest_status: {summary['manifest_status']}",
        f"bridge_ready_count: {summary['bridge_ready_count']}",
        "",
        "Sources:",
    ]
    for item in summary["items"]:
        lines.append(
            f"- {item['label']}: {item['verdict']} | status={item['status']} | bridge={item['bridge_value']} | {item['json_path']}"
        )
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return json_path, txt_path


def build_summary() -> dict:
    root = workspace_root()
    manifest_summary = summarize_v10_sources(root)
    items = []
    supported = 0

    for source in manifest_summary["sources"]:
        verdict = "supported" if source["index_status"] in {"partial", "metadata_only"} and source["ingest_exists"] else "blocked"
        if verdict == "supported":
            supported += 1
        items.append(
            {
                "label": source["id"],
                "verdict": verdict,
                "json_path": str((root / source["local_ingest_path"]).resolve()),
                "txt_path": str((root / source["local_readme_path"]).resolve()),
                "status": source["index_status"],
                "bridge_value": source.get("bridge_value"),
                "source_type": source.get("source_type"),
            }
        )

    overall_verdict = "supported" if supported == len(items) else ("contradicted" if supported == 0 else "partiel")

    return {
        "suite": "v10",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": supported,
        "total": len(items),
        "manifest_status": manifest_summary["manifest_status"],
        "bridge_ready_count": manifest_summary["bridge_ready_count"],
        "items": items,
    }


def run_suite(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "python" / "results" / "v10"

    summary = build_summary()
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V10 source-base summary.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
