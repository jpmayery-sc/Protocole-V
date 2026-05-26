import math
import statistics as stats

# ============================
# PARAMETRES
# ============================
N = 60                       # fenêtre m<n<k<=N
PETITS = {5,7,11,13}

# filtres (canon)
T_NEUTRON_MAX = 1
ASPECT_NEUTRON_MAX = 2
ASPECT_PROTON_MAX = 3
ASPECT_ELECTRON_MIN = 4

# options importantes (mettre None si inactif)
MIN_NEUTRON = 29           # ex: 29 pour "cosmos"
MIN_GLOBAL  = 29           # ex: 29 pour appliquer a toutes classes

LAMBDA_PHYS = 1836.15267389

# ============================
# OUTILS
# ============================

def coherent_gcd(m, n, k):
    gmn = math.gcd(m, n)
    gnk = math.gcd(n, k)
    gmk = math.gcd(m, k)
    return (gmn == gnk == gmk)


def heron_area(m, n, k):
    s = 0.5*(m+n+k)
    val = s*(s-m)*(s-n)*(s-k)
    if val <= 0:
        return 0.0
    return math.sqrt(val)


def Q_T(m, n, k):
    d1 = n-m
    d2 = k-n
    diff = d2-d1
    Q = 0
    if diff > 0: Q = 1
    elif diff < 0: Q = -1
    T = abs(diff)
    return Q, T


def mass_geo(m, n, k):
    _, T = Q_T(m, n, k)
    A = heron_area(m, n, k)
    return A/(1.0+T*T)


def aspect(m, n, k):
    return k/m


def count_petits(m, n, k):
    return int(m in PETITS) + int(n in PETITS) + int(k in PETITS)


def has_any_petit(m, n, k):
    return (m in PETITS) or (n in PETITS) or (k in PETITS)

# ============================
# CLASSES
# ============================

def is_neutron_like(m, n, k):
    if MIN_NEUTRON is not None and min(m,n,k) < MIN_NEUTRON:
        return False
    if not coherent_gcd(m,n,k):
        return False
    if has_any_petit(m,n,k):
        return False
    Q, T = Q_T(m,n,k)
    if T > T_NEUTRON_MAX:
        return False
    if aspect(m,n,k) > ASPECT_NEUTRON_MAX:
        return False
    return True


def is_proton_like(m, n, k):
    if MIN_GLOBAL is not None and min(m,n,k) < MIN_GLOBAL:
        return False
    if not coherent_gcd(m,n,k):
        return False
    if count_petits(m,n,k) != 1:
        return False
    Q, T = Q_T(m,n,k)
    if Q != 1:
        return False
    if aspect(m,n,k) > ASPECT_PROTON_MAX:
        return False
    return True


def is_electron_like(m, n, k):
    if MIN_GLOBAL is not None and min(m,n,k) < MIN_GLOBAL:
        return False
    if not coherent_gcd(m,n,k):
        return False
    if count_petits(m,n,k) != 1:
        return False
    Q, T = Q_T(m,n,k)
    if Q != -1:
        return False
    if aspect(m,n,k) < ASPECT_ELECTRON_MIN:
        return False
    return True

# ============================
# SCAN
# ============================
Cn, Cp, Ce = [], [], []

for m in range(1, N+1):
    for n in range(m+1, N+1):
        for k in range(n+1, N+1):
            if m+n <= k:
                continue
            if MIN_GLOBAL is not None and min(m,n,k) < MIN_GLOBAL:
                continue
            if is_neutron_like(m,n,k):
                Cn.append((m,n,k))
            if is_proton_like(m,n,k):
                Cp.append((m,n,k))
            if is_electron_like(m,n,k):
                Ce.append((m,n,k))

Mn_list = [mass_geo(*t) for t in Cn]
Mp_list = [mass_geo(*t) for t in Cp]
Me_list = [mass_geo(*t) for t in Ce]

def mean(x): return sum(x)/len(x) if x else float("nan")
def median(x): return stats.median(x) if x else float("nan")

Mn = mean(Mn_list); Mp = mean(Mp_list); Me = mean(Me_list)
medMn = median(Mn_list)
Cint_n = Mn/medMn if (medMn and not math.isnan(Mn)) else float("nan")

lambda_geo  = Mp/Me if (Me and not math.isnan(Mp) and not math.isnan(Me)) else float("nan")
lambda_pred = 1728.0*Cint_n if not math.isnan(Cint_n) else float("nan")
eps = (LAMBDA_PHYS - lambda_pred)/LAMBDA_PHYS if not math.isnan(lambda_pred) else float("nan")

# ============================
# SORTIE
# ============================
print("=== PARAMETRES ===")
print(f"N={N}, MIN_NEUTRON={MIN_NEUTRON}, MIN_GLOBAL={MIN_GLOBAL}")
print(f"T_NEUTRON_MAX={T_NEUTRON_MAX}, ASPECT_N_MAX={ASPECT_NEUTRON_MAX}, ASPECT_P_MAX={ASPECT_PROTON_MAX}, ASPECT_E_MIN={ASPECT_ELECTRON_MIN}")

print("\n=== RESULTATS ===")
print(f"|Cn| = {len(Cn)}")
print(f"|Cp| = {len(Cp)}")
print(f"|Ce| = {len(Ce)}")
print(f"Mn = {Mn}")
print(f"Mp = {Mp}")
print(f"Me = {Me}")
print(f"median(Mn) = {medMn}")
print(f"Cint^(n) = {Cint_n}")
print(f"lambda_geo = {lambda_geo}")
print(f"lambda_pred = {lambda_pred}")
print(f"lambda_phys = {LAMBDA_PHYS}")
print(f"eps = {eps}")

print("\n=== COPIER-COLLER LaTeX (Annexe B) ===")
print(f"Fenêtre : $m<n<k\\le {N}$.")
print(f"$|\\mathcal{{C}}_n|={len(Cn)}$, $|\\mathcal{{C}}_p|={len(Cp)}$, $|\\mathcal{{C}}_e|={len(Ce)}$.")
print(f"$M_n={Mn}$, $M_p={Mp}$, $M_e={Me}$.")
print(f"$\\mathrm{{median}}(M_n)={medMn}$, $C_\\mathrm{{int}}^{{(n)}}={Cint_n}$.")
print(f"$\\lambda_\\mathrm{{geo}}={lambda_geo}$, $\\lambda_\\mathrm{{pred}}={lambda_pred}$, $\\varepsilon={eps}$.")
