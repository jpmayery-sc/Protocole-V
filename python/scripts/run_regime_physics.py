"""Run a regime-aware physics launcher for the D1 / D2 / D3 / D4 grid.

The launcher keeps the API explicit so the next test suite can plug into the
same branch points without reinterpreting the physics model.
"""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Any

from d1d4_model import d1_proxy, fermi_balance_ev, fermi_pressure_pa


REGIME_CHOICES = ("atomique", "metal", "lanthanide", "dense")


@dataclass(frozen=True)
class RegimeRequest:
    regime: str
    element: str | None = None
    ionization_ev: float | None = None
    principal_n: float | None = None
    electron_density_m3: float | None = None


def _base_payload(request: RegimeRequest) -> dict[str, Any]:
    return {
        "regime": request.regime,
        "element": request.element,
        "ionization_ev": request.ionization_ev,
        "principal_n": request.principal_n,
        "electron_density_m3": request.electron_density_m3,
    }


def _attach_balance_metrics(
    result: dict[str, Any],
    *,
    ionization_ev: float | None,
    principal_n: float | None,
    electron_density_m3: float | None,
) -> dict[str, Any]:
    if ionization_ev is None or principal_n is None or electron_density_m3 is None:
        return result

    d1_value = d1_proxy(ionization_ev, principal_n)
    d4_pressure = fermi_pressure_pa(electron_density_m3)
    d4_balance = fermi_balance_ev(electron_density_m3)
    result.update(
        {
            "D1_proxy": d1_value,
            "D4_pressure_pa": d4_pressure,
            "D4_balance_ev": d4_balance,
            "D4_over_D1": d4_balance / d1_value,
            "dense_balance_gap_ev": abs(d1_value - d4_balance),
        }
    )
    return result


def run_regime(
    regime: str,
    *,
    element: str | None = None,
    ionization_ev: float | None = None,
    principal_n: float | None = None,
    electron_density_m3: float | None = None,
) -> dict[str, Any]:
    if regime not in REGIME_CHOICES:
        raise ValueError(f"Unsupported regime: {regime}")

    request = RegimeRequest(
        regime=regime,
        element=element,
        ionization_ev=ionization_ev,
        principal_n=principal_n,
        electron_density_m3=electron_density_m3,
    )

    result = {
        **_base_payload(request),
        "dominant_grid": None,
        "checks": [],
        "notes": [],
        "ok": True,
    }

    if regime == "atomique":
        result["dominant_grid"] = "D1"
        result["checks"] = ["D1 dominates", "D4 remains negligible", "no Fermi gas control"]
        result["notes"] = ["Use the atomic ladder as a baseline." if element else "Element is optional here."]
        _attach_balance_metrics(
            result,
            ionization_ev=ionization_ev,
            principal_n=principal_n,
            electron_density_m3=electron_density_m3,
        )
        result["ok"] = result.get("D4_over_D1", 1.0) < 1.0e-3 if "D4_over_D1" in result else True
        return result

    if regime == "metal":
        result["dominant_grid"] = "D1 + D2 + D4"
        result["checks"] = ["D4 is moderate", "Fermi scale remains finite", "transport remains relevant"]
        result["notes"] = ["Use the metallic branch when the density is still moderate."]
        _attach_balance_metrics(
            result,
            ionization_ev=ionization_ev,
            principal_n=principal_n,
            electron_density_m3=electron_density_m3,
        )
        result["ok"] = result.get("D1_proxy") is None or result.get("D4_balance_ev") is None or result["D1_proxy"] > result["D4_balance_ev"]
        return result

    if regime == "lanthanide":
        result["dominant_grid"] = "D1 + D3"
        result["checks"] = ["D3 is mandatory", "local reduction is not assumed", "topological blockage remains visible"]
        result["notes"] = ["This branch explicitly refuses a D1-only collapse."]
        _attach_balance_metrics(
            result,
            ionization_ev=ionization_ev,
            principal_n=principal_n,
            electron_density_m3=electron_density_m3,
        )
        return result

    density = electron_density_m3
    if density is None:
        result["ok"] = False
        result["notes"] = ["Dense regime requires electron_density_m3."]
        return result

    result["dominant_grid"] = "D1 + D4"
    result["checks"] = ["D1 and D4 are compared directly", "D1 ~= D4 is a local dense-regime balance", "density drives the crossover"]

    if ionization_ev is not None and principal_n is not None:
        _attach_balance_metrics(
            result,
            ionization_ev=ionization_ev,
            principal_n=principal_n,
            electron_density_m3=density,
        )
        result["ok"] = True
    else:
        result["ok"] = False
        result["notes"] = ["Provide ionization_ev and principal_n to evaluate the D1 proxy in dense mode."]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a regime-aware physics launcher.")
    parser.add_argument("regime", choices=REGIME_CHOICES, help="Selected regime to evaluate")
    parser.add_argument("--element", default=None, help="Element symbol or label for the regime")
    parser.add_argument("--ionization-ev", type=float, default=None, help="Ionization energy used for the D1 proxy")
    parser.add_argument("--principal-n", type=float, default=None, help="Principal quantum number used for the D1 proxy")
    parser.add_argument("--electron-density-m3", type=float, default=None, help="Electron density for the D4 branch")
    args = parser.parse_args()

    result = run_regime(
        args.regime,
        element=args.element,
        ionization_ev=args.ionization_ev,
        principal_n=args.principal_n,
        electron_density_m3=args.electron_density_m3,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()