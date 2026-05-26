"""Development wrapper for V77L physical levers.

This module does not pretend to patch AlterBBN/PArthENoPE directly because the
real external BBN sources are not present in this workspace. Instead it defines
an explicit adapter boundary, the physical lever parameters, and a dry-run
verification path that can be wired to a real BBN executable or codebase later.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path

from runv80_bbn_scan import workspace_root


@dataclass(frozen=True)
class LeverConfig:
    beta_e_phys: float = 1.0
    gamma_exch_phys: float = 0.0
    gamma_drain_phys: float = 0.0
    k_screen: float = 0.2
    k_capture: float = 0.3
    a_li7pa: float = 0.6
    a_be7np: float = 0.4
    a_be7dp: float = 0.2
    b_be7np: float = 0.7
    b_be7dp: float = 0.3


def apply_beta_e_phys(base: dict[str, float], config: LeverConfig) -> dict[str, float]:
    beta_shift = config.beta_e_phys - 1.0
    screening_eff = 1.0 + config.k_screen * beta_shift
    capture_eff = 1.0 + config.k_capture * beta_shift

    result = dict(base)
    result["screening_eff"] = screening_eff
    result["capture_eff"] = capture_eff
    result["Li7_over_H"] = base["Li7_over_H"] * capture_eff
    result["Be7_over_H"] = base["Be7_over_H"] / capture_eff
    result["Li_total_over_H"] = result["Li7_over_H"] + result["Be7_over_H"]
    result["beta_response_ok"] = beta_shift >= -1.0
    return result


def apply_gamma_drain_phys(base: dict[str, float], config: LeverConfig) -> dict[str, float]:
    result = dict(base)
    drain_factor = 1.0 + config.gamma_drain_phys * (config.a_li7pa + config.a_be7np + config.a_be7dp)
    result["Li7_over_H"] = base["Li7_over_H"] / drain_factor
    result["Be7_over_H"] = base["Be7_over_H"] / drain_factor
    result["Li_total_over_H"] = result["Li7_over_H"] + result["Be7_over_H"]
    result["drain_response_ok"] = drain_factor >= 1.0
    return result


def apply_gamma_exch_phys(base: dict[str, float], config: LeverConfig) -> dict[str, float]:
    result = dict(base)
    exch_boost = 1.0 + config.gamma_exch_phys * (config.b_be7np + config.b_be7dp)
    result["Li7_over_H"] = base["Li7_over_H"] * exch_boost
    result["Be7_over_H"] = base["Be7_over_H"] / exch_boost
    result["Li_total_over_H"] = result["Li7_over_H"] + result["Be7_over_H"]
    result["exchange_response_ok"] = exch_boost >= 1.0
    return result


def toy_bbn_standard() -> dict[str, float]:
    return {
        "D_over_H": 2.527e-5,
        "Y_p": 0.2436,
        "Li7_over_H": 1.1e-10,
        "Be7_over_H": 0.0,
        "Li_total_over_H": 1.1e-10,
    }


def run_bbn(beta_e_phys: float, gamma_exch_phys: float, gamma_drain_phys: float, config_cosmo: dict[str, float] | None = None) -> dict[str, float]:
    """Dry-run BBN wrapper.

    The function is intentionally deterministic and small so it can be swapped
    out for a real external code call once the actual BBN source tree is
    available.
    """

    base = toy_bbn_standard()
    config = LeverConfig(
        beta_e_phys=beta_e_phys,
        gamma_exch_phys=gamma_exch_phys,
        gamma_drain_phys=gamma_drain_phys,
    )

    after_beta = apply_beta_e_phys(base, config)
    after_exchange = apply_gamma_exch_phys(after_beta, config)
    after_drain = apply_gamma_drain_phys(after_exchange, config)

    # Keep the cosmological observables stable for modest lever shifts.
    result = dict(after_drain)
    result["D_over_H"] = base["D_over_H"] * (1.0 - 0.005 * (beta_e_phys - 1.0))
    result["Y_p"] = base["Y_p"] + 0.001 * (beta_e_phys - 1.0)
    result["Li_total_over_H"] = result["Li7_over_H"] + result["Be7_over_H"]
    if config_cosmo:
        result.update({f"cosmo_{key}": value for key, value in config_cosmo.items()})
    return result


def implementation_check() -> list[dict[str, float]]:
    points = [
        (1.0, 0.0, 0.0),
        (1.1, 0.0, 0.0),
        (1.0, 0.5, 0.0),
        (1.0, 0.0, 0.3),
        (1.1, 0.5, 0.3),
    ]
    rows: list[dict[str, float]] = []
    for beta_e_phys, gamma_exch_phys, gamma_drain_phys in points:
        row = run_bbn(beta_e_phys, gamma_exch_phys, gamma_drain_phys)
        row.update(
            {
                "beta_e_phys": beta_e_phys,
                "gamma_exch_phys": gamma_exch_phys,
                "gamma_drain_phys": gamma_drain_phys,
            }
        )
        rows.append(row)
    return rows


def write_check_log(rows: list[dict[str, float]], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    log_path = output_dir / "V77L_IMPLEMENTATION_CHECK.txt"
    lines = [
        "V77L implementation check",
        f"timestamp: {time.strftime('%Y%m%d-%H%M%SZ')}",
        "mode: dry-run adapter because no external BBN source tree is present in the workspace",
        "",
    ]
    for row in rows:
        lines.append(
            "- beta_e_phys={beta_e_phys:.3f}, gamma_exch_phys={gamma_exch_phys:.3f}, gamma_drain_phys={gamma_drain_phys:.3f}, D/H={D_over_H:.6e}, Y_p={Y_p:.6f}, Li7/H={Li7_over_H:.6e}, Be7/H={Be7_over_H:.6e}, Li_total/H={Li_total_over_H:.6e}".format(
                **row
            )
        )
    lines.append("")
    lines.append("Interpretation:")
    lines.append("- beta_e_phys increases Li7 capture and reduces Be7 in the dry-run adapter.")
    lines.append("- gamma_drain_phys reduces both A=7 channels in the dry-run adapter.")
    lines.append("- gamma_exch_phys redistributes Li7/Be7 without fully emptying A=7.")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_path


def run_v77l(output_dir: str | Path | None = None) -> dict[str, object]:
    root = workspace_root()
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v77l_physical_levers_impl"
    result_dir.mkdir(parents=True, exist_ok=True)

    rows = implementation_check()
    log_path = write_check_log(rows, result_dir)

    payload = {
        "suite": "v77l_physical_levers_impl",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "rows": rows,
        "log_path": str(log_path),
        "notes": [
            "No external AlterBBN/PArthENoPE source tree was available in the workspace.",
            "This is an explicit adapter boundary, not a claim of patching a real BBN code here.",
        ],
    }
    summary_path = result_dir / f"v77l_physical_levers_impl_summary_{payload['timestamp']}.json"
    summary_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    payload["summary_path"] = str(summary_path)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V77L physical lever implementation dry-run.")
    parser.add_argument("--output-dir", default=None, help="Directory for the V77L outputs")
    args = parser.parse_args()

    result = run_v77l(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()