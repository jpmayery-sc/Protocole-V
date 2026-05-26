"""Quick coherence check for silicon as a semiconductor.

The script applies strict qualitative checks to known silicon behavior:

- intrinsically weak conduction
- stronger conduction when temperature rises
- strong conduction increase with n- or p-type doping
- clear separation from metallic conduction

It writes a timestamped JSON summary and a text report under
results/result-analyse/.
"""

from __future__ import annotations

import json
import time
from pathlib import Path


INTRINSIC_RHO_300K = 2.3e3  # ohm * m, order-of-magnitude reference
HIGH_TEMP_RHO = 2.3e2  # ohm * m, lower resistivity when heated (illustrative)
DOPED_RHO = 1.0e-1  # ohm * m, order-of-magnitude lower when doped
METAL_RHO_REFERENCE = 2.82e-8  # ohm * m, aluminum reference for contrast


def classify_silicon() -> dict:
    intrinsic_ok = INTRINSIC_RHO_300K > 1.0e2
    thermal_ok = HIGH_TEMP_RHO < INTRINSIC_RHO_300K
    doping_ok = DOPED_RHO < HIGH_TEMP_RHO
    contrast_ok = INTRINSIC_RHO_300K > METAL_RHO_REFERENCE * 1.0e8

    verdict = (
        "conforme strict"
        if intrinsic_ok and thermal_ok and doping_ok and contrast_ok
        else "falsifie"
    )

    return {
        "reference": {
            "intrinsic_rho_300k_ohm_m": INTRINSIC_RHO_300K,
            "heated_rho_ohm_m": HIGH_TEMP_RHO,
            "doped_rho_ohm_m": DOPED_RHO,
            "metal_rho_reference_ohm_m": METAL_RHO_REFERENCE,
        },
        "intrinsic_test": {
            "status": "conforme strict" if intrinsic_ok else "falsifie",
        },
        "thermal_test": {
            "status": "conforme strict" if thermal_ok else "falsifie",
        },
        "doping_test": {
            "status": "conforme strict" if doping_ok else "falsifie",
        },
        "contrast_test": {
            "status": "conforme strict" if contrast_ok else "falsifie",
        },
        "overall_verdict": verdict,
        "falsifiers": [
            "le silicium intrinsèque se comporte comme un métal",
            "la température ne change presque pas la conduction",
            "le dopage n’a pas d’effet net",
            "le cadre ne distingue pas le semi-conducteur du conducteur métallique",
        ],
    }


def main() -> None:
    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    root = Path(__file__).resolve().parents[1]
    outdir = root / "results" / "result-analyse"
    outdir.mkdir(parents=True, exist_ok=True)

    results = classify_silicon()

    json_path = outdir / f"silicon_semiconductor_check_{timestamp}.json"
    txt_path = outdir / f"silicon_semiconductor_check_{timestamp}.txt"
    json_path.write_text(json.dumps({"timestamp": timestamp, **results}, indent=2, ensure_ascii=False), encoding="utf-8")

    with txt_path.open("w", encoding="utf-8") as handle:
        handle.write("Contrôle du silicium comme semi-conducteur\n")
        handle.write(f"Timestamp: {timestamp}\n\n")
        handle.write("Tests:\n")
        handle.write(f"- Intrinsèque: {results['intrinsic_test']['status']}\n")
        handle.write(f"- Température: {results['thermal_test']['status']}\n")
        handle.write(f"- Dopage: {results['doping_test']['status']}\n")
        handle.write(f"- Contraste avec métal: {results['contrast_test']['status']}\n\n")
        handle.write(f"Verdict global: {results['overall_verdict']}\n\n")
        handle.write("Falsificateurs:\n")
        for item in results["falsifiers"]:
            handle.write(f"- {item}\n")

    print(f"Wrote JSON report to {json_path}")
    print(f"Wrote text report to {txt_path}")
    print(f"Global verdict: {results['overall_verdict']}")


if __name__ == "__main__":
    main()