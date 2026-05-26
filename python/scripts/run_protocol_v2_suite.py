"""Run the protocol V2 readiness checks and summarize the result.

The protocol V2 document requires HF transport data that is not yet present in
the repository. This runner therefore separates two concerns:

* actual evidence already available from adjacent suites;
* readiness of the repository to execute the H1-H4 protocol as written.

The final verdict is honest about missing data instead of pretending the
protocol has been fully validated.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

if __package__ in (None, ""):
    script_dir = Path(__file__).resolve().parent
    if str(script_dir) not in sys.path:
        sys.path.insert(0, str(script_dir))


def workspace_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def write_markdown_report(summary: dict, result_dir: Path) -> Path:
    report_path = result_dir / "protocole_v2.md"
    stages = summary.get("stages", [])
    evidence = summary.get("adjacent_evidence", [])
    missing = summary.get("missing_inputs", [])

    lines = [
        "# Protocole V2",
        "",
        "## But",
        "Verifier la loi de transport et sa robustesse sur les etages H1 a H4.",
        "",
        "## Verdict",
        f"- Verdict global: {summary.get('overall_verdict', 'unknown')}",
        f"- Statut des donnees: {summary.get('data_status', 'unknown')}",
        f"- Jeux attendus: {', '.join(summary.get('expected_metals', []))}",
        "",
        "## Etages",
    ]
    for stage in stages:
        lines.append(f"- {stage['id']}: {stage['verdict']} - {stage['title']}")
        if stage.get("reason"):
            lines.append(f"  - {stage['reason']}")

    lines.extend([
        "",
        "## Evidence adjacente deja disponible",
    ])
    for item in evidence:
        lines.append(f"- {item['label']}: {item['verdict']} -> {item['json_path']}")

    lines.extend([
        "",
        "## Manques bloquants",
    ])
    if missing:
        for item in missing:
            lines.append(f"- {item}")
    else:
        lines.append("- Aucun manque bloque detecte dans le manifeste.")

    lines.extend([
        "",
        "## Lecture courte",
        "Le protocole est structurellement pret, mais la validation numerique H1-H4 reste bloquee tant qu'un jeu HF transport exploitable n'est pas present.",
    ])
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return report_path


def run_script(command: list[str]) -> None:
    print(f"Running: {Path(command[1]).name}")
    subprocess.run(command, check=True)


def collect_adjacent_evidence() -> list[dict]:
    root = workspace_root()
    scripts_dir = root / "python" / "scripts"
    evidence_specs = [
        ("material_conductivity", scripts_dir / "run_conductivity_suite.py"),
        ("current_regime", scripts_dir / "run_current_regime_suite.py"),
        ("induction", scripts_dir / "run_induction_suite.py"),
        ("skin_effect", scripts_dir / "run_skin_suite.py"),
        ("saturation_magnetic", scripts_dir / "run_saturation_suite.py"),
    ]

    items: list[dict] = []
    for label, script_path in evidence_specs:
        command = [sys.executable, str(script_path)]
        run_script(command)
        result_dir = root / "results" / "result-analyse"
        if label == "material_conductivity":
            json_name = "material_conductivity_suite_summary_"
        elif label == "current_regime":
            json_name = "current_regime_suite_summary_"
        elif label == "induction":
            json_name = "induction_suite_summary_"
        elif label == "skin_effect":
            json_name = "skin_effect_suite_summary_"
        else:
            json_name = "saturation_magnetic_suite_summary_"

        matches = sorted(result_dir.glob(f"{json_name}*.json"))
        if not matches:
            raise FileNotFoundError(f"No summary found for {label} in {result_dir}")
        report_path = matches[-1]
        report = json.loads(report_path.read_text(encoding="utf-8"))
        verdict = report.get("overall_verdict") or report.get("verdict") or "unknown"
        items.append(
            {
                "label": label,
                "verdict": verdict,
                "json_path": str(report_path),
                "txt_path": report.get("txt_path") or str(report_path.with_suffix(".txt")),
            }
        )
    return items


def collect_data_status(root: Path) -> dict:
    expected_metals = ["Cu", "Al", "Ag", "Fe"]
    manifest_path = root / "python" / "data" / "hf_transport_manifest.json"
    manifest = load_json(manifest_path)

    if manifest is None:
        return {
            "expected_metals": expected_metals,
            "manifest_path": str(manifest_path.relative_to(root)),
            "manifest_status": "missing",
            "found_manifests": [],
            "missing_inputs": [f"missing manifest: {manifest_path.relative_to(root)}"],
            "data_status": "missing",
        }

    manifest_status = str(manifest.get("status", "template")).lower()
    datasets = manifest.get("datasets", {})
    dataset_paths = []
    missing_inputs = []

    if isinstance(datasets, dict):
        items = datasets.items()
    else:
        items = []

    for label, entry in items:
        relative_path = entry.get("file") or entry.get("path")
        if not relative_path:
            missing_inputs.append(f"missing dataset file entry for {label}")
            continue

        dataset_path = root / relative_path.replace("/", "\\")
        dataset_paths.append(str(dataset_path.relative_to(root)))
        if not dataset_path.exists():
            missing_inputs.append(f"missing dataset: {dataset_path.relative_to(root)}")
            continue

        record_count = entry.get("record_count")
        if record_count is not None and int(record_count) <= 0:
            missing_inputs.append(f"empty dataset: {dataset_path.relative_to(root)}")

    if manifest_status != "ready":
        data_status = "template"
    elif missing_inputs:
        data_status = "missing"
    else:
        data_status = "ready"

    if manifest_status != "ready" and not missing_inputs:
        missing_inputs.append(f"manifest status is {manifest_status}")

    return {
        "expected_metals": expected_metals,
        "manifest_path": str(manifest_path.relative_to(root)),
        "manifest_status": manifest_status,
        "found_manifests": [str(manifest_path.relative_to(root))],
        "found_datasets": dataset_paths,
        "missing_inputs": missing_inputs,
        "data_status": data_status,
    }


def build_summary(result_dir: Path) -> dict:
    root = workspace_root()
    data_status = collect_data_status(root)
    adjacent_evidence = collect_adjacent_evidence()

    stages = [
        {
            "id": "H1",
            "title": "Local model only",
            "verdict": "blocked" if data_status["data_status"] != "ready" else "pending",
            "reason": "No HF transport dataset is available to compare K_loc against measured residuals." if data_status["data_status"] != "ready" else "Ready to fit K_loc against the declared data.",
        },
        {
            "id": "H2",
            "title": "Global alpha' correction",
            "verdict": "blocked" if data_status["data_status"] != "ready" else "pending",
            "reason": "The protocol needs a frozen global fit on Cu before cross-material testing." if data_status["data_status"] != "ready" else "Ready to freeze alpha' after the Cu fit.",
        },
        {
            "id": "H3",
            "title": "Quadratic beta' term",
            "verdict": "blocked" if data_status["data_status"] != "ready" else "pending",
            "reason": "There is no material-resolved HF set for Fe or Ni to test nonlinearity." if data_status["data_status"] != "ready" else "Ready to test beta' on the nonlinear materials.",
        },
        {
            "id": "H4",
            "title": "Mass-weighted FTM comparison",
            "verdict": "blocked" if data_status["data_status"] != "ready" else "pending",
            "reason": "The repository does not yet expose the inter-material HF observables needed for sigma sqrt(m) comparison." if data_status["data_status"] != "ready" else "Ready to compare the mass-weighted observable across metals.",
        },
    ]

    overall_verdict = "pending" if data_status["data_status"] == "ready" else "blocked"

    return {
        "suite": "protocol_v2",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "overall_verdict": overall_verdict,
        "supported_count": sum(1 for stage in stages if stage["verdict"] == "supported"),
        "total": len(stages),
        "stages": stages,
        "adjacent_evidence": adjacent_evidence,
        **data_status,
    }


def write_summary(summary: dict, result_dir: Path) -> tuple[Path, Path]:
    result_dir.mkdir(parents=True, exist_ok=True)
    timestamp = summary["timestamp"]
    json_path = result_dir / f"protocol_v2_suite_summary_{timestamp}.json"
    txt_path = result_dir / f"protocol_v2_suite_summary_{timestamp}.txt"

    payload = {**summary, "json_path": str(json_path), "txt_path": str(txt_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Protocol V2 suite summary",
        f"timestamp: {timestamp}",
        f"overall_verdict: {summary['overall_verdict']}",
        f"data_status: {summary['data_status']}",
        f"supported_count: {summary['supported_count']}/{summary['total']}",
        "",
        "Stages:",
    ]
    for stage in summary["stages"]:
        lines.append(f"- {stage['id']}: {stage['verdict']} -> {stage['title']}")
    lines.extend([
        "",
        "Adjacent evidence:",
    ])
    for item in summary["adjacent_evidence"]:
        lines.append(f"- {item['label']}: {item['verdict']} -> {item['json_path']}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    report_path = write_markdown_report(summary, result_dir)
    summary["report_path"] = str(report_path)
    return json_path, txt_path


def run_suite(output_dir: str | Path | None = None) -> dict:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse"

    summary = build_summary(result_dir)
    json_path, txt_path = write_summary(summary, result_dir)
    summary["json_path"] = str(json_path)
    summary["txt_path"] = str(txt_path)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the protocol V2 readiness checks and summarize them.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite summary")
    args = parser.parse_args()

    result = run_suite(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()