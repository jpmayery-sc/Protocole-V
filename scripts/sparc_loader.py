import os
import numpy as np


def load_rotmod(galaxy_name, base_dir="data/SPARC/Rotmod"):
    """Charge un fichier Rotmod SPARC pour `galaxy_name`.

    Retourne dict avec clés: r, v_obs, err, v_gas, v_disk, v_bulge
    """
    candidates = [
        f"{galaxy_name}_rotmod.dat",
        f"{galaxy_name}_rotmod.txt",
        f"{galaxy_name}_rotmod.dat",
    ]
    found = None
    for c in candidates:
        path = os.path.join(base_dir, c)
        if os.path.exists(path):
            found = path
            break
    if found is None:
        # try to find any file starting with galaxy_name
        for fname in os.listdir(base_dir):
            if fname.startswith(galaxy_name):
                found = os.path.join(base_dir, fname)
                break
    if found is None:
        raise FileNotFoundError(f"Rotmod file for {galaxy_name} not found in {base_dir}")

    data = []
    with open(found, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) < 6:
                continue
            vals = [float(x) for x in parts[:8]]
            data.append(vals)

    arr = np.array(data)
    r = arr[:, 0]
    v_obs = arr[:, 1]
    err = arr[:, 2]
    v_gas = arr[:, 3]
    v_disk = arr[:, 4]
    v_bul = arr[:, 5]

    return {
        "r": r,
        "v_obs": v_obs,
        "err": err,
        "v_gas": v_gas,
        "v_disk": v_disk,
        "v_bul": v_bul,
        "source": found,
    }
