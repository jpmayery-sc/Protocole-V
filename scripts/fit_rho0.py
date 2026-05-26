import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
import math

# Galaxy parameters (modifiable)
M_disk = 5e10  # Msun
r_s = 3.0  # kpc
r0 = 1.0  # kpc (scale for emergent halo)
G = 4.30091727003628e-6  # kpc (km/s)^2 / Msun

# Target rotation velocity (flat) at r_target
V_target = 200.0  # km/s
r_target = 15.0  # kpc where we match the flat velocity

# Disk contribution at r (approx exponential disk enclosed mass)
def V_disk_at_r(r):
    M_enclosed = M_disk * (1 - np.exp(-r/r_s)*(1 + r/r_s))
    return np.sqrt(G * M_enclosed / r)

Vd = V_disk_at_r(r_target)
print(f"V_disk({r_target} kpc) = {Vd:.2f} km/s")

# Required emergent halo contribution
V_em_req = math.sqrt(max(0.0, V_target**2 - Vd**2))
print(f"Required V_em = {V_em_req:.2f} km/s")

# For emergent halo with rho = rho0*(r0/r)^2 -> V_em^2 = 4*pi*G*rho0*r0^2 (constant)
rho0_required = V_em_req**2 / (4 * math.pi * G * r0**2)
print(f"rho0 required = {rho0_required:.3e} Msun/kpc^3 (for r0={r0} kpc)")

# Generate rotation curve with fitted rho0
r = np.linspace(0.1, 30, 300)

# Disk
M_enclosed_disk = M_disk * (1 - np.exp(-r/r_s)*(1 + r/r_s))
V_disk = np.sqrt(G * M_enclosed_disk / r)

# Emergent halo with fitted rho0
M_enclosed_em = 4*np.pi * rho0_required * r0**2 * r
V_em = np.sqrt(G * M_enclosed_em / r)

V_tot = np.sqrt(V_disk**2 + V_em**2)

outdir = Path('results/result-analyse')
outdir.mkdir(parents=True, exist_ok=True)

plt.figure()
plt.plot(r, V_disk, label='Baryons')
plt.plot(r, V_em, label='Emergent halo (fitted)')
plt.plot(r, V_tot, label='Total')
plt.axhline(V_target, color='k', linestyle='--', label=f'Target {V_target} km/s')
plt.xlabel('r [kpc]')
plt.ylabel('v_c [km/s]')
plt.legend()
plt.grid(True)
plt.title('Rotation curve with fitted rho0')
fn = outdir / 'rotation_curve_fitted.png'
plt.savefig(fn, dpi=150)
plt.close()

# Save fitted parameter
with open(outdir / 'fitted_rho0.txt', 'w') as f:
    f.write(f"rho0={rho0_required:.6e} Msun/kpc^3\n")
    f.write(f"V_disk_at_{r_target}kpc={Vd:.6f} km/s\n")
    f.write(f"V_em_required={V_em_req:.6f} km/s\n")

print('Saved fitted rotation plot and parameters to', outdir.resolve())