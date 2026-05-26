import math
import csv
from pathlib import Path

H0 = 70.0
Omega_b = 0.05
Omega_m_LCDM = 0.3
Omega_L_LCDM = 0.7
Omega_emergent = 0.25
Omega_act0 = 0.7
z_star = 0.46
dz = 0.1

def linspace(a, b, n):
    return [a + i*(b-a)/(n-1) for i in range(n)]

def H_LCDM(z):
    return H0 * math.sqrt(Omega_m_LCDM*(1+z)**3 + Omega_L_LCDM)

def H_LRD(z):
    rho_emergent = Omega_emergent * (1+z)**3
    rho_act = Omega_act0 * math.tanh((z - z_star)/dz)
    term = Omega_b*(1+z)**3 + rho_emergent + max(rho_act, 0.0)
    return H0 * math.sqrt(term)

z_vals = linspace(0.0, 2.0, 201)
outdir = Path('results/result-analyse')
outdir.mkdir(parents=True, exist_ok=True)
fn = outdir / 'H_summary.csv'
with open(fn, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['z', 'H_LCDM', 'H_LRD'])
    for z in z_vals:
        writer.writerow([f"{z:.6f}", f"{H_LCDM(z):.6f}", f"{H_LRD(z):.6f}"])

print('Wrote', fn.resolve())
