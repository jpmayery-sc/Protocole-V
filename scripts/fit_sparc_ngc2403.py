import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
import os
# ensure scripts/ is importable when running the script from workspace root
sys.path.insert(0, os.path.join(os.getcwd(), 'scripts'))
from sparc_loader import load_rotmod


def compute_best_vhalo(r, v_obs, err, v_gas, v_disk, v_bul):
    v_b2 = v_gas**2 + v_disk**2 + v_bul**2

    # coarse grid search
    grid = np.linspace(0.0, 300.0, 601)
    chi = np.empty_like(grid)
    for i, vh in enumerate(grid):
        v_model = np.sqrt(v_b2 + vh**2)
        chi[i] = np.sum(((v_model - v_obs) / err)**2)
    idx = np.argmin(chi)
    v0 = grid[idx]

    # refined grid around best
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
    return best_vh, chi_min, grid2, chi2


def rho0_from_vh(vh, r0_kpc=1.0):
    # G in kpc (km/s)^2 / Msun
    G = 4.30091e-6
    rho0 = vh**2 / (4.0 * np.pi * G * (r0_kpc**2))
    return rho0


def main():
    gal = 'NGC2403'
    data = load_rotmod(gal)
    r = data['r']
    v_obs = data['v_obs']
    err = data['err']
    v_gas = data['v_gas']
    v_disk = data['v_disk']
    v_bul = data['v_bul']

    out_dir = 'results/result-analyse'
    os.makedirs(out_dir, exist_ok=True)

    best_vh, chi_min, grid2, chi2 = compute_best_vhalo(r, v_obs, err, v_gas, v_disk, v_bul)

    # compute baryonic and total model
    v_b2 = v_gas**2 + v_disk**2 + v_bul**2
    v_model = np.sqrt(v_b2 + best_vh**2)

    # estimate 1-sigma from delta chi2 = 1 (one free parameter)
    target = chi_min + 1.0
    idx_min = np.argmin(chi2)
    # left interpolation
    left_idx = None
    for i in range(idx_min - 1, -1, -1):
        if chi2[i] > target and chi2[i+1] <= target:
            x0, x1 = grid2[i], grid2[i+1]
            y0, y1 = chi2[i], chi2[i+1]
            left_idx = x0 + (target - y0) * (x1 - x0) / (y1 - y0)
            break
    # right interpolation
    right_idx = None
    for i in range(idx_min + 1, len(chi2)):
        if chi2[i] > target and chi2[i-1] <= target:
            x0, x1 = grid2[i-1], grid2[i]
            y0, y1 = chi2[i-1], chi2[i]
            right_idx = x0 + (target - y0) * (x1 - x0) / (y1 - y0)
            break

    vh_minus = best_vh - (left_idx if left_idx is not None else best_vh)
    vh_plus = (right_idx if right_idx is not None else best_vh) - best_vh

    # save chi2 curve plot
    chi2_fig = os.path.join(out_dir, f'sparc_{gal}_chi2.png')
    plt.figure(figsize=(6,4))
    plt.plot(grid2, chi2, '-', color='C1')
    plt.axvline(best_vh, color='k', linestyle='--', label=f'best Vh={best_vh:.2f}')
    if left_idx is not None:
        plt.axvline(left_idx, color='gray', linestyle=':')
    if right_idx is not None:
        plt.axvline(right_idx, color='gray', linestyle=':')
    plt.xlabel('V_halo [km/s]')
    plt.ylabel(r'Chi^2')
    plt.legend()
    plt.tight_layout()
    plt.savefig(chi2_fig, dpi=150)
    plt.close()

    # Bootstrap resampling to estimate uncertainty (resample datapoints)
    def bootstrap_vh(nboot=500, seed=42):
        rng = np.random.default_rng(seed)
        vh_samples = []
        N = len(r)
        for _ in range(nboot):
            idxs = rng.integers(0, N, N)
            r_b = r[idxs]
            v_obs_b = v_obs[idxs]
            err_b = err[idxs]
            v_gas_b = v_gas[idxs]
            v_disk_b = v_disk[idxs]
            v_bul_b = v_bul[idxs]
            vh_b, _, _, _ = compute_best_vhalo(r_b, v_obs_b, err_b, v_gas_b, v_disk_b, v_bul_b)
            vh_samples.append(vh_b)
        return np.array(vh_samples)

    nboot = 500
    vh_samples = bootstrap_vh(nboot=nboot, seed=20260506)
    p16, p50, p84 = np.percentile(vh_samples, [16, 50, 84])

    # save bootstrap histogram
    bs_fig = os.path.join(out_dir, f'sparc_{gal}_bootstrap_vh.png')
    plt.figure(figsize=(6,4))
    plt.hist(vh_samples, bins=30, color='C2', alpha=0.8)
    plt.axvline(p50, color='k', linestyle='--', label=f'median={p50:.2f}')
    plt.axvline(p16, color='gray', linestyle=':', label=f'-1sigma={p16:.2f}')
    plt.axvline(p84, color='gray', linestyle=':', label=f'+1sigma={p84:.2f}')
    plt.xlabel('V_halo [km/s]')
    plt.ylabel('Counts')
    plt.legend()
    plt.tight_layout()
    plt.savefig(bs_fig, dpi=150)
    plt.close()


    out_dir = 'results/result-analyse'
    os.makedirs(out_dir, exist_ok=True)
    fig_path = os.path.join(out_dir, f'sparc_{gal}_fit.png')
    txt_path = os.path.join(out_dir, f'sparc_{gal}_fit.txt')

    plt.figure(figsize=(7,5))
    plt.errorbar(r, v_obs, yerr=err, fmt='o', markersize=4, label='V_obs')
    plt.plot(r, np.sqrt(v_b2), label='V_baryonic', linestyle='--')
    plt.plot(r, v_model, label=f'Model (Vhalo={best_vh:.2f} km/s)')
    plt.hlines(best_vh, r.min(), r.max(), colors='gray', linestyles=':', label='V_halo (flat)')
    plt.xlabel('r [kpc]')
    plt.ylabel('V [km/s]')
    plt.legend()
    plt.tight_layout()
    plt.savefig(fig_path, dpi=150)
    plt.close()

    # compute rho0 for r0=1 kpc
    rho0 = rho0_from_vh(best_vh, r0_kpc=1.0)

    with open(txt_path, 'w') as f:
        f.write(f'Galaxy: {gal}\n')
        f.write(f'Rotmod source: {data["source"]}\n')
        f.write(f'Best V_halo (flat): {best_vh:.6f} km/s\n')
        f.write(f'Chi2_min: {chi_min:.6f}\n')
        if left_idx is not None or right_idx is not None:
            f.write(f'V_halo 1-sigma lower bound: {best_vh - (left_idx if left_idx is not None else best_vh):.6f} km/s\n')
            f.write(f'V_halo 1-sigma upper bound: {best_vh + (right_idx if right_idx is not None else best_vh):.6f} km/s\n')
            f.write(f'V_halo -1sigma/+1sigma: -{abs(vh_minus):.6f} / +{abs(vh_plus):.6f} km/s\n')
        else:
            f.write('Unable to determine 1-sigma bounds from chi2 curve.\n')
        f.write(f'Inferred rho0 (r0=1.0 kpc): {rho0:.6e} Msun/kpc^3\n')

    print('Fit complete:')
    print(f'  Galaxy: {gal}')
    print(f'  Best V_halo = {best_vh:.4f} km/s')
    print(f'  rho0 (r0=1 kpc) = {rho0:.6e} Msun/kpc^3')
    print(f'  Saved: {fig_path} and {txt_path}')


if __name__ == '__main__':
    main()
