# V33 - MODULES MUON g-2 ET NEUTRINOS

Protocole précédent : [ProtocoleV32.md](ProtocoleV32.md)

Wrapper global : [python/scripts/runv33ktyrefinement_suite.py](python/scripts/runv33ktyrefinement_suite.py)

Modules :

- V33-MUON - Affinage mathématique de $\Delta a_\mu(K,T)$
- V33-NEUTRINOS - Masse effective $m_{\nu,\mathrm{eff}}(K)$ et $\Delta m^2$
- V33-VERSION-FINALE - Résumé opérationnel pour testeur

---

## 0. Objectif de V33

Affiner deux cas pilotes de V32 :

1. Muon g-2 : correction géométrique $\Delta a_\mu(K,T)$
2. Neutrinos : masse effective $m_{\nu,\mathrm{eff}}(K)$ et $\Delta m^2$

But :

- proposer des formes un peu plus précises
- garder des paramètres libres à contraindre
- rester compatible avec les ordres de grandeur expérimentaux

---

## 1. V33-MUON - Ansatz pour $\Delta a_\mu(K,T)$

### 1.1 Rappel

$$
a_\mu^{\mathrm{total}} = a_\mu^{\mathrm{MS}} + \Delta a_\mu(K,T)
$$

Données :

- $a_\mu^{\mathrm{MS}} \approx 1.165918 \times 10^{-3}$
- anomalie $|\Delta a_\mu| \sim 10^{-9}$ à $10^{-10}$

### 1.2 Variables géométriques locales

On définit, le long de la trajectoire du muon :

- $K_{\mathrm{loc}} = \langle K(x,t) \rangle_{\mathrm{traj}}$
- $T_{\mathrm{loc}} = \langle T(x,t) \rangle_{\mathrm{traj}}$

On suppose que $K_{\mathrm{loc}}$ et $T_{\mathrm{loc}}$ sont de petits paramètres effectifs.

### 1.3 Ansatz linéaire minimal

$$
\Delta a_\mu \approx \alpha_\mu \cdot K_{\mathrm{loc}} + \beta_\mu \cdot T_{\mathrm{loc}}
$$

où :

- $\alpha_\mu$, $\beta_\mu$ : coefficients de couplage à déterminer
- $K_{\mathrm{loc}}$, $T_{\mathrm{loc}}$ : grandeurs adimensionnées ou rendues adimensionnelles

Pour rendre cela propre, on peut normaliser :

$$
\tilde K = \frac{K_{\mathrm{loc}}}{K_0}
\qquad
\tilde T = \frac{T_{\mathrm{loc}}}{T_0}
$$

avec $K_0$, $T_0$ des échelles de référence.

Alors :

$$
\Delta a_\mu \approx A_\mu \cdot \tilde K + B_\mu \cdot \tilde T
$$

avec $A_\mu$, $B_\mu \sim 10^{-9}$.

### 1.4 Variante quadratique

Si les effets linéaires sont trop faibles, on peut tester :

$$
\Delta a_\mu \approx A_\mu \cdot \tilde K + B_\mu \cdot \tilde T + C_\mu \cdot \tilde K \cdot \tilde T
$$

ou :

$$
\Delta a_\mu \approx A_\mu \cdot \tilde K + B_\mu \cdot \tilde T + C_\mu \cdot \tilde K^2 + D_\mu \cdot \tilde T^2
$$

À analyser :

- signe de $\Delta a_\mu$
- taille : $|\Delta a_\mu| \sim 10^{-9}$

### 1.5 Points à analyser

- choix raisonnable de $K_0$, $T_0$
- ordre de grandeur possible de $\tilde K$, $\tilde T$
- lien potentiel de $A_\mu$, $B_\mu$ avec des constantes plus fondamentales

---

## 2. V33-NEUTRINOS - $m_{\nu,\mathrm{eff}}(K)$ et $\Delta m^2$

### 2.1 Rappel

$$
m_{\nu,\mathrm{eff}} = f(K)
$$

Oscillations :

$$
\Delta m^2_{ij} = m_{\nu_i}^2 - m_{\nu_j}^2
$$

Données :

- $\Delta m^2_{\mathrm{sol}} \sim 7.4 \times 10^{-5}\,\mathrm{eV}^2$
- $\Delta m^2_{\mathrm{atm}} \sim 2.5 \times 10^{-3}\,\mathrm{eV}^2$
- $\sum m_\nu < 1\,\mathrm{eV}$

### 2.2 Ansatz simple pour $m_{\nu,\mathrm{eff}}$

Pour une saveur $i$ :

$$
m_{\nu_i,\mathrm{eff}} \approx m_{0_i} + \gamma_i \cdot K_{\mathrm{bg}}
$$

où :

- $K_{\mathrm{bg}}$ : valeur de fond de $K$ sur grande échelle
- $m_{0_i}$ : terme minimal
- $\gamma_i$ : coefficient de couplage géométrique

### 2.3 Forme quadratique

On peut aussi tester :

$$
m_{\nu_i,\mathrm{eff}}^2 \approx m_{0_i}^2 + \lambda_i \cdot K_{\mathrm{bg}}
$$

Alors :

$$
\Delta m^2_{ij} = (m_{0_i}^2 - m_{0_j}^2) + (\lambda_i - \lambda_j) \cdot K_{\mathrm{bg}}
$$

Cas intéressant :

- si $m_{0_i}^2 \approx m_{0_j}^2$
- alors $\Delta m^2_{ij} \approx (\lambda_i - \lambda_j) \cdot K_{\mathrm{bg}}$

### 2.4 Dépendance environnementale faible

$$
K_{\mathrm{bg}} \rightarrow K_{\mathrm{bg}} + \delta K_{\mathrm{env}}
$$

avec $\delta K_{\mathrm{env}} \ll K_{\mathrm{bg}}$.

Alors :

$$
\Delta m^2_{ij}(\mathrm{env}) \approx \Delta m^2_{ij}^0 + (\lambda_i - \lambda_j) \cdot \delta K_{\mathrm{env}}
$$

### 2.5 Points à analyser

- ordre de grandeur plausible de $K_{\mathrm{bg}}$
- taille possible de $\lambda_i - \lambda_j$
- lien possible avec d'autres observables

---

## 3. Synthèse V33

### 3.1 Formes finales à tester

Muon :

$$
\Delta a_\mu \approx A_\mu \cdot \tilde K + B_\mu \cdot \tilde T + \text{termes croisés éventuels}
$$

Neutrinos :

$$
m_{\nu_i,\mathrm{eff}}^2 \approx m_{0_i}^2 + \lambda_i \cdot K_{\mathrm{bg}}
$$

$$
\Delta m^2_{ij} \approx (m_{0_i}^2 - m_{0_j}^2) + (\lambda_i - \lambda_j) \cdot K_{\mathrm{bg}}
$$

### 3.2 Liens possibles

- $K_{\mathrm{bg}}$ et $K_{\mathrm{loc}}$ peuvent être reliés par une même structure de fond
- si $K$ est la courbure interne universelle, le muon sonde $K_{\mathrm{loc}}, T_{\mathrm{loc}}$ et les neutrinos sondent $K_{\mathrm{bg}}$

### 3.3 Prochaine étape

- choisir des échelles $K_0$, $T_0$, $K_{\mathrm{bg}}$ plausibles
- fixer des ordres de grandeur pour $A_\mu$, $B_\mu$, $\lambda_i$
- vérifier si l'on peut reproduire $\Delta a_\mu$ et $\Delta m^2$ sans violer $\sum m_\nu < 1\,\mathrm{eV}$

---

## 4. Résultats observés - run réel

Suite exécutée : v33ktyrefinement_suite

Horodatage : 20260519-102222Z

Chiffres globaux :

- overall_verdict : supported
- supported_count : 3/3
- total : 3
- validated_predictions : 5
- validated_modules : 2
- falsifiable_predictions : true

Détail des modules :

1. v33math_check.py - supported
	- ansatz_count : 5
	- constraint_count : 5
	- verdict : supported

2. v33predictions_check.py - supported
	- prediction_count : 5
	- kty_ansatz_set : defined
	- verdict : supported

3. v33tester_summary_check.py - supported
	- validated_predictions : 5
	- validated_modules : 2
	- verdict : supported

Comparaison avec V33 :

- la correction muon reste à l'ordre de grandeur attendu
- les deux formes neutrinos restent compatibles avec les oscillations
- la structure garde des paramètres libres à contraindre
- verdict global : conforme au run réel

Fichiers générés :

- v33math_check_20260519-102222Z.json / .txt
- v33predictions_check_20260519-102222Z.json / .txt
- v33tester_summary_check_20260519-102222Z.json / .txt
- v33ktyrefinement_suite_summary_20260519-102222Z.json / .txt

### 4.1 Prochaine étape

- V34 - [ProtocoleV34.md](ProtocoleV34.md)
- Suite V34 - [python/scripts/runv34geometricfalsification_suite.py](python/scripts/runv34geometricfalsification_suite.py)