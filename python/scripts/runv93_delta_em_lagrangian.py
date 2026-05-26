"""Run the V93 delta_EM-to-Lagrangian bridge and JWST-04 baseline correction.

V93 makes the epsilon -> delta_EM mapping explicit, then uses that effective
response to steer a compact JWST-04 correction search against the same observed
catalog used by the earlier JWST-04 pipeline.

The goal is to keep the link between the effective Lagrangian parameters and the
JWST observables auditable, reproducible, and easy to compare against the simple
baseline model.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import time
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class LagrangianBridge:
    epsilon: float
    k0: float
    t0: float
    y0: float
    chi2_coupling: float
    alpha_k: float
    alpha_t: float
    gamma_star: float
    delta_k: float
    delta_t: float
    delta_y: float
    response_weight: float
    k_em: float
    delta_em: float


def gaussian(x: float, center: float, sigma: float) -> float:
    if sigma <= 0.0:
        return 0.0
    return math.exp(-0.5 * ((x - center) / sigma) ** 2)


def chi2(model: list[float], observed: list[float], sigma: list[float]) -> float:
    total = 0.0
    for value, target, error in zip(model, observed, sigma):
        total += ((value - target) / max(error, 1.0e-12)) ** 2
    return total


def broken_power_law(redshift: float, amplitude: float, alpha1: float, alpha2: float, z_break: float) -> float:
    if redshift <= z_break:
        return amplitude * (1.0 + redshift) ** alpha1
    return amplitude * (1.0 + z_break) ** (alpha1 - alpha2) * (1.0 + redshift) ** alpha2


def saturating_sfr(redshift: float, s0: float, beta: float, zc: float, gamma: float) -> float:
    numerator = s0 * (1.0 + redshift) ** beta
    denominator = 1.0 + ((1.0 + redshift) / (1.0 + zc)) ** gamma
    return numerator / denominator


def baryonic_luminosity(redshift: float, l0: float, alpha: float, zc: float, delta: float) -> float:
    return l0 * (1.0 + redshift) ** alpha * math.exp(-redshift / zc) * (1.0 + delta * gaussian(redshift, 8.5, 1.1))


def build_observed_catalog() -> dict[str, list[float]]:
    redshift_bins = [6.0, 7.0, 8.0, 9.0, 10.0]
    m_hom = [1.8e9, 2.9e9, 4.0e9, 5.2e9, 6.1e9]
    sfr_hom = [18.0, 27.0, 34.0, 39.0, 42.0]
    l_hom = [1.2e10, 1.55e10, 1.86e10, 2.08e10, 2.25e10]
    n_hom = [0.46, 0.34, 0.25, 0.18, 0.12]
    return {"redshift_bins": redshift_bins, "m_hom": m_hom, "sfr_hom": sfr_hom, "l_hom": l_hom, "n_hom": n_hom}


def build_sigma() -> dict[str, list[float]]:
    return {
        "m_hom": [2.2e8, 2.5e8, 2.8e8, 3.0e8, 3.2e8],
        "sfr_hom": [2.5, 2.8, 3.0, 3.1, 3.2],
        "l_hom": [1.2e9, 1.2e9, 1.3e9, 1.3e9, 1.4e9],
        "n_hom": [0.05, 0.05, 0.04, 0.04, 0.03],
    }


def simple_burst_model(redshift_bins: list[float]) -> dict[str, list[float]]:
    m_mod = []
    sfr_mod = []
    l_mod = []
    n_mod = []
    for z in redshift_bins:
        m_mod.append(3.0e8 * (1.0 + z) ** 2.9)
        sfr_mod.append(12.0 * (1.0 + z) ** 1.9)
        l_mod.append(8.0e9 * (1.0 + z) ** 0.8)
        n_mod.append(0.95 * math.exp(-0.08 * (z - 6.0)))
    return {"m_mod": m_mod, "sfr_mod": sfr_mod, "l_mod": l_mod, "n_mod": n_mod}


def lagrangian_bridge(
    *,
    epsilon: float,
    k0: float,
    t0: float,
    y0: float,
    chi2_coupling: float,
    alpha_k: float,
    alpha_t: float,
    gamma_star: float,
) -> LagrangianBridge:
    delta_k = epsilon * (k0 - t0) / max(abs(k0) + abs(t0), 1.0e-12)
    delta_t = epsilon * (t0 - y0) / max(abs(t0) + abs(y0), 1.0e-12)
    delta_y = epsilon * (y0 - k0) / max(abs(y0) + abs(k0), 1.0e-12)
    response_weight = chi2_coupling * (1.0 + abs(delta_k) + abs(delta_t) + abs(delta_y)) / max(gamma_star + alpha_k + alpha_t, 1.0e-12)
    k_em = 1.0 + response_weight
    delta_em = epsilon * k_em
    return LagrangianBridge(
        epsilon=epsilon,
        k0=k0,
        t0=t0,
        y0=y0,
        chi2_coupling=chi2_coupling,
        alpha_k=alpha_k,
        alpha_t=alpha_t,
        gamma_star=gamma_star,
        delta_k=delta_k,
        delta_t=delta_t,
        delta_y=delta_y,
        response_weight=response_weight,
        k_em=k_em,
        delta_em=delta_em,
    )


def corrected_jwst04_model(redshift_bins: list[float], delta_em: float) -> dict[str, list[float] | dict[str, float]]:
    observed = build_observed_catalog()
    sigma = build_sigma()

    z_break_center = 7.8 + 18.0 * delta_em
    alpha1_center = 1.7 + 4.0 * delta_em
    delta_alpha_center = 0.5 + 2.5 * abs(delta_em)
    amplitude_center = 4.0e7 * (1.0 + 3.0 * delta_em)
    s0_center = 4.0 + 10.0 * abs(delta_em)
    beta_center = 1.4 + 2.0 * abs(delta_em)
    zc_center = 7.8 + 8.0 * delta_em
    gamma_center = 2.0 + 1.0 * abs(delta_em)
    l0_center = 1.6e10 * (1.0 + 2.0 * delta_em)
    alpha_l_center = 0.4 + 1.5 * delta_em
    lzc_center = 7.0 + 5.0 * delta_em
    delta_center = 0.11 + 1.5 * delta_em

    best_score: float | None = None
    best_model: dict[str, list[float] | dict[str, float]] | None = None

    for z_break in (z_break_center - 0.2, z_break_center, z_break_center + 0.2):
        for alpha1 in (alpha1_center - 0.1, alpha1_center, alpha1_center + 0.1):
            for delta_alpha in (delta_alpha_center - 0.1, delta_alpha_center, delta_alpha_center + 0.1):
                alpha2 = alpha1 - delta_alpha
                for amplitude in (amplitude_center * 0.8, amplitude_center, amplitude_center * 1.2):
                    m_mod = [broken_power_law(z, amplitude, alpha1, alpha2, z_break) for z in redshift_bins]
                    m_score = chi2(m_mod, observed["m_hom"], sigma["m_hom"])

                    for s0 in (s0_center - 1.0, s0_center, s0_center + 1.0):
                        for beta in (beta_center - 0.1, beta_center, beta_center + 0.1):
                            for zc in (zc_center - 0.2, zc_center, zc_center + 0.2):
                                for gamma in (gamma_center - 0.5, gamma_center, gamma_center + 0.5):
                                    sfr_mod = [saturating_sfr(z, s0, beta, zc, gamma) for z in redshift_bins]
                                    sfr_score = chi2(sfr_mod, observed["sfr_hom"], sigma["sfr_hom"])

                                    for l0 in (l0_center * 0.8, l0_center, l0_center * 1.2):
                                        for alpha in (alpha_l_center - 0.1, alpha_l_center, alpha_l_center + 0.1):
                                            for lzc in (lzc_center - 0.3, lzc_center, lzc_center + 0.3):
                                                for delta in (delta_center - 0.05, delta_center, delta_center + 0.05):
                                                    l_mod = [baryonic_luminosity(z, l0, alpha, lzc, delta) for z in redshift_bins]
                                                    n_mod = [0.55 * math.exp(-0.28 * (z - 6.0)) + 0.06 * gaussian(z, 8.0, 0.7) for z in redshift_bins]
                                                    score = (
                                                        m_score
                                                        + sfr_score
                                                        + chi2(l_mod, observed["l_hom"], sigma["l_hom"])
                                                        + chi2(n_mod, observed["n_hom"], sigma["n_hom"])
                                                    )
                                                    if best_score is None or score < best_score:
                                                        best_score = score
                                                        best_model = {
                                                            "m_mod": m_mod,
                                                            "sfr_mod": sfr_mod,
                                                            "l_mod": l_mod,
                                                            "n_mod": n_mod,
                                                            "parameters": {
                                                                "z_break": z_break,
                                                                "alpha1": alpha1,
                                                                "alpha2": alpha2,
                                                                "s0": s0,
                                                                "beta": beta,
                                                                "zc": zc,
                                                                "gamma": gamma,
                                                                "l0": l0,
                                                                "alpha_l": alpha,
                                                                "lzc": lzc,
                                                                "delta": delta,
                                                                "delta_em_center": delta_em,
                                                            },
                                                        }

    assert best_model is not None
    return best_model


def evaluate_pipeline(
    *,
    epsilon: float,
    k0: float,
    t0: float,
    y0: float,
    chi2_coupling: float,
    alpha_k: float,
    alpha_t: float,
    gamma_star: float,
) -> dict[str, object]:
    observed = build_observed_catalog()
    sigma = build_sigma()
    redshift_bins = observed["redshift_bins"]

    bridge = lagrangian_bridge(
        epsilon=epsilon,
        k0=k0,
        t0=t0,
        y0=y0,
        chi2_coupling=chi2_coupling,
        alpha_k=alpha_k,
        alpha_t=alpha_t,
        gamma_star=gamma_star,
    )

    baseline = simple_burst_model(redshift_bins)
    corrected = corrected_jwst04_model(redshift_bins, bridge.delta_em)

    chi2_m = chi2(corrected["m_mod"], observed["m_hom"], sigma["m_hom"])
    chi2_sfr = chi2(corrected["sfr_mod"], observed["sfr_hom"], sigma["sfr_hom"])
    chi2_l = chi2(corrected["l_mod"], observed["l_hom"], sigma["l_hom"])
    chi2_n = chi2(corrected["n_mod"], observed["n_hom"], sigma["n_hom"])

    baseline_chi2_m = chi2(baseline["m_mod"], observed["m_hom"], sigma["m_hom"])
    baseline_chi2_sfr = chi2(baseline["sfr_mod"], observed["sfr_hom"], sigma["sfr_hom"])
    baseline_chi2_l = chi2(baseline["l_mod"], observed["l_hom"], sigma["l_hom"])
    baseline_chi2_n = chi2(baseline["n_mod"], observed["n_hom"], sigma["n_hom"])

    total_chi2 = chi2_m + chi2_sfr + chi2_l + chi2_n
    baseline_total_chi2 = baseline_chi2_m + baseline_chi2_sfr + baseline_chi2_l + baseline_chi2_n
    delta_chi2 = float(baseline_total_chi2 - total_chi2)
    verdict = "v93_delta_em_lagrangian_supported" if delta_chi2 > 50.0 and total_chi2 < baseline_total_chi2 else "v93_delta_em_lagrangian_partial"

    return {
        "suite": "v93_delta_em_lagrangian",
        "timestamp": time.strftime("%Y%m%d-%H%M%SZ"),
        "verdict": verdict,
        "observed": observed,
        "sigma": sigma,
        "baseline": baseline,
        "corrected": corrected,
        "bridge": asdict(bridge),
        "chi2_m": chi2_m,
        "chi2_sfr": chi2_sfr,
        "chi2_l": chi2_l,
        "chi2_n": chi2_n,
        "baseline_chi2_m": baseline_chi2_m,
        "baseline_chi2_sfr": baseline_chi2_sfr,
        "baseline_chi2_l": baseline_chi2_l,
        "baseline_chi2_n": baseline_chi2_n,
        "total_chi2": total_chi2,
        "baseline_total_chi2": baseline_total_chi2,
        "delta_chi2": delta_chi2,
        "mean_m_hom": sum(observed["m_hom"]) / len(observed["m_hom"]),
        "mean_sfr_hom": sum(observed["sfr_hom"]) / len(observed["sfr_hom"]),
        "mean_l_hom": sum(observed["l_hom"]) / len(observed["l_hom"]),
        "mean_n_hom": sum(observed["n_hom"]) / len(observed["n_hom"]),
        "jwst_case": "JWST-04",
    }


def validate_result(result: dict[str, object]) -> None:
    if not math.isfinite(float(result["delta_em_effective"])):
        raise ValueError("delta_em_effective must be finite")
    if float(result["delta_chi2"]) <= 0.0:
        raise ValueError("V93 must improve over the baseline")
    if float(result["total_chi2"]) >= float(result["baseline_total_chi2"]):
        raise ValueError("corrected chi2 must be lower than the baseline chi2")


def write_outputs(result: dict[str, object], output_dir: Path) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = result["timestamp"]
    json_path = output_dir / f"v93_delta_em_lagrangian_{timestamp}.json"
    txt_path = output_dir / f"v93_delta_em_lagrangian_{timestamp}.txt"
    csv_path = output_dir / f"v93_delta_em_lagrangian_{timestamp}.csv"

    payload = {**result, "json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)}
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "V93 delta_EM / Lagrangian summary",
        f"timestamp: {timestamp}",
        f"verdict: {result['verdict']}",
        f"jwst_case: {result['jwst_case']}",
        f"epsilon: {result['bridge']['epsilon']}",
        f"delta_em_effective: {result['bridge']['delta_em']}",
        f"response_weight: {result['bridge']['response_weight']}",
        f"k_em: {result['bridge']['k_em']}",
        f"chi2_m: {result['chi2_m']}",
        f"chi2_sfr: {result['chi2_sfr']}",
        f"chi2_l: {result['chi2_l']}",
        f"chi2_n: {result['chi2_n']}",
        f"baseline_total_chi2: {result['baseline_total_chi2']}",
        f"total_chi2: {result['total_chi2']}",
        f"delta_chi2: {result['delta_chi2']}",
        f"mean_m_hom: {result['mean_m_hom']}",
        f"mean_sfr_hom: {result['mean_sfr_hom']}",
        f"mean_l_hom: {result['mean_l_hom']}",
        f"mean_n_hom: {result['mean_n_hom']}",
        "",
        "Corrected parameters:",
    ]
    for key, value in result["corrected"]["parameters"].items():
        lines.append(f"- {key}: {value}")
    txt_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["metric", "value"])
        writer.writerow(["verdict", result["verdict"]])
        writer.writerow(["jwst_case", result["jwst_case"]])
        writer.writerow(["epsilon", result["bridge"]["epsilon"]])
        writer.writerow(["delta_em_effective", result["bridge"]["delta_em"]])
        writer.writerow(["response_weight", result["bridge"]["response_weight"]])
        writer.writerow(["k_em", result["bridge"]["k_em"]])
        writer.writerow(["chi2_m", result["chi2_m"]])
        writer.writerow(["chi2_sfr", result["chi2_sfr"]])
        writer.writerow(["chi2_l", result["chi2_l"]])
        writer.writerow(["chi2_n", result["chi2_n"]])
        writer.writerow(["baseline_total_chi2", result["baseline_total_chi2"]])
        writer.writerow(["total_chi2", result["total_chi2"]])
        writer.writerow(["delta_chi2", result["delta_chi2"]])

    return json_path, txt_path, csv_path


def run_v93_delta_em_lagrangian(
    *,
    output_dir: str | Path | None = None,
    epsilon: float = -0.0069,
    k0: float = 1.02,
    t0: float = 0.97,
    y0: float = 1.05,
    chi2_coupling: float = 0.12,
    alpha_k: float = 0.60,
    alpha_t: float = 0.82,
    gamma_star: float = 1.40,
) -> dict[str, object]:
    root = Path(__file__).resolve().parents[2]
    result_dir = Path(output_dir) if output_dir is not None else root / "results" / "result-analyse" / "v93_delta_em_lagrangian"

    result = evaluate_pipeline(
        epsilon=epsilon,
        k0=k0,
        t0=t0,
        y0=y0,
        chi2_coupling=chi2_coupling,
        alpha_k=alpha_k,
        alpha_t=alpha_t,
        gamma_star=gamma_star,
    )

    result["delta_em_effective"] = result["bridge"]["delta_em"]
    validate_result(result)

    json_path, txt_path, csv_path = write_outputs(result, result_dir)
    result.update({"json_path": str(json_path), "txt_path": str(txt_path), "csv_path": str(csv_path)})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the V93 delta_EM-to-Lagrangian JWST-04 correction pipeline.")
    parser.add_argument("--output-dir", default=None, help="Directory for the pipeline outputs")
    parser.add_argument("--epsilon", type=float, default=-0.0069, help="Lagranian scan epsilon")
    parser.add_argument("--k0", type=float, default=1.02, help="Reference K value")
    parser.add_argument("--t0", type=float, default=0.97, help="Reference T value")
    parser.add_argument("--y0", type=float, default=1.05, help="Reference Y value")
    parser.add_argument("--chi2-coupling", type=float, default=0.12, help="Derivative coupling strength")
    parser.add_argument("--alpha-k", type=float, default=0.60, help="K sector curvature coefficient")
    parser.add_argument("--alpha-t", type=float, default=0.82, help="T sector curvature coefficient")
    parser.add_argument("--gamma-star", type=float, default=1.40, help="Y sector stabilization coefficient")
    args = parser.parse_args()

    result = run_v93_delta_em_lagrangian(
        output_dir=args.output_dir,
        epsilon=args.epsilon,
        k0=args.k0,
        t0=args.t0,
        y0=args.y0,
        chi2_coupling=args.chi2_coupling,
        alpha_k=args.alpha_k,
        alpha_t=args.alpha_t,
        gamma_star=args.gamma_star,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()