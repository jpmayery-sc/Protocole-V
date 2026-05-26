# V37 - EXTENSION AUX MÉSONS B ET À LA MATIÈRE NOIRE

Protocole précédent : [ProtocoleV36.md](ProtocoleV36.md)

Wrapper global : [python/scripts/runv37extensions_suite.py](python/scripts/runv37extensions_suite.py)

Modules :

- V37-BPHYSICS - Test des mésons B
- V37-DARK - Test de la matière noire
- V37-SYNTHESIS - Lecture physique multi-secteur

---

## 0. Objectif de V37

1. Tester si le schéma K/T/Y reste cohérent dans le secteur flavour.
2. Tester si la lecture géométrique de la matière noire peut être calibrée sans casser les échelles V35-V36.

V37 prépare V38 (cosmo) et V39 (MCMC global).

---

## 1. V37-BPHYSICS - Test des mésons B

### 1.1 Données expérimentales

Les anomalies flavour les plus connues sont les tensions sur $R_K$ et $R_{K^*}$, avec un écart de quelques pour cent entre les canaux électroniques et muoniques.

### 1.2 Ansatz géométrique

$$
\Delta P(B \to K \ell\ell) \approx C_\ell \cdot F(K_{\mathrm{loc}}, T_{\mathrm{loc}})
$$

### 1.3 Hypothèse d'échelle flavour

$$
K_{\mathrm{loc}}^B = d_K \cdot K_{\mathrm{loc,best}}
\qquad
T_{\mathrm{loc}}^B = d_T \cdot T_{\mathrm{loc,best}}
$$

avec $d_K, d_T \in \{2, 5, 10\}$.

### 1.4 Condition flavour

On impose :

$$
R_{K,\mathrm{eff}} = \left(\frac{P_\mu}{P_e}\right)_{\mathrm{eff}} \approx 1 + \delta_{R_K}
$$

avec $\delta_{R_K} \in [0.01, 0.10]$.

### 1.5 Tests de cohérence

- flavour_match_ok
- naturality_ok
- hierarchy_ok
- v37_B_verdict

---

## 2. V37-DARK - Test de la matière noire

### 2.1 Données cibles

La matière noire doit reproduire des profils de rotation plats et une fraction de masse invisible dominante.

### 2.2 Ansatz géométrique

$$
g_{\mathrm{eff}} = g_{\mathrm{GR}} + \delta g(\mathrm{Sent}(Y))
$$

avec $\mathrm{Sent}(Y)$ la cohérence interne.

### 2.3 Hypothèse d'échelle cosmologique

$$
\mathrm{Sent}(Y)_{\mathrm{halo}} = 1 - \varepsilon
$$

avec $\varepsilon \in \{0.05, 0.10, 0.20\}$.

### 2.4 Condition DM

On impose :

$$
v_{\mathrm{rot,eff}}(r) \approx \mathrm{constante}
$$

dans la zone $r \in [5\,\mathrm{kpc}, 20\,\mathrm{kpc}]$ et :

$$
\rho_{\mathrm{DM,eff}} / \rho_{\mathrm{baryon}} \approx 5 \pm 2
$$

### 2.5 Tests de cohérence

- halo_match_ok
- epsilon_ok
- multi_scale_ok
- v37_DM_verdict

---

## 3. V37-SYNTHESIS - Lecture physique

### 3.1 Objectif

Relier le secteur flavour, le secteur DM et les échelles V35-V36 pour tester la cohérence multi-secteur.

### 3.2 Sorties attendues

- flavour_summary
- dark_summary
- multi_sector_consistency
- v37_global_verdict

---

## 4. Résultats observés - run réel

Suite exécutée : v37extensions_suite

Horodatage : 20260519-134135Z

Chiffres globaux :

- v37_global_verdict : supported
- supported_count : 3/3
- total : 3
- multi_sector_consistency : true
- sectors_tested : 2

Détail des modules :

1. v37bphysics_check.py - supported
	- chosen_system : B_to_K_ll
	- delta_RK : 0.04999999999999992
	- flavour_match_ok : true
	- naturality_ok : true
	- hierarchy_ok : true
	- verdict : supported

2. v37dark_check.py - supported
	- Sent_Y_halo : 0.9
	- epsilon : 0.1
	- density_ratio : 5.0
	- halo_match_ok : true
	- epsilon_ok : true
	- multi_scale_ok : true
	- verdict : supported

3. v37tester_summary_check.py - supported
	- v37_global_verdict : supported
	- multi_sector_consistency : true
	- verdict : supported

Comparaison avec V37 :

- l'écart flavour reste dans la fenêtre 1% à 10%
- la matière noire reproduit une densité effective de halo compatible
- la cohérence multi-secteur reste positive
- verdict global : conforme au run réel

Fichiers générés :

- v37bphysics_check_20260519-134134Z.json / .txt
- v37dark_check_20260519-134134Z.json / .txt
- v37tester_summary_check_20260519-134134Z.json / .txt
- v37extensions_suite_summary_20260519-134135Z.json / .txt

### 4.1 Prochaine étape

- V38 - [ProtocoleV38.md](ProtocoleV38.md)
- Suite V38 - [python/scripts/runv38cosmology_suite.py](python/scripts/runv38cosmology_suite.py)
- V39 - MCMC global sur tous les secteurs