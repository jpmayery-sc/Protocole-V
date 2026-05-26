import csv
import os
import sys

import matplotlib
import numpy as np

matplotlib.use('Agg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.getcwd(), 'scripts'))
from sparc_loader import load_rotmod


G = 4.30091e-6  # kpc (km/s)^2 / Msun


def load_quality_flags(table_path='data/SPARC/Table1.mrt'):
    qmap = {}
    with open(table_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            stripped = line.rstrip('\n')
            if not stripped:
                continue
            if stripped.startswith(('Title:', 'Authors:', 'Table:', 'Byte-by-byte', 'Note ')):
                continue
            if set(stripped.strip()) in ({'='}, {'-'}):
                continue
            parts = stripped.split()
            if len(parts) < 18 or parts[0] == 'Galaxy':
                continue
            try:
                qmap[parts[0]] = int(parts[17])
            except Exception:
                continue
    return qmap


def isothermal_v2(r, rho0, r0_kpc):
    r_safe = np.where(r > 0.0, r, 1e-6)
    x = r_safe / r0_kpc
    return 4.0 * np.pi * G * rho0 * (r0_kpc ** 2) * (1.0 - (1.0 / x) * np.arctan(x))


def profile_velocity(r, rho0, r0_kpc):
    return np.sqrt(np.maximum(0.0, isothermal_v2(r, rho0, r0_kpc)))


def fit_isothermal_profile(r, v_obs, err, v_gas, v_disk, v_bul):
    v_b2 = v_gas**2 + v_disk**2 + v_bul**2
    err2 = err[:, None]
    obs2 = v_obs[:, None]

    log_r0_grid = np.linspace(-2.5, 3.0, 100)
    log_rho_grid = np.linspace(0.0, 13.0, 130)
    r0_grid = 10.0 ** log_r0_grid
    rho_grid = 10.0 ** log_rho_grid

    best = {
        'chi2': np.inf,
        'rho0': None,
        'r0': None,
    }

    def scan_grid(log_r0_values, log_rho_values):
        local_best = {
            'chi2': np.inf,
            'rho0': None,
            'r0': None,
            'chi2_grid': None,
            'rho_grid': None,
            'r0_grid': None,
        }
        for r0 in (10.0 ** log_r0_values):
            coeff = 4.0 * np.pi * G * (r0 ** 2) * (1.0 - (r0 / np.where(r > 0.0, r, 1e-6)) * np.arctan(np.where(r > 0.0, r, 1e-6) / r0))
            model_sq = v_b2[:, None] + coeff[:, None] * (10.0 ** log_rho_values)[None, :]
            model = np.sqrt(np.maximum(0.0, model_sq))
            chi2 = np.sum(((model - obs2) / err2) ** 2, axis=0)
            idx = int(np.argmin(chi2))
            if float(chi2[idx]) < local_best['chi2']:
                local_best['chi2'] = float(chi2[idx])
                local_best['rho0'] = float(10.0 ** log_rho_values[idx])
                local_best['r0'] = float(r0)
                local_best['chi2_grid'] = chi2
                local_best['rho_grid'] = 10.0 ** log_rho_values
                local_best['r0_grid'] = np.array([r0])
        return local_best

    coarse = scan_grid(log_r0_grid, log_rho_grid)

    best_log_r0 = np.log10(coarse['r0'])
    best_log_rho = np.log10(coarse['rho0'])
    ref_log_r0 = np.linspace(max(-3.0, best_log_r0 - 0.6), min(3.2, best_log_r0 + 0.6), 121)
    ref_log_rho = np.linspace(max(-0.2, best_log_rho - 0.7), min(13.5, best_log_rho + 0.7), 151)
    refined = scan_grid(ref_log_r0, ref_log_rho)

    rho0_best = refined['rho0']
    r0_best = refined['r0']
    chi2_min = refined['chi2']
    v_inf = np.sqrt(4.0 * np.pi * G * rho0_best * (r0_best ** 2))
    fit_status = 'boundary' if (
        np.isclose(np.log10(rho0_best), -0.2) or np.isclose(np.log10(rho0_best), 13.5) or
        np.isclose(np.log10(r0_best), -3.0) or np.isclose(np.log10(r0_best), 3.2)
    ) else 'ok'

    return {
        'rho0_best': rho0_best,
        'r0_best': r0_best,
        'v_inf_best': float(v_inf),
        'chi2_min': chi2_min,
        'fit_status': fit_status,
        'chi2_red': float(chi2_min / max(1, len(r) - 2)),
    }


def fit_galaxy(gal, out_dir, q_flag=None):
    data = load_rotmod(gal)
    r = data['r']
    v_obs = data['v_obs']
    err = data['err']
    v_gas = data['v_gas']
    v_disk = data['v_disk']
    v_bul = data['v_bul']

    fit = fit_isothermal_profile(r, v_obs, err, v_gas, v_disk, v_bul)
    v_b2 = v_gas**2 + v_disk**2 + v_bul**2
    v_halo = profile_velocity(r, fit['rho0_best'], fit['r0_best'])
    v_model = np.sqrt(v_b2 + v_halo**2)

    fig_fit = os.path.join(out_dir, f'sparc_{gal}_isothermal_fit.png')
    fig_chi = os.path.join(out_dir, f'sparc_{gal}_isothermal_profile.png')

    plt.figure(figsize=(7, 5))
    plt.errorbar(r, v_obs, yerr=err, fmt='o', markersize=4, label='V_obs')
    plt.plot(r, np.sqrt(v_b2), label='V_baryonic', linestyle='--')
    plt.plot(r, v_model, label=f'Iso halo (rho0={fit["rho0_best"]:.2e}, r0={fit["r0_best"]:.2f} kpc)')
    plt.plot(r, v_halo, label='V_halo', linestyle=':')
    plt.xlabel('r [kpc]')
    plt.ylabel('V [km/s]')
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(fig_fit, dpi=150)
    plt.close()

    plt.figure(figsize=(7, 4))
    plt.plot(r, v_halo, color='C3', label='Halo profile')
    plt.xlabel('r [kpc]')
    plt.ylabel('V_halo [km/s]')
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_chi, dpi=150)
    plt.close()

    return {
        'galaxy': gal,
        'source': data['source'],
        'q_flag': int(q_flag) if q_flag is not None else '',
        'fit_status': fit['fit_status'],
        'n_points': int(len(r)),
        'rho0_best': float(fit['rho0_best']),
        'r0_best': float(fit['r0_best']),
        'v_inf_best': float(fit['v_inf_best']),
        'chi2_min': float(fit['chi2_min']),
        'chi2_red': float(fit['chi2_red']),
    }


def main():
    rotmod_dir = 'data/SPARC/Rotmod'
    out_dir = 'results/result-analyse'
    os.makedirs(out_dir, exist_ok=True)
    qmap = load_quality_flags()

    files = [f for f in os.listdir(rotmod_dir) if f.endswith('_rotmod.dat')]
    files.sort()

    results = []
    for f in files:
        gal = f.replace('_rotmod.dat', '')
        try:
            print('Fitting iso', gal)
            results.append(fit_galaxy(gal, out_dir, q_flag=qmap.get(gal)))
        except Exception as e:
            print('Failed for', gal, e)

    csv_path = os.path.join(out_dir, 'sparc_batch_isothermal_results.csv')
    keys = ['galaxy', 'source', 'q_flag', 'fit_status', 'n_points', 'rho0_best', 'r0_best', 'v_inf_best', 'chi2_min', 'chi2_red']
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=keys)
        writer.writeheader()
        for row in results:
            writer.writerow({k: row.get(k, '') for k in keys})

    summary_path = os.path.join(out_dir, 'sparc_batch_isothermal_summary.txt')
    rho = np.array([row['rho0_best'] for row in results if row['rho0_best'] > 0])
    r0 = np.array([row['r0_best'] for row in results if row['r0_best'] > 0])
    chi = np.array([row['chi2_min'] for row in results if np.isfinite(row['chi2_min'])])
    q1 = [row for row in results if str(row.get('q_flag', '')) == '1']
    q1_rho = np.array([row['rho0_best'] for row in q1 if row['rho0_best'] > 0])
    q1_r0 = np.array([row['r0_best'] for row in q1 if row['r0_best'] > 0])
    q1_chi = np.array([row['chi2_min'] for row in q1 if np.isfinite(row['chi2_min'])])
    with open(summary_path, 'w', encoding='utf-8') as sf:
        sf.write('SPARC isothermal batch summary\n')
        sf.write(f'Total galaxies fitted: {len(results)}\n')
        sf.write(f'rho0 median/mean/std: {np.median(rho):.6e} / {np.mean(rho):.6e} / {np.std(rho):.6e} Msun/kpc^3\n')
        sf.write(f'r0 median/mean/std: {np.median(r0):.6f} / {np.mean(r0):.6f} / {np.std(r0):.6f} kpc\n')
        sf.write(f'chi2_min median: {np.median(chi):.6f}\n')
        sf.write(f'Q=1 subset: N={len(q1)}, rho0 median={np.median(q1_rho):.6e}, r0 median={np.median(q1_r0):.6f} kpc, chi2 median={np.median(q1_chi):.6f}\n')
        sf.write('Boundary cases:\n')
        for row in results:
            if row['fit_status'] != 'ok':
                sf.write(f"- {row['galaxy']} (Q={row.get('q_flag', 'NA')}, rho0={row['rho0_best']:.6e}, r0={row['r0_best']:.6f}, chi2={row['chi2_min']:.6f})\n")

    print('Batch complete. Results saved to', csv_path)
    print('Summary saved to', summary_path)


if __name__ == '__main__':
    main()