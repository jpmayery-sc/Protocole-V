# V36 - ANALYSE DES ÉCHELLES K/T/Y ET TEST D'UNE PARTICULE FORTE

Protocole précédent : [ProtocoleV35.md](ProtocoleV35.md)

Wrapper global : [python/scripts/runv36scalestrong_suite.py](python/scripts/runv36scalestrong_suite.py)

Modules :

- V36-SCALES - Analyse des échelles issues de V35
- V36-STRONG - Test d'une particule forte
- V36-SYNTHESIS - Lecture physique multi-échelle

---

## 0. Objectif de V36

1. Analyser les échelles géométriques implicites extraites en V35.
2. Tester si le même schéma K/T/Y reste cohérent pour une particule dominée par l'interaction forte.

---

## 1. V36-SCALES - Analyse des échelles issues de V35

### 1.1 Entrées

Depuis V35 :

- A_mu_best, B_mu_best
- K_tilde_best, T_tilde_best
- K_bg_best
- lambda_2_best, lambda_3_best
- sum_mnu_best

### 1.2 Reconstruction des échelles

On définit :

$$
K_{\mathrm{loc,best}} = \tilde K_{\mathrm{best}} \cdot K_0
\qquad
T_{\mathrm{loc,best}} = \tilde T_{\mathrm{best}} \cdot T_0
$$

avec $K_0 = T_0 = 1$ pour la version opérationnelle.

### 1.3 Sorties

- K_loc_best, T_loc_best
- K_bg_best
- scale_ratio_K = K_loc_best / K_bg_best
- scale_ratio_T = T_loc_best / K_bg_best
- leptonic_couplings = {A_mu_best, B_mu_best}
- neutrino_couplings = {lambda_2_best, lambda_3_best}

---

## 2. V36-STRONG - Test d'une particule forte

### 2.1 Choix de la particule

Paramètre :

- chosen_particle ∈ {pion_charged, kaon_charged, glueball_0pp}

### 2.2 Ansatz de masse géométrique

$$
m_{\mathrm{strong,eff}} \approx M_{0,\mathrm{strong}} + \alpha_s \cdot K_{\mathrm{loc,strong}} + \beta_s \cdot T_{\mathrm{loc,strong}}
$$

### 2.3 Hypothèse d'échelle forte

$$
K_{\mathrm{loc,strong}} \approx c_K \cdot K_{\mathrm{loc,best}}
\qquad
T_{\mathrm{loc,strong}} \approx c_T \cdot T_{\mathrm{loc,best}}
$$

avec $c_K, c_T \in \{5, 10, 20\}$.

### 2.4 Condition de masse

On cherche des triplets $(M_{0,\mathrm{strong}}, \alpha_s, \beta_s)$ tels que :

$$
m_{\mathrm{strong,eff}} \approx m_{\mathrm{exp}}(\mathrm{chosen\_particle})
$$

On impose :

- $10^{-3} \le \alpha_s, \beta_s \le 10^{-1}$
- $\alpha_s / A_{\mu,\mathrm{best}} < 10^6$
- $\beta_s / B_{\mu,\mathrm{best}} < 10^6$

### 2.5 Tests de cohérence

- mass_match_ok
- naturality_ok
- hierarchy_ok
- v36_strong_verdict

---

## 3. V36-SYNTHESIS - Lecture physique

### 3.1 Objectif

Relier les échelles leptoniques, neutrinos et fortes pour tester la cohérence multi-échelle du schéma K/T/Y.

### 3.2 Sorties attendues

- scales_summary
- couplings_summary
- multi_scale_consistency
- v36_global_verdict

---

## 4. Résultats observés - run réel

Suite exécutée : v36scalestrong_suite

Horodatage : 20260519-131903Z

Chiffres globaux :

- v36_global_verdict : supported
- supported_count : 3/3
- total : 3
- multi_scale_consistency : true
- strong_particle_tested : 1

Détail des modules :

1. v36scales_check.py - supported
	- K_loc_best : 0.0002
	- T_loc_best : 0.0008
	- K_bg_best : 1.0
	- scale_ratio_K : 0.0002
	- scale_ratio_T : 0.0008
	- verdict : supported

2. v36strong_check.py - supported
	- chosen_particle : glueball_0pp
	- m_exp : 1.6
	- m_strong_eff : 1.59999
	- mass_match_ok : true
	- naturality_ok : true
	- hierarchy_ok : true
	- verdict : supported

3. v36tester_summary_check.py - supported
	- v36_global_verdict : supported
	- multi_scale_consistency : true
	- verdict : supported

Comparaison avec V36 :

- les échelles V35 sont réutilisées sans rupture
- la hiérarchie forte reste compatible avec les couplages leptoniques
- le glueball 0++ peut être calibré dans la fenêtre visée
- verdict global : conforme au run réel

Fichiers générés :

- v36scales_check_20260519-131903Z.json / .txt
- v36strong_check_20260519-131903Z.json / .txt
- v36tester_summary_check_20260519-131903Z.json / .txt
- v36scalestrong_suite_summary_20260519-131903Z.json / .txt

### 4.1 Prochaine étape

- V37 - [ProtocoleV37.md](ProtocoleV37.md)
- Suite V37 - [python/scripts/runv37extensions_suite.py](python/scripts/runv37extensions_suite.py)
- V38 - Préparation d'un MCMC global