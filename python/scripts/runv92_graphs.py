"""Build the V92 article figures from the V91 confrontation data.

This script reuses the V91 calculation scaffold and writes publication-style
PNG figures that compare V90 against LCDM.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt

from runv91_lcdm_compare import run_v91_lcdm_compare


def build_figures(figure_dir: Path, data_dir: Path) -> dict[str, str]:
    summary = run_v91_lcdm_compare(output_dir=data_dir)
    rows = summary["rows"]

    z = [row["z"] for row in rows]
    v_info_v90 = [row["v_info_v90"] for row in rows]
    v_info_lcdm = [row["v_info_lcdm"] for row in rows]
    distance_ratio = [row["distance_ratio"] for row in rows]
    v_ratio = [row["v_ratio"] for row in rows]

    figure_dir.mkdir(parents=True, exist_ok=True)

    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=180)
    ax.plot(z, v_info_lcdm, marker="o", linewidth=2.2, label="LCDM baseline")
    ax.plot(z, v_info_v90, marker="o", linewidth=2.2, label="V90")
    ax.axvline(0.46, linestyle="--", linewidth=1.2, color="#8c564b", alpha=0.8, label="zone critique")
    ax.set_xlabel("redshift z")
    ax.set_ylabel("v_info")
    ax.set_title("V92 - vitesse d'information")
    ax.legend(frameon=True)
    fig.tight_layout()
    vinfo_path = figure_dir / "v92_vinfo_comparison.png"
    fig.savefig(vinfo_path, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8.2, 4.8), dpi=180)
    ax.plot(z, distance_ratio, marker="o", linewidth=2.2, label="d_V90 / d_LCDM")
    ax.plot(z, v_ratio, marker="o", linewidth=2.2, label="v_info,V90 / v_info,LCDM")
    ax.axhline(1.0, linestyle=":", linewidth=1.2, color="#444444", alpha=0.9)
    ax.axvline(0.46, linestyle="--", linewidth=1.2, color="#8c564b", alpha=0.8)
    ax.set_xlabel("redshift z")
    ax.set_ylabel("ratio")
    ax.set_title("V92 - ratios V90 / LCDM")
    ax.legend(frameon=True)
    fig.tight_layout()
    ratio_path = figure_dir / "v92_ratio_comparison.png"
    fig.savefig(ratio_path, bbox_inches="tight")
    plt.close(fig)

    return {
        "summary_path": summary["json_path"],
        "vinfo_path": str(vinfo_path),
        "ratio_path": str(ratio_path),
        "verdict": summary["verdict"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the V92 comparison figures.")
    parser.add_argument("--output-dir", default=None, help="Directory for the figure outputs")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    figure_dir = Path(args.output_dir) if args.output_dir is not None else root / "V70_overleaf" / "figures"
    data_dir = root / "results" / "result-analyse" / "v92_graphs"
    result = build_figures(figure_dir, data_dir)
    print(result)


if __name__ == "__main__":
    main()