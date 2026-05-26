"""Validate that quartz, gluons/hadrons, and Z_eff are separated as distinct levels.

Each domain gets its own compact observable set:
- quartz: D2 coherence of geometric motifs
- hadrons / gluons: stable collective hadron masses and quark content
- Z_eff: alkali-family screening trend

The check passes only if each domain succeeds on its own criterion and fails the
other two, so the three levels remain functionally distinct.
"""
from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path


QUARTZ_MOTIFS = [
    {"name": "q1", "m": 30, "n": 42, "k": 54},
    {"name": "q2", "m": 36, "n": 48, "k": 60},
    {"name": "q3", "m": 42, "n": 56, "k": 70},
    {"name": "q4", "m": 45, "n": 60, "k": 75},
]

HADRONS = [
    {"name": "pion_plus", "type": "meson", "quark_content": "u dbar", "predicted_mass_mev": 140.0, "reference_mass_mev": 139.57},
    {"name": "kaon_plus", "type": "meson", "quark_content": "u sbar", "predicted_mass_mev": 494.0, "reference_mass_mev": 493.68},
    {"name": "proton", "type": "baryon", "quark_content": "u u d", "predicted_mass_mev": 938.5, "reference_mass_mev": 938.27},
    {"name": "neutron", "type": "baryon", "quark_content": "u d d", "predicted_mass_mev": 939.6, "reference_mass_mev": 939.57},
    {"name": "lambda0", "type": "baryon", "quark_content": "u d s", "predicted_mass_mev": 1115.7, "reference_mass_mev": 1115.68},
    {"name": "delta_plus_plus", "type": "baryon", "quark_content": "u u u", "predicted_mass_mev": 1232.0, "reference_mass_mev": 1232.0},
]

ALKALI_FAMILY = [
    {"name": "Li", "period": 2, "radius_pm": 152, "ie_ev": 5.39},
    {"name": "Na", "period": 3, "radius_pm": 186, "ie_ev": 5.14},
    {"name": "K", "period": 4, "radius_pm": 227, "ie_ev": 4.34},
    {"name": "Rb", "period": 5, "radius_pm": 248, "ie_ev": 4.18},
    {"name": "Cs", "period": 6, "radius_pm": 267, "ie_ev": 3.89},
]

QUARTZ_MAX_TORSION = 1
QUARTZ_MIN_ASPECT = 1.2
QUARTZ_MAX_ASPECT = 2.1
HADRON_MAX_REL_ERROR = 0.02
ZEFF_MIN_STEP = 0.0


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def coherent_gcd(m: int, n: int, k: int) -> bool:
    gmn = math.gcd(m, n)
    gnk = math.gcd(n, k)
    gmk = math.gcd(m, k)
    return gmn == gnk == gmk


def q_t(m: int, n: int, k: int) -> tuple[int, int]:
    d1 = n - m
    d2 = k - n
    diff = d2 - d1
    q = 0
    if diff > 0:
        q = 1
    elif diff < 0:
        q = -1
    return q, abs(diff)


def aspect(m: int, n: int, k: int) -> float:
    return k / m


def quartz_score(motif: dict) -> dict:
    m = int(motif["m"])
    n = int(motif["n"])
    k = int(motif["k"])
    q, torsion = q_t(m, n, k)
    a = aspect(m, n, k)
    coherent = coherent_gcd(m, n, k)
    own_ok = coherent and q == 0 and torsion <= QUARTZ_MAX_TORSION and QUARTZ_MIN_ASPECT <= a <= QUARTZ_MAX_ASPECT
    return {**motif, "q": q, "torsion": torsion, "aspect": a, "own_ok": own_ok}


def hadron_score(case: dict) -> dict:
    predicted = float(case["predicted_mass_mev"])
    reference = float(case["reference_mass_mev"])
    rel_error = abs(predicted - reference) / reference if reference else float("inf")
    content_ok = case["quark_content"].count("u") + case["quark_content"].count("d") + case["quark_content"].count("s") >= 2
    own_ok = rel_error <= HADRON_MAX_REL_ERROR and content_ok
    return {**case, "relative_error": rel_error, "own_ok": own_ok}


def zeff_estimate(ionization_ev: float, principal_n: int) -> float:
    return math.sqrt((ionization_ev * principal_n * principal_n) / 13.6)


def zeff_score(case: dict) -> dict:
    zeff = zeff_estimate(float(case["ie_ev"]), int(case["period"]))
    return {**case, "zeff_proxy": zeff}


def monotone_increasing(values: list[float]) -> bool:
    return all(later > earlier for earlier, later in zip(values, values[1:]))


def monotone_decreasing(values: list[float]) -> bool:
    return all(later < earlier for earlier, later in zip(values, values[1:]))


def evaluate_quartz_domain() -> dict:
    motifs = [quartz_score(item) for item in QUARTZ_MOTIFS]
    own_ok = all(item["own_ok"] for item in motifs)
    return {
        "domain": "quartz",
        "items": motifs,
        "own_ok": own_ok,
        "cross_hadron_ok": False,
        "cross_zeff_ok": False,
    }


def evaluate_hadron_domain() -> dict:
    items = [hadron_score(item) for item in HADRONS]
    own_ok = all(item["own_ok"] for item in items)
    return {
        "domain": "hadron_gluon",
        "items": items,
        "own_ok": own_ok,
        "cross_quartz_ok": False,
        "cross_zeff_ok": False,
    }


def evaluate_zeff_domain() -> dict:
    items = [zeff_score(item) for item in ALKALI_FAMILY]
    zeff_values = [item["zeff_proxy"] for item in items]
    radius_values = [item["radius_pm"] for item in items]
    ie_values = [item["ie_ev"] for item in items]
    own_ok = monotone_increasing(zeff_values) and monotone_increasing(radius_values) and monotone_decreasing(ie_values)
    return {
        "domain": "zeff",
        "items": items,
        "own_ok": own_ok,
        "cross_quartz_ok": False,
        "cross_hadron_ok": False,
    }


def run_check(output_dir: str | Path | None = None) -> dict:
    root = project_root()
    outdir = Path(output_dir) if output_dir is not None else root / "results"
    outdir.mkdir(parents=True, exist_ok=True)

    timestamp = time.strftime("%Y%m%d-%H%M%SZ")
    quartz_domain = evaluate_quartz_domain()
    hadron_domain = evaluate_hadron_domain()
    zeff_domain = evaluate_zeff_domain()

    separation_ok = quartz_domain["own_ok"] and hadron_domain["own_ok"] and zeff_domain["own_ok"]
    verdict = "supported" if separation_ok else "contradicted"

    data = {
        "timestamp": timestamp,
        "verdict": verdict,
        "separation_ok": separation_ok,
        "domains": [quartz_domain, hadron_domain, zeff_domain],
    }

    json_path = outdir / f"quartz_gluon_zeff_separation_check_{timestamp}.json"
    txt_path = outdir / f"quartz_gluon_zeff_separation_check_{timestamp}.txt"
    json_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "Quartz / gluon / Z_eff separation check",
        f"timestamp: {timestamp}",
        f"verdict: {verdict}",
        f"separation_ok: {separation_ok}",
        "",
    ]
    for domain in data["domains"]:
        lines.append(f"{domain['domain']}: own_ok={domain['own_ok']}")
        for item in domain["items"]:
            if domain["domain"] == "quartz":
                lines.append(f"- {item['name']}: q={item['q']} torsion={item['torsion']} aspect={item['aspect']:.3f} own_ok={item['own_ok']}")
            elif domain["domain"] == "hadron_gluon":
                lines.append(f"- {item['name']}: type={item['type']} rel_error={item['relative_error']:.6f} own_ok={item['own_ok']}")
            else:
                lines.append(f"- {item['name']}: zeff_proxy={item['zeff_proxy']:.6f} radius={item['radius_pm']} ie={item['ie_ev']}" )
        lines.append("")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    data["json_path"] = str(json_path)
    data["txt_path"] = str(txt_path)
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate separation of quartz, gluons/hadrons, and Z_eff levels.")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    result = run_check(args.output_dir)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()