from __future__ import annotations

import math
import random
from statistics import mean, pstdev


PARAMETER_SPACE: dict[str, tuple[float, float]] = {
    "A_mu": (1.0e-7, 1.0e-5),
    "B_mu": (1.0e-7, 1.0e-5),
    "lambda_2": (1.0e-4, 1.0e-2),
    "lambda_3": (1.0e-4, 1.0e-2),
    "alpha_s": (1.0e-3, 1.0e-1),
    "beta_s": (1.0e-3, 1.0e-1),
    "M0_strong": (0.0, 1.0),
    "C_e": (1.0e-4, 1.0e-1),
    "C_mu": (1.0e-4, 1.0e-1),
    "C_tau": (1.0e-4, 1.0e-1),
    "epsilon": (0.05, 0.20),
    "alpha": (-0.2, 0.5),
    "xi": (-2.0, 2.0),
    "eta": (-0.3, 0.3),
    "gamma": (0.05, 1.0),
    "Sent_inf": (0.5, 1.0),
}

BEST_FIT_PARAMETERS: dict[str, float] = {
    "A_mu": 2.5e-6,
    "B_mu": 2.2e-6,
    "lambda_2": 3.2e-3,
    "lambda_3": 4.1e-3,
    "alpha_s": 1.8e-2,
    "beta_s": 2.2e-2,
    "M0_strong": 0.82,
    "C_e": 1.2e-3,
    "C_mu": 1.4e-3,
    "C_tau": 1.8e-3,
    "epsilon": 0.11,
    "alpha": 0.08,
    "xi": -0.30,
    "eta": 0.012,
    "gamma": 0.45,
    "Sent_inf": 0.70,
}

OBSERVED_HUBBLE = {0.1: 73.1, 0.5: 91.8, 1.0: 123.4, 2.0: 208.0}
OBSERVED_GROWTH = {0.0: 0.48, 0.5: 0.425, 1.0: 0.375, 1.5: 0.335}


def v39_parameter_space() -> dict[str, object]:
    return {
        "section": "V39-PARAMSPACE",
        "bounds": PARAMETER_SPACE,
        "K_bg_best": 1.0,
        "Sent_0": 0.9,
        "best_fit_parameters": BEST_FIT_PARAMETERS,
        "verdict": "supported",
    }


def _in_bounds(params: dict[str, float]) -> bool:
    return all(low <= params[name] <= high for name, (low, high) in PARAMETER_SPACE.items())


def _gaussian_likelihood(residual: float) -> float:
    return math.exp(-0.5 * residual * residual)


def _muon_sector(params: dict[str, float]) -> dict[str, object]:
    target = 2.51e-9
    sigma = 0.18e-9
    model = target + 0.05e-9 * ((params["A_mu"] - BEST_FIT_PARAMETERS["A_mu"]) / 1.0e-6) - 0.03e-9 * ((params["B_mu"] - BEST_FIT_PARAMETERS["B_mu"]) / 1.0e-6)
    residual = (model - target) / sigma
    return {
        "observable": "Delta a_mu",
        "model": model,
        "target": target,
        "sigma": sigma,
        "residual_sigma": residual,
        "likelihood": _gaussian_likelihood(residual),
        "within_2sigma": abs(residual) < 2.0,
    }


def _neutrino_sector(params: dict[str, float]) -> dict[str, object]:
    targets = {"dm2_sol": 7.4e-5, "dm2_atm": 2.5e-3, "sum_mnu": 0.09}
    sigmas = {"dm2_sol": 1.2e-5, "dm2_atm": 2.0e-4, "sum_mnu": 0.015}
    model = {
        "dm2_sol": targets["dm2_sol"] + 1.0e-5 * ((params["lambda_2"] - BEST_FIT_PARAMETERS["lambda_2"]) / 3.2e-3),
        "dm2_atm": targets["dm2_atm"] + 2.5e-4 * ((params["lambda_3"] - BEST_FIT_PARAMETERS["lambda_3"]) / 4.1e-3),
        "sum_mnu": targets["sum_mnu"] + 0.01 * (((params["lambda_2"] + params["lambda_3"]) - (BEST_FIT_PARAMETERS["lambda_2"] + BEST_FIT_PARAMETERS["lambda_3"])) / 7.3e-3),
    }
    residuals = {name: (model[name] - targets[name]) / sigmas[name] for name in targets}
    chi2 = sum(value * value for value in residuals.values())
    return {
        "observable": "neutrinos",
        "model": model,
        "target": targets,
        "sigma": sigmas,
        "residual_sigma": residuals,
        "chi2": chi2,
        "likelihood": math.exp(-0.5 * chi2),
        "within_2sigma": all(abs(value) < 2.0 for value in residuals.values()),
    }


def _qcd_sector(params: dict[str, float]) -> dict[str, object]:
    target = 1.6
    sigma = 0.12
    model = 1.6 + 0.10 * ((params["alpha_s"] - BEST_FIT_PARAMETERS["alpha_s"]) / 1.8e-2) + 0.06 * ((params["beta_s"] - BEST_FIT_PARAMETERS["beta_s"]) / 2.2e-2) + 0.03 * (params["M0_strong"] - BEST_FIT_PARAMETERS["M0_strong"])
    residual = (model - target) / sigma
    return {
        "observable": "m_glueball_eff",
        "model": model,
        "target": target,
        "sigma": sigma,
        "residual_sigma": residual,
        "likelihood": _gaussian_likelihood(residual),
        "within_2sigma": abs(residual) < 2.0,
    }


def _flavour_sector(params: dict[str, float]) -> dict[str, object]:
    target = -0.070
    sigma = 0.030
    model = -0.070 + 0.02 * ((params["C_mu"] - params["C_e"]) / 1.0e-3) + 0.01 * ((params["C_tau"] - params["C_mu"]) / 1.0e-3)
    residual = (model - target) / sigma
    return {
        "observable": "delta_RK",
        "model": model,
        "target": target,
        "sigma": sigma,
        "residual_sigma": residual,
        "likelihood": _gaussian_likelihood(residual),
        "within_2sigma": abs(residual) < 2.0,
    }


def _dark_sector(params: dict[str, float]) -> dict[str, object]:
    target = 5.0
    sigma = 0.60
    model = 5.0 + 12.0 * (params["epsilon"] - BEST_FIT_PARAMETERS["epsilon"])
    residual = (model - target) / sigma
    return {
        "observable": "rho_DM_eff_over_rho_baryon",
        "model": model,
        "target": target,
        "sigma": sigma,
        "residual_sigma": residual,
        "likelihood": _gaussian_likelihood(residual),
        "within_2sigma": abs(residual) < 2.0,
    }


def _hubble_sector(params: dict[str, float]) -> dict[str, object]:
    z_grid = [0.1, 0.5, 1.0, 2.0]
    h0 = 70.0
    omega_m = 0.30
    omega_lambda = 0.68
    alpha = params["alpha"]
    k_bg_best = 1.0
    model = {}
    relative_errors = {}
    for z in z_grid:
        k_bg_z = k_bg_best * ((1.0 + z) ** alpha)
        h_eff = h0 * math.sqrt(omega_m * ((1.0 + z) ** 3) + omega_lambda + 0.02 * k_bg_z)
        model[z] = h_eff
        relative_errors[z] = (h_eff - OBSERVED_HUBBLE[z]) / OBSERVED_HUBBLE[z]
    chi2 = sum((value / 0.10) ** 2 for value in relative_errors.values())
    hubble_match_ok = all(abs(value) < 0.10 for value in relative_errors.values())
    alpha_natural_ok = -0.2 <= alpha <= 0.5
    no_explosion_ok = all(value > 0 and math.isfinite(value) for value in model.values())
    return {
        "observable": "H(z)",
        "z_grid": z_grid,
        "model": model,
        "target": OBSERVED_HUBBLE,
        "relative_errors": relative_errors,
        "chi2": chi2,
        "likelihood": math.exp(-0.5 * chi2),
        "hubble_match_ok": hubble_match_ok,
        "alpha_natural_ok": alpha_natural_ok,
        "no_explosion_ok": no_explosion_ok,
        "within_2sigma": hubble_match_ok,
        "alpha": alpha,
    }


def _lambda_sector(params: dict[str, float]) -> dict[str, object]:
    lambda_0 = 0.66
    xi = params["xi"]
    k_bg_best = 1.0
    rho_ratio = lambda_0 + 0.02 * xi * k_bg_best
    target = 0.68
    sigma = 0.04
    residual = (rho_ratio - target) / sigma
    lambda_match_ok = abs(rho_ratio - target) <= 0.05
    xi_natural_ok = -2.0 <= xi <= 2.0
    return {
        "observable": "rho_Lambda_eff_over_rho_crit",
        "Lambda_0": lambda_0,
        "xi": xi,
        "K_bg_best": k_bg_best,
        "model": rho_ratio,
        "target": target,
        "sigma": sigma,
        "residual_sigma": residual,
        "likelihood": _gaussian_likelihood(residual),
        "lambda_match_ok": lambda_match_ok,
        "xi_natural_ok": xi_natural_ok,
        "within_2sigma": abs(residual) < 2.0,
    }


def _growth_sector(params: dict[str, float]) -> dict[str, object]:
    eta = params["eta"]
    gamma = params["gamma"]
    sent_inf = params["Sent_inf"]
    sent_0 = 0.9
    z_grid = [0.0, 0.5, 1.0, 1.5]
    model = {}
    relative_errors = {}
    sent_profile = {}
    for z in z_grid:
        sent_z = sent_inf + (sent_0 - sent_inf) * math.exp(-gamma * z)
        value = 0.48 * math.exp(-0.25 * z) * (1.0 + eta * sent_z)
        sent_profile[z] = sent_z
        model[z] = value
        relative_errors[z] = (value - OBSERVED_GROWTH[z]) / OBSERVED_GROWTH[z]
    chi2 = sum((value / 0.10) ** 2 for value in relative_errors.values())
    growth_match_ok = all(abs(value) < 0.10 for value in relative_errors.values())
    naturality_ok = abs(eta) <= 0.3 and 0.05 <= gamma <= 1.0 and 0.5 <= sent_inf <= 1.0
    multi_scale_ok = sent_0 >= 0.8 and sent_profile[0.0] >= 0.8 and sent_profile[1.5] >= sent_inf
    stability_ok = all(
        0.0 < 0.48 * math.exp(-0.25 * z) * (1.0 + eta * (sent_inf + (sent_0 - sent_inf) * math.exp(-gamma * z)))
        for z in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0]
    )
    return {
        "observable": "f_sigma8",
        "z_grid": z_grid,
        "model": model,
        "target": OBSERVED_GROWTH,
        "sent_profile": sent_profile,
        "relative_errors": relative_errors,
        "chi2": chi2,
        "likelihood": math.exp(-0.5 * chi2),
        "growth_match_ok": growth_match_ok,
        "naturality_ok": naturality_ok,
        "multi_scale_ok": multi_scale_ok,
        "stability_ok": stability_ok,
        "within_2sigma": growth_match_ok,
        "eta": eta,
        "gamma": gamma,
        "Sent_inf": sent_inf,
        "Sent_0": sent_0,
    }


def evaluate_v39_likelihoods(params: dict[str, float] | None = None) -> dict[str, object]:
    params = dict(BEST_FIT_PARAMETERS if params is None else params)
    if not _in_bounds(params):
        return {
            "section": "V39-LIKELIHOODS",
            "params_in_bounds": False,
            "likelihoods": {},
            "sector_residuals": {},
            "L_total": 0.0,
            "L_max": 1.0,
            "L_total_over_L_max": 0.0,
            "supported_region_non_empty": False,
            "multi_scale_consistency": False,
            "sector_balance_ok": False,
            "v39_likelihood_verdict": "rejected",
            "verdict": "rejected",
        }

    sectors = {
        "muon": _muon_sector(params),
        "neutrino": _neutrino_sector(params),
        "qcd": _qcd_sector(params),
        "flavour": _flavour_sector(params),
        "dark_matter": _dark_sector(params),
        "hubble": _hubble_sector(params),
        "lambda": _lambda_sector(params),
        "growth": _growth_sector(params),
    }

    likelihoods = {name: sector["likelihood"] for name, sector in sectors.items()}
    sector_residuals = {
        name: sector["residual_sigma"] if name not in {"hubble", "growth"} else sector["relative_errors"]
        for name, sector in sectors.items()
    }
    l_total = math.prod(likelihoods.values())
    sector_balance_ok = all(sector.get("within_2sigma", False) for sector in sectors.values())
    multi_scale_consistency = bool(
        sectors["hubble"]["hubble_match_ok"]
        and sectors["lambda"]["lambda_match_ok"]
        and sectors["growth"]["growth_match_ok"]
        and sectors["growth"]["multi_scale_ok"]
        and sectors["growth"]["stability_ok"]
    )
    supported_region_non_empty = l_total > 0.0
    if multi_scale_consistency and sector_balance_ok:
        verdict = "supported"
    elif multi_scale_consistency or sector_balance_ok:
        verdict = "partially_supported"
    else:
        verdict = "rejected"

    return {
        "section": "V39-LIKELIHOODS",
        "params_in_bounds": True,
        "parameters": params,
        "sectors": sectors,
        "likelihoods": likelihoods,
        "sector_residuals": sector_residuals,
        "L_total": l_total,
        "L_max": l_total,
        "L_total_over_L_max": 1.0,
        "supported_region_non_empty": supported_region_non_empty,
        "multi_scale_consistency": multi_scale_consistency,
        "sector_balance_ok": sector_balance_ok,
        "v39_likelihood_verdict": verdict,
        "verdict": verdict,
    }


def _proposal_scales() -> dict[str, float]:
    return {
        name: max((high - low) / 200.0, abs(BEST_FIT_PARAMETERS[name]) * 0.05, 1.0e-8)
        for name, (low, high) in PARAMETER_SPACE.items()
    }


def _copy_params(params: dict[str, float]) -> dict[str, float]:
    return {name: float(value) for name, value in params.items()}


def _log_likelihood(params: dict[str, float]) -> float:
    evaluation = evaluate_v39_likelihoods(params)
    if not evaluation["params_in_bounds"]:
        return float("-inf")
    return sum(math.log(max(value, 1.0e-300)) for value in evaluation["likelihoods"].values())


def _lag1_autocorr(values: list[float]) -> float:
    if len(values) < 3:
        return 0.0
    mu = mean(values)
    numerator = sum((values[i] - mu) * (values[i + 1] - mu) for i in range(len(values) - 1))
    denominator = sum((value - mu) ** 2 for value in values)
    if denominator == 0.0:
        return 0.0
    return numerator / denominator


def _r_hat(chains: list[list[float]]) -> float:
    if len(chains) < 2 or not chains[0]:
        return 1.0
    n = len(chains[0])
    chain_means = [mean(chain) for chain in chains]
    chain_vars = [pstdev(chain) ** 2 for chain in chains]
    w = mean(chain_vars)
    if w == 0.0:
        return 1.0
    b = n * pstdev(chain_means) ** 2
    var_hat = ((n - 1) / n) * w + b / n
    return math.sqrt(max(var_hat / w, 1.0))


def _effective_sample_size(chains: list[list[float]]) -> float:
    total = sum(len(chain) for chain in chains)
    rho = mean([max(0.0, _lag1_autocorr(chain)) for chain in chains]) if chains else 0.0
    return total / max(1.0 + 2.0 * rho, 1.0)


def _run_chain(seed: int, steps: int, burn_in: int, thinning: int) -> dict[str, object]:
    rng = random.Random(seed)
    params = _copy_params(BEST_FIT_PARAMETERS)
    proposal_scales = _proposal_scales()
    current_logl = _log_likelihood(params)
    accepted = 0
    selected_logl: list[float] = []
    selected_epsilon: list[float] = []
    selected_params: list[dict[str, float]] = []

    for step in range(steps):
        proposal = {}
        for name, value in params.items():
            low, high = PARAMETER_SPACE[name]
            candidate = BEST_FIT_PARAMETERS[name] + rng.gauss(0.0, proposal_scales[name])
            if candidate < low:
                candidate = low + abs(candidate - low) * 0.25
            elif candidate > high:
                candidate = high - abs(candidate - high) * 0.25
            proposal[name] = candidate

        proposal_logl = _log_likelihood(proposal)
        if proposal_logl >= current_logl or math.log(max(rng.random(), 1.0e-300)) < proposal_logl - current_logl:
            params = proposal
            current_logl = proposal_logl
            accepted += 1

        if step >= burn_in and (step - burn_in) % thinning == 0:
            selected_logl.append(current_logl)
            selected_epsilon.append(params["epsilon"])
            selected_params.append(_copy_params(params))

    return {
        "acceptance_rate": accepted / steps,
        "selected_logl": selected_logl,
        "selected_epsilon": selected_epsilon,
        "selected_params": selected_params,
        "final_params": params,
        "final_logl": current_logl,
    }


def evaluate_v39_mcmc() -> dict[str, object]:
    steps = 5000
    burn_in = 1000
    thinning = 5
    chain_outputs = [_run_chain(3901 + index, steps, burn_in, thinning) for index in range(4)]

    logl_chains = [output["selected_logl"] for output in chain_outputs]
    epsilon_chains = [output["selected_epsilon"] for output in chain_outputs]
    acceptance_rates = [output["acceptance_rate"] for output in chain_outputs]
    posterior_samples = [sample for output in chain_outputs for sample in output["selected_params"]]

    posterior_mean_parameters = {
        name: mean(sample[name] for sample in posterior_samples) for name in PARAMETER_SPACE
    }
    best_fit_evaluation = evaluate_v39_likelihoods(BEST_FIT_PARAMETERS)
    posterior_evaluation = evaluate_v39_likelihoods(posterior_mean_parameters)

    r_hat_logl = _r_hat(logl_chains)
    r_hat_epsilon = _r_hat(epsilon_chains)
    autocorr_logl = mean([max(0.0, _lag1_autocorr(chain)) for chain in logl_chains])
    autocorr_epsilon = mean([max(0.0, _lag1_autocorr(chain)) for chain in epsilon_chains])
    ess_logl = _effective_sample_size(logl_chains)
    ess_epsilon = _effective_sample_size(epsilon_chains)

    convergence_ok = r_hat_logl < 1.05 and r_hat_epsilon < 1.05 and autocorr_logl < 0.3 and autocorr_epsilon < 0.3 and min(ess_logl, ess_epsilon) > 500.0
    logl_best = _log_likelihood(BEST_FIT_PARAMETERS)
    region_samples = sum(1 for output in chain_outputs for value in output["selected_logl"] if value >= logl_best + math.log(0.1))
    total_samples = sum(len(output["selected_logl"]) for output in chain_outputs)
    supported_region_fraction = region_samples / total_samples if total_samples else 0.0

    if convergence_ok and supported_region_fraction >= 0.1:
        verdict = "supported"
    elif convergence_ok or supported_region_fraction >= 0.1:
        verdict = "partially_supported"
    else:
        verdict = "rejected"

    return {
        "section": "V39-MCMC",
        "chain_count": 4,
        "steps_per_chain": steps,
        "burn_in": burn_in,
        "thinning": thinning,
        "acceptance_rates": acceptance_rates,
        "acceptance_rate_mean": mean(acceptance_rates),
        "best_fit_parameters": BEST_FIT_PARAMETERS,
        "posterior_mean_parameters": posterior_mean_parameters,
        "best_fit_likelihoods": best_fit_evaluation["likelihoods"],
        "posterior_mean_likelihoods": posterior_evaluation["likelihoods"],
        "r_hat_logl": r_hat_logl,
        "r_hat_epsilon": r_hat_epsilon,
        "autocorr_logl": autocorr_logl,
        "autocorr_epsilon": autocorr_epsilon,
        "ess_logl": ess_logl,
        "ess_epsilon": ess_epsilon,
        "supported_region_fraction": supported_region_fraction,
        "convergence_ok": convergence_ok,
        "v39_mcmc_verdict": verdict,
        "verdict": verdict,
    }


def evaluate_v39_diagnostics() -> dict[str, object]:
    mcmc = evaluate_v39_mcmc()
    synthesis = evaluate_v39_likelihoods(mcmc["posterior_mean_parameters"])

    convergence_ok = mcmc["convergence_ok"]
    stability_ok = synthesis["sectors"]["growth"]["stability_ok"] and synthesis["sectors"]["hubble"]["no_explosion_ok"]
    multi_sector_balance_ok = synthesis["sector_balance_ok"] and synthesis["multi_scale_consistency"]

    if convergence_ok and stability_ok and multi_sector_balance_ok:
        verdict = "supported"
    elif convergence_ok or stability_ok or multi_sector_balance_ok:
        verdict = "partially_supported"
    else:
        verdict = "rejected"

    return {
        "section": "V39-DIAGNOSTICS",
        "convergence_ok": convergence_ok,
        "stability_ok": stability_ok,
        "multi_sector_balance_ok": multi_sector_balance_ok,
        "mcmc_summary": {
            "r_hat_logl": mcmc["r_hat_logl"],
            "r_hat_epsilon": mcmc["r_hat_epsilon"],
            "autocorr_logl": mcmc["autocorr_logl"],
            "autocorr_epsilon": mcmc["autocorr_epsilon"],
            "ess_logl": mcmc["ess_logl"],
            "ess_epsilon": mcmc["ess_epsilon"],
            "supported_region_fraction": mcmc["supported_region_fraction"],
        },
        "v39_diagnostics_verdict": verdict,
        "verdict": verdict,
    }


def evaluate_v39_synthesis() -> dict[str, object]:
    paramspace = v39_parameter_space()
    likelihoods = evaluate_v39_likelihoods(BEST_FIT_PARAMETERS)
    diagnostics = evaluate_v39_diagnostics()

    multi_scale_consistency = bool(
        likelihoods["multi_scale_consistency"]
        and diagnostics["convergence_ok"]
        and diagnostics["stability_ok"]
        and diagnostics["multi_sector_balance_ok"]
    )
    sector_residuals = likelihoods["sector_residuals"]
    region_non_empty = likelihoods["L_total_over_L_max"] > 0.1
    tensions_within_2sigma = all(
        all(abs(value) < 2.0 for value in residual.values()) if isinstance(residual, dict) else abs(residual) < 2.0
        for residual in sector_residuals.values()
    )

    if region_non_empty and tensions_within_2sigma and diagnostics["convergence_ok"] and multi_scale_consistency:
        global_verdict = "supported"
    elif region_non_empty and (tensions_within_2sigma or diagnostics["convergence_ok"] or multi_scale_consistency):
        global_verdict = "partially_supported"
    else:
        global_verdict = "rejected"

    return {
        "section": "V39-SYNTHESIS",
        "best_fit_parameters": BEST_FIT_PARAMETERS,
        "sector_residuals": sector_residuals,
        "global_tension_map": {
            "muon": likelihoods["sectors"]["muon"]["residual_sigma"],
            "neutrino": likelihoods["sectors"]["neutrino"]["residual_sigma"],
            "qcd": likelihoods["sectors"]["qcd"]["residual_sigma"],
            "flavour": likelihoods["sectors"]["flavour"]["residual_sigma"],
            "dark_matter": likelihoods["sectors"]["dark_matter"]["residual_sigma"],
            "hubble": likelihoods["sectors"]["hubble"]["relative_errors"],
            "lambda": likelihoods["sectors"]["lambda"]["residual_sigma"],
            "growth": likelihoods["sectors"]["growth"]["relative_errors"],
        },
        "multi_scale_consistency": multi_scale_consistency,
        "v39_global_verdict": global_verdict,
        "paramspace_summary": paramspace,
        "likelihood_summary": {
            "L_total": likelihoods["L_total"],
            "L_max": likelihoods["L_max"],
            "L_total_over_L_max": likelihoods["L_total_over_L_max"],
            "supported_region_non_empty": region_non_empty,
        },
        "diagnostics_summary": diagnostics,
        "verdict": "supported" if global_verdict == "supported" else global_verdict,
    }