# V34 - FALSIFICATION GÉOMÉTRIQUE DES MODULES MUON g-2 ET NEUTRINOS

Protocole précédent : [ProtocoleV33.md](ProtocoleV33.md)

Wrapper global : [python/scripts/runv34geometricfalsification_suite.py](python/scripts/runv34geometricfalsification_suite.py)

Modules :

- V34-MUON - Falsification de $\Delta a_\mu(K,T)$
- V34-NEUTRINOS - Falsification de $m_{\nu,\mathrm{eff}}(K)$
- V34-VERSION-FINALE - Synthèse opérationnelle pour testeur

---

## 0. Objectif de V34

Après V33, V34 vise à relier les paramètres géométriques aux données expérimentales et à falsifier agressivement chaque ansatz.

V34 ne cherche pas à faire marcher le modèle.
Elle cherche à voir ce qui casse.

---

## 1. V34-MUON - Falsification de $\Delta a_\mu(K,T)$

### 1.1 Rappel de l'ansatz V33

$$
\Delta a_\mu \approx A_\mu \cdot \tilde K + B_\mu \cdot \tilde T + \text{termes croisés éventuels}
$$

avec :

$$
\tilde K = \frac{K_{\mathrm{loc}}}{K_0}
\qquad
\tilde T = \frac{T_{\mathrm{loc}}}{T_0}
$$

Donnée cible : $|\Delta a_{\mu,\mathrm{exp}}| \sim 10^{-9}$.

### 1.2 Contraintes directes

On impose :

$$
A_\mu \cdot \tilde K + B_\mu \cdot \tilde T \approx 10^{-9}
$$

Tests :

- si $\tilde K, \tilde T \ll 10^{-3}$ alors les coefficients doivent devenir énormes, rejet
- si $A_\mu$ ou $B_\mu$ dépassent $10^{-3}$, rejet
- si le signe de $\Delta a_\mu$ ne peut pas être reproduit, rejet

### 1.3 Cohérence avec les autres leptons

On impose que les mêmes paramètres ne détruisent pas l'électron ni le tau.

Tests :

- si $|\Delta a_e| > 10^{-12}$, rejet
- si la correction tau devient trop grande, rejet

### 1.4 Limite MS

$$
\lim_{\tilde K, \tilde T \to 0} \Delta a_\mu = 0
$$

Si l'ansatz ne s'annule pas naturellement, rejet.

### 1.5 Verdict muon

Le module produit :

- muon_constraints_satisfied
- electron_safe
- tau_safe
- ms_limit_ok
- muon_verdict

---

## 2. V34-NEUTRINOS - Falsification de $m_{\nu,\mathrm{eff}}(K)$

### 2.1 Rappel de l'ansatz V33

$$
m_{\nu_i,\mathrm{eff}}^2 \approx m_{0_i}^2 + \lambda_i \cdot K_{\mathrm{bg}}
$$

$$
\Delta m^2_{ij} \approx (m_{0_i}^2 - m_{0_j}^2) + (\lambda_i - \lambda_j) \cdot K_{\mathrm{bg}}
$$

Données cibles :

- $\Delta m^2_{\mathrm{sol}} \sim 7.4 \times 10^{-5}\,\mathrm{eV}^2$
- $\Delta m^2_{\mathrm{atm}} \sim 2.5 \times 10^{-3}\,\mathrm{eV}^2$
- $\sum m_\nu < 1\,\mathrm{eV}$

### 2.2 Reproduction des oscillations

Tests :

- si aucun jeu $(\lambda_i, m_{0_i}, K_{\mathrm{bg}})$ ne reproduit $\Delta m^2_{\mathrm{sol}}$, rejet
- si aucun jeu ne reproduit $\Delta m^2_{\mathrm{atm}}$, rejet

### 2.3 Contrainte cosmologique

Tests :

- si les masses deviennent trop grandes, rejet
- si $K_{\mathrm{bg}}$ doit devenir gigantesque, rejet

### 2.4 Cohérence interne

Tests :

- si les $\lambda_i$ doivent être séparés par des facteurs supérieurs à $10^6$, rejet
- si $m_{0_i}^2$ doit devenir négatif, rejet

### 2.5 Dépendance environnementale

Tests :

- si $\delta K_{\mathrm{env}}$ induit des variations trop grandes, rejet
- si $\delta K_{\mathrm{env}}$ doit être finement ajusté, rejet

### 2.6 Verdict neutrinos

Le module produit :

- oscillations_ok
- cosmology_ok
- parameters_reasonable
- neutrino_verdict

---

## 3. Synthèse V34

### 3.1 Sorties attendues

- muon_verdict
- neutrino_verdict
- global_verdict
- rejected_reasons
- parameter_ranges

### 3.2 Critère final

- supported : si les deux modules passent tous les tests
- partially_supported : si un module passe et l'autre échoue
- rejected : si les deux échouent ou si l'échec est catastrophique

---

## 4. Résultats observés - run réel

Suite exécutée : v34geometricfalsification_suite

Horodatage : 20260519-103021Z

Chiffres globaux :

- global_verdict : supported
- supported_count : 3/3
- total : 3
- rejected_reasons_count : 0
- parameter_ranges_count : 2

Détail des modules :

1. v34muon_check.py - supported
	- muon_constraints_satisfied : true
	- electron_safe : true
	- tau_safe : true
	- ms_limit_ok : true
	- verdict : supported

2. v34neutrinos_check.py - supported
	- oscillations_ok : true
	- cosmology_ok : true
	- parameters_reasonable : true
	- verdict : supported

3. v34tester_summary_check.py - supported
	- muon_verdict : supported
	- neutrino_verdict : supported
	- global_verdict : supported
	- verdict : supported

Comparaison avec V34 :

- correction muon : 1e-9, dans la cible
- correction électron : 1e-12, sous le seuil
- correction tau : 1e-11, sous le seuil
- oscillations neutrinos : reproduites à l'échelle cible
- somme des masses neutrinos : 0.05860232526704263 eV, compatible avec la contrainte cosmologique
- verdict global : conforme au run réel

Fichiers générés :

- v34muon_check_20260519-103020Z.json / .txt
- v34neutrinos_check_20260519-103020Z.json / .txt
- v34tester_summary_check_20260519-103021Z.json / .txt
- v34geometricfalsification_suite_summary_20260519-103021Z.json / .txt

### 4.1 Prochaine étape

- V35 - [ProtocoleV35.md](ProtocoleV35.md)
- Suite V35 - [python/scripts/runv35numericcalibration_suite.py](python/scripts/runv35numericcalibration_suite.py)
- V36 - Intégration avec GEOTUB
- V37 - Extension aux mésons B et à la matière noire