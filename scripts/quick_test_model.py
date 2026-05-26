import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

# Cosmological H(z) comparison
H0 = 70.0  # km/s/Mpc
Omega_b = 0.05
Omega_r = 0.0
# Standard LCDM params (for demo)
Omega_m_LCDM = 0.3
Omega_L_LCDM = 0.7

# LRD-like model params (demo)
Omega_b_lrd = Omega_b
Omega_emergent = 0.25
Omega_act0 = 0.7
z_star = 0.46
dz = 0.1

z = np.linspace(0, 2.0, 201)

def H_LCDM(z):
    return H0 * np.sqrt(Omega_r*(1+z)**4 + Omega_m_LCDM*(1+z)**3 + Omega_L_LCDM)

def H_LRD(z):
    rho_emergent = Omega_emergent * (1+z)**3
    rho_act = Omega_act0 * np.tanh((z - z_star)/dz)
    return H0 * np.sqrt(Omega_r*(1+z)**4 + Omega_b_lrd*(1+z)**3 + rho_emergent + np.maximum(rho_act, 0.0))

H1 = H_LCDM(z)
H2 = H_LRD(z)

outdir = Path('../results')
outdir.mkdir(parents=True, exist_ok=True)
plt.figure()
plt.plot(z, H1/H0, label='LCDM (H/H0)')
plt.plot(z, H2/H0, label='LRD-like (H/H0)')
plt.xlabel('z')
plt.ylabel('H(z)/H0')
plt.legend()
plt.title('Comparaison H(z)')
plt.grid(True)
plt.savefig(outdir / 'H_vs_z.png', dpi=150)
plt.close()

# Rotation curve: baryons + emergent halo with F(r)~1/r leading to rho~1/r^2
G = 4.30091727003628e-6  # kpc (km/s)^2 / Msun
M_disk = 5e10  # Msun
r_s = 3.0  # kpc (disk scale)

r = np.linspace(0.1, 30, 300)
# Exponential disk mass enclosed (approx)
M_enclosed_disk = M_disk * (1 - np.exp(-r/r_s)*(1 + r/r_s))
V_disk = np.sqrt(G * M_enclosed_disk / r)

# Emergent halo: rho = rho0 * (r0/r)^2 -> M_enclosed = 4*pi*rho0*r0^2 * r
rho0 = 0.01  # Msun / kpc^3 (demo scaling)
r0 = 1.0  # kpc
M_enclosed_em = 4*np.pi * rho0 * r0**2 * r
V_em = np.sqrt(G * M_enclosed_em / r)

V_tot = np.sqrt(V_disk**2 + V_em**2)

plt.figure()
plt.plot(r, V_disk, label='Baryons')
plt.plot(r, V_em, label='Emergent halo (flat)')
plt.plot(r, V_tot, label='Total')
plt.xlabel('r [kpc]')
plt.ylabel('v_c [km/s]')
plt.legend()
plt.grid(True)
plt.title('Courbe de rotation demo')
plt.savefig(outdir / 'rotation_curve_demo.png', dpi=150)
plt.close()

print('Saved plots to', outdir.resolve())
