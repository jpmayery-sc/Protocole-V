# V35 - CALIBRATION NUMÉRIQUE DES MODULES MUON g-2 ET NEUTRINOS

Protocole précédent : [ProtocoleV34.md](ProtocoleV34.md)

Wrapper global : [python/scripts/runv35numericcalibration_suite.py](python/scripts/runv35numericcalibration_suite.py)

Modules :

- V35-MUON - Scan numérique de $\Delta a_\mu(K,T)$
- V35-NEUTRINOS - Scan numérique de $m_{\nu,\mathrm{eff}}(K)$
- V35-VERSION-FINALE - Résumé opérationnel pour testeur

---

## 0. Objectif de V35

V35 prend les relations validées en V34 et cherche les meilleurs points numériques dans un espace de paramètres limité.

Le but n'est plus de savoir si la structure passe.
Le but est de trouver où elle s'aligne le mieux avec les ordres de grandeur observés.

---

## 1. V35-MUON - Scan numérique de $\Delta a_\mu(K,T)$

### 1.1 Cible

On garde l'ansatz :

$$
\Delta a_\mu \approx A_\mu \cdot \tilde K + B_\mu \cdot \tilde T
$$

La cible numérique reste :

$$
|\Delta a_{\mu,\mathrm{exp}}| \approx 10^{-9}
$$

### 1.2 Espace de scan

On balaye un petit ensemble de points :

- $A_\mu \in \{5\times 10^{-7}, 1\times 10^{-6}, 2\times 10^{-6}\}$
- $B_\mu \in \{5\times 10^{-7}, 1\times 10^{-6}, 2\times 10^{-6}\}$
- $\tilde K \in \{2\times 10^{-4}, 5\times 10^{-4}, 8\times 10^{-4}\}$
- $\tilde T \in \{2\times 10^{-4}, 5\times 10^{-4}, 8\times 10^{-4}\}$

### 1.3 Critère de score

On minimise :

$$
\mathrm{score}_\mu = |\Delta a_\mu - 10^{-9}| + \Pi_\mu
$$

où $\Pi_\mu$ pénalise les sorties hors bornes pour l'électron et le tau.

### 1.4 Sorties attendues

- best_muon_point
- best_muon_score
- muon_target_hit
- electron_safe
- tau_safe
- muon_verdict

---

## 2. V35-NEUTRINOS - Scan numérique de $m_{\nu,\mathrm{eff}}(K)$

### 2.1 Cible

On garde :

$$
m_{\nu_i,\mathrm{eff}}^2 \approx m_{0_i}^2 + \lambda_i \cdot K_{\mathrm{bg}}
$$

avec les cibles :

- $\Delta m^2_{\mathrm{sol}} \approx 7.4 \times 10^{-5}\,\mathrm{eV}^2$
- $\Delta m^2_{\mathrm{atm}} \approx 2.5 \times 10^{-3}\,\mathrm{eV}^2$

### 2.2 Espace de scan

On balaye :

- $K_{\mathrm{bg}} \in \{0.5, 1.0, 2.0\}$
- $\lambda_2 \in \{3.7\times 10^{-5}, 7.4\times 10^{-5}, 1.0\times 10^{-4}\}$
- $\lambda_3 \in \{1.5\times 10^{-3}, 2.5\times 10^{-3}, 3.5\times 10^{-3}\}$

### 2.3 Critère de score

On minimise :

$$
\mathrm{score}_\nu = |\Delta m^2_{\mathrm{sol}} - 7.4\times 10^{-5}| + |\Delta m^2_{\mathrm{atm}} - 2.5\times 10^{-3}| + \Omega_\nu
$$

où $\Omega_\nu$ pénalise la violation de $\sum m_\nu < 1\,\mathrm{eV}$.

### 2.4 Sorties attendues

- best_neutrino_point
- best_neutrino_score
- oscillations_hit
- cosmology_safe
- parameters_reasonable
- neutrino_verdict

---

## 3. Synthèse V35

### 3.1 Sorties attendues

- muon_verdict
- neutrino_verdict
- global_verdict
- best_points
- scan_statistics

### 3.2 Critère final

- supported : les deux scans trouvent un point compatible
- partially_supported : un scan trouve un point et l'autre non
- rejected : aucun scan n'atteint la zone cible

---

## 4. Résultats observés - run réel

Suite exécutée : v35numericcalibration_suite

Horodatage : 20260519-104502Z

Chiffres globaux :

- global_verdict : supported
- supported_count : 3/3
- total : 3
- best_points_count : 2
- scan_statistics_count : 2

Détail des modules :

1. v35muon_scan_check.py - supported
	- scan_count : 81
	- muon_target_hit : true
	- electron_safe : true
	- tau_safe : true
	- verdict : supported

2. v35neutrino_scan_check.py - supported
	- scan_count : 27
	- oscillations_hit : true
	- cosmology_safe : true
	- parameters_reasonable : true
	- verdict : supported

3. v35tester_summary_check.py - supported
	- muon_verdict : supported
	- neutrino_verdict : supported
	- global_verdict : supported
	- verdict : supported

Comparaison avec V35 :

- meilleur point muon : A_mu = 1e-06, B_mu = 1e-06
- meilleure correction muon : Delta a_mu = 1e-09
- meilleur point neutrinos : K_bg = 1.0, lambda_2 = 7.4e-05, lambda_3 = 0.0025
- meilleure somme des masses neutrinos : 0.05860232526704263 eV
- score neutrinos : 0.0
- verdict global : conforme au run réel

Fichiers générés :

- v35muon_scan_check_20260519-104501Z.json / .txt
- v35neutrino_scan_check_20260519-104501Z.json / .txt
- v35tester_summary_check_20260519-104502Z.json / .txt
- v35numericcalibration_suite_summary_20260519-104502Z.json / .txt

### 4.1 Prochaine étape

- V36 - [ProtocoleV36.md](ProtocoleV36.md)
- Suite V36 - [python/scripts/runv36scalestrong_suite.py](python/scripts/runv36scalestrong_suite.py)
- V37 - Extension aux mésons B et à la matière noire