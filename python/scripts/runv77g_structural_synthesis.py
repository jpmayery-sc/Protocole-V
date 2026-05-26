"""Run the V77G structural synthesis from the existing V77 results."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from runv80_bbn_scan import workspace_root


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def collect_source_texts(root: Path) -> dict[str, str]:
    paths = {
        "v77c": root / "ProtocoleV77C.md",
        "v77d": root / "ProtocoleV77D.md",
        "v77e": root / "ProtocoleV77E.md",
        "v77f": root / "ProtocoleV77F.md",
        "v77c_summary": root / "results" / "result-analyse" / "v77c_a7_autopsy" / "V77C_A7_STRUCTURE.txt",
        "v77d_summary": root / "results" / "result-analyse" / "v77d_triplet_epn" / "v77d_triplet_epn_summary_20260521-105527Z.txt",
        "v77e_summary": root / "results" / "result-analyse" / "v77e_a7_exchange_drain" / "v77e_exchange_drain_summary_20260521-113729Z.txt",
        "v77f_summary": root / "results" / "result-analyse" / "v77f_curve_shape" / "V77F_CURVE_SHAPE.txt",
    }
    return {key: read_text(path) for key, path in paths.items() if path.exists()}


def build_summary_text(source_texts: dict[str, str]) -> str:
    return "\n".join(
        [
            "V77G structural synthesis",
            "",
            "1) Ce que le proxy a appris",
            "- V77C : Li_total = Li7 + Be7, verrou structurel positif sans destruction explicite.",
            "- V77D : beta_e crée une pente monotone et convexe sur Li_total.",
            "- V77E : exchange + drain renverse l’équilibre A=7 et ouvre une zone de passage de largeur moyenne.",
            "- V77F : la courbe Li_total montre une pente nette, sans point de bascule interne marqué.",
            "",
            "2) Schéma minimal A=7",
            "- Variables : Li7, Be7, Li_total = Li7 + Be7.",
            "- Leviers : delta_EM, beta_e, gamma_exch, gamma_drain.",
            "- Rôles : delta_EM ajuste, beta_e incline, gamma_exch redistribue, gamma_drain vide.",
            "",
            "3) Questions pour le réel",
            "- Existe-t-il un levier électronique analogue à beta_e ?",
            "- Les destructions A=7 peuvent-elles jouer le rôle de gamma_drain ?",
            "- Les échanges Be7 <-> Li7 ont-ils un analogue réaliste ?",
            "- Le code réel reproduit-il une pente nette avec une zone de passage moyenne ?",
            "",
            "4) Phrase de synthèse",
            "Le proxy jouet A=7 montre qu’un levier électronique (beta_e) combiné à un schéma échange + vidange (gamma_exch, gamma_drain) permet de renverser l’équilibre interne A=7 et de faire passer Li_total dans une zone acceptable de largeur moyenne.",
            "V78R devra tester si des mécanismes physiques réels peuvent reproduire cette géométrie de courbe.",
            "",
            "5) Extraits consolidés",
        ]
        + [f"[{key}]" for key in sorted(source_texts.keys())]
    )


def write_output(summary_text: str, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_path = output_dir / "V77G_STRUCTURAL_SUMMARY.txt"
    txt_path.write_text(summary_text + "\n", encoding="utf-8")

    json_path = output_dir / f"v77g_structural_synthesis_summary_{time.strftime('%Y%m%d-%H%M%SZ')}.json"
    payload = {
        "suite": "v77g_structural_synthesis",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "txt_path": str(txt_path),
        "source_keys": ["v77c", "v77d", "v77e", "v77f"],
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return txt_path, json_path


def run_synthesis(output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77g_structural_synthesis"

    source_texts = collect_source_texts(root)
    summary_text = build_summary_text(source_texts)
    txt_path, json_path = write_output(summary_text, result_dir)

    return {
        "suite": "v77g_structural_synthesis",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "txt_path": str(txt_path),
        "json_path": str(json_path),
        "output_dir": str(result_dir),
        "source_count": len(source_texts),
        "source_keys": sorted(source_texts.keys()),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77G structural synthesis.")
    parser.add_argument("--output-dir", default=None, help="Directory for the suite outputs")
    args = parser.parse_args()

    result = run_synthesis(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()