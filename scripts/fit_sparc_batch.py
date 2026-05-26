import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
sys.path.insert(0, os.path.join(os.getcwd(), 'scripts'))
from sparc_loader import load_rotmod


def load_quality_flags(table_path='data/SPARC/Table1.mrt'):
    qmap = {}
    with open(table_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            stripped = line.rstrip('\n')
            if not stripped:
                continue
            if stripped.startswith(('Title:', 'Authors:', 'Table:', 'Byte-by-byte', 'Note ')):
                continue
            if set(stripped.strip()) == {'='} or set(stripped.strip()) == {'-'}:
                continue
            parts = stripped.split()
            if len(parts) < 18 or parts[0] == 'Galaxy':
                continue
            try:
                qmap[parts[0]] = int(parts[17])
            except Exception:
                continue
    return qmap


def compute_best_vhalo(r, v_obs, err, v_gas, v_disk, v_bul):
    v_b2 = v_gas**2 + v_disk**2 + v_bul**2
    grid = np.linspace(0.0, 300.0, 601)
    chi = np.empty_like(grid)
    for i, vh in enumerate(grid):
        v_model = np.sqrt(v_b2 + vh**2)
        chi[i] = np.sum(((v_model - v_obs) / err)**2)
    idx = np.argmin(chi)
    v0 = grid[idx]
    lo = max(0.0, v0 - 20.0)
    hi = v0 + 20.0
    grid2 = np.linspace(lo, hi, 2001)
    chi2 = np.empty_like(grid2)
    for i, vh in enumerate(grid2):
        v_model = np.sqrt(v_b2 + vh**2)
        chi2[i] = np.sum(((v_model - v_obs) / err)**2)
    idx2 = np.argmin(chi2)
    best_vh = grid2[idx2]
    chi_min = chi2[idx2]
    chi2_at_zero = chi2[0]
    return best_vh, chi_min, chi2_at_zero, grid2, chi2


def rho0_from_vh(vh, r0_kpc=1.0):
    G = 4.30091e-6
    rho0 = vh**2 / (4.0 * np.pi * G * (r0_kpc**2))
    return rho0


def bootstrap_vh(r, v_obs, err, v_gas, v_disk, v_bul, nboot=200, seed=20260506):
    rng = np.random.default_rng(seed)
    N = len(r)
    samples = []
    for _ in range(nboot):
        idxs = rng.integers(0, N, N)
        vh_b, _, _, _, _ = compute_best_vhalo(r[idxs], v_obs[idxs], err[idxs], v_gas[idxs], v_disk[idxs], v_bul[idxs])
        samples.append(vh_b)
    return np.array(samples)


def fit_galaxy(gal, out_dir, q_flag=None, nboot=200):
    data = load_rotmod(gal)
    r = data['r']
    v_obs = data['v_obs']
    err = data['err']
    v_gas = data['v_gas']
    v_disk = data['v_disk']
    v_bul = data['v_bul']

    best_vh, chi_min, chi2_at_zero, grid2, chi2 = compute_best_vhalo(r, v_obs, err, v_gas, v_disk, v_bul)

    # chi2 bounds
    target = chi_min + 1.0
    idx_min = np.argmin(chi2)
    left_idx = None
    for i in range(idx_min - 1, -1, -1):
        if chi2[i] > target and chi2[i+1] <= target:
            x0, x1 = grid2[i], grid2[i+1]
            y0, y1 = chi2[i], chi2[i+1]
            left_idx = x0 + (target - y0) * (x1 - x0) / (y1 - y0)
            break
    right_idx = None
    for i in range(idx_min + 1, len(chi2)):
        if chi2[i] > target and chi2[i-1] <= target:
            x0, x1 = grid2[i-1], grid2[i]
            y0, y1 = chi2[i-1], chi2[i]
            right_idx = x0 + (target - y0) * (x1 - x0) / (y1 - y0)
            break

    vh_minus = best_vh - (left_idx if left_idx is not None else best_vh)
    vh_plus = (right_idx if right_idx is not None else best_vh) - best_vh

    # bootstrap
    vh_samples = bootstrap_vh(r, v_obs, err, v_gas, v_disk, v_bul, nboot=nboot)
    p16, p50, p84 = np.percentile(vh_samples, [16, 50, 84])

    fit_status = 'boundary_zero' if best_vh <= 1e-12 else 'ok'
    delta_chi2_vh0 = chi2_at_zero - chi_min

    # save figures
    fig_fit = os.path.join(out_dir, f'sparc_{gal}_fit.png')
    fig_chi = os.path.join(out_dir, f'sparc_{gal}_chi2.png')
    fig_bs = os.path.join(out_dir, f'sparc_{gal}_bootstrap_vh.png')

    v_b2 = v_gas**2 + v_disk**2 + v_bul**2
    v_model = np.sqrt(v_b2 + best_vh**2)
    plt.figure(figsize=(7,5))
    plt.errorbar(r, v_obs, yerr=err, fmt='o', markersize=4, label='V_obs')
    plt.plot(r, np.sqrt(v_b2), label='V_baryonic', linestyle='--')
    plt.plot(r, v_model, label=f'Model (Vhalo={best_vh:.2f} km/s)')
    plt.hlines(best_vh, r.min(), r.max(), colors='gray', linestyles=':', label='V_halo (flat)')
    plt.xlabel('r [kpc]')
    plt.ylabel('V [km/s]')
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_fit, dpi=150)
    plt.close()

    plt.figure(figsize=(6,4))
    plt.plot(grid2, chi2, '-', color='C1')
    plt.axvline(best_vh, color='k', linestyle='--')
    if left_idx is not None:
        plt.axvline(left_idx, color='gray', linestyle=':')
    if right_idx is not None:
        plt.axvline(right_idx, color='gray', linestyle=':')
    plt.xlabel('V_halo [km/s]')
    plt.ylabel('Chi^2')
    plt.tight_layout()
    plt.savefig(fig_chi, dpi=150)
    plt.close()

    plt.figure(figsize=(6,4))
    plt.hist(vh_samples, bins=30, color='C2', alpha=0.8)
    plt.axvline(p50, color='k', linestyle='--')
    plt.axvline(p16, color='gray', linestyle=':')
    plt.axvline(p84, color='gray', linestyle=':')
    plt.xlabel('V_halo [km/s]')
    plt.ylabel('Counts')
    plt.tight_layout()
    plt.savefig(fig_bs, dpi=150)
    plt.close()

    rho0 = rho0_from_vh(best_vh, r0_kpc=1.0)

    return {
        'galaxy': gal,
        'source': data['source'],
        'q_flag': int(q_flag) if q_flag is not None else '',
        'fit_status': fit_status,
        'n_points': int(len(r)),
        'vh_best': float(best_vh),
        'chi2_min': float(chi_min),
        'chi2_vh0': float(chi2_at_zero),
        'delta_chi2_vh0': float(delta_chi2_vh0),
        'vh_minus': float(abs(vh_minus)),
        'vh_plus': float(abs(vh_plus)),
        'vh_bs_p16': float(p16),
        'vh_bs_p50': float(p50),
        'vh_bs_p84': float(p84),
        'rho0_r0_1kpc': float(rho0),
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
            print('Fitting', gal)
            res = fit_galaxy(gal, out_dir, q_flag=qmap.get(gal), nboot=200)
            results.append(res)
        except Exception as e:
            print('Failed for', gal, e)

    # save CSV
    import csv
    csv_path = os.path.join(out_dir, 'sparc_batch_results.csv')
    keys = ['galaxy','source','q_flag','fit_status','n_points','vh_best','chi2_min','chi2_vh0','delta_chi2_vh0','vh_minus','vh_plus','vh_bs_p16','vh_bs_p50','vh_bs_p84','rho0_r0_1kpc']
    with open(csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, '') for k in keys})

    q1_csv_path = os.path.join(out_dir, 'sparc_batch_results_q1.csv')
    with open(q1_csv_path, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=keys)
        writer.writeheader()
        for r in results:
            if str(r.get('q_flag', '')) == '1' and r.get('fit_status') == 'ok':
                writer.writerow({k: r.get(k, '') for k in keys})

    def summarize(subset):
        vh = np.array([float(r['vh_best']) for r in subset if float(r['vh_best']) > 0])
        rho = np.array([float(r['rho0_r0_1kpc']) for r in subset if float(r['rho0_r0_1kpc']) > 0])
        chi = np.array([float(r['chi2_min']) for r in subset if np.isfinite(float(r['chi2_min']))])
        return {
            'n': len(subset),
            'n_vh_pos': len(vh),
            'vh_mean': float(np.mean(vh)) if len(vh) else np.nan,
            'vh_median': float(np.median(vh)) if len(vh) else np.nan,
            'vh_std': float(np.std(vh)) if len(vh) else np.nan,
            'rho_mean': float(np.mean(rho)) if len(rho) else np.nan,
            'rho_median': float(np.median(rho)) if len(rho) else np.nan,
            'rho_std': float(np.std(rho)) if len(rho) else np.nan,
            'chi_median': float(np.median(chi)) if len(chi) else np.nan,
        }

    all_summary = summarize(results)
    q1_summary = summarize([r for r in results if str(r.get('q_flag', '')) == '1'])
    zero_cases = [r for r in results if float(r['vh_best']) <= 1e-12]
    zero_by_q = {}
    for r in zero_cases:
        key = str(r.get('q_flag', 'NA'))
        zero_by_q[key] = zero_by_q.get(key, 0) + 1

    summary_path = os.path.join(out_dir, 'sparc_batch_summary.txt')
    with open(summary_path, 'w', encoding='utf-8') as sf:
        sf.write('SPARC batch summary\n')
        sf.write(f'Total galaxies fitted: {all_summary["n"]}\n')
        sf.write(f'Fits with vh_best>0: {all_summary["n_vh_pos"]}\n')
        sf.write(f'vh_best mean/median/std: {all_summary["vh_mean"]:.6f} / {all_summary["vh_median"]:.6f} / {all_summary["vh_std"]:.6f} km/s\n')
        sf.write(f'rho0 mean/median/std: {all_summary["rho_mean"]:.6e} / {all_summary["rho_median"]:.6e} / {all_summary["rho_std"]:.6e} Msun/kpc^3\n')
        sf.write(f'Median chi2_min: {all_summary["chi_median"]:.6f}\n')
        sf.write(f'Quality Q=1 subset: N={q1_summary["n"]}, vh_best>0={q1_summary["n_vh_pos"]}, vh_median={q1_summary["vh_median"]:.6f} km/s, rho_median={q1_summary["rho_median"]:.6e} Msun/kpc^3\n')
        sf.write('Zero-vh cases by Q: ' + ', '.join(f'Q{q}={n}' for q, n in sorted(zero_by_q.items())) + '\n')
        sf.write('Zero-vh galaxies:\n')
        for r in zero_cases:
            sf.write(f'- {r["galaxy"]} (Q={r.get("q_flag", "NA")}, chi2_min={float(r["chi2_min"]):.6f}, chi2_vh0={float(r["chi2_vh0"]):.6f})\n')

    print('Batch complete. Results saved to', csv_path)
    print('Filtered Q=1 CSV saved to', q1_csv_path)
    print('Summary saved to', summary_path)


if __name__ == '__main__':
    main()
