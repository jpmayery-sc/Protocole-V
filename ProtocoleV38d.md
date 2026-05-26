# V38d - DYNAMIQUE STRUCTURELLE DE LA CROISSANCE (fσ8) VIA D1/D2

Version : 0.1

Protocole précédent : [ProtocoleV38c.md](ProtocoleV38c.md)

Wrapper global suggéré :
- [python/scripts/runv38dcosmo_suite.py](python/scripts/runv38dcosmo_suite.py)

Modules :

- V38d-HUBBLE - Test de H(z) (inchangé)
- V38d-LAMBDA - Test de Lambda_eff(K) (inchangé)
- V38d-GROWTH - Dynamique structurelle de fσ8 via D1/D2
- V38d-SYNTHESIS - Cohérence cosmologique multi-couches

---

## 0. Objectif

Passer d’un ansatz polynomial pour G_eff(z) (V38b/V38c) à une dynamique structurelle dérivée de la cohérence D1/D2.

- ne pas modifier les données cosmologiques
- garder la tolérance stricte de 10 %
- conserver la cohérence multi-échelle V35-V37
- faire émerger G_eff(z) à partir d’une équation de relaxation de Sent(Y)

---

## 1. V38d-GROWTH - DYNAMIQUE STRUCTURELLE DE fσ8

### 1.1 Idée centrale

La croissance des structures dépend de la cohérence interne Sent(Y), qui elle-même résulte d’un équilibre dynamique entre deux couches géométriques D1 et D2.

On modélise cette cohérence par une équation de relaxation minimale en z :

$$
\frac{d}{dz} \mathrm{Sent}(Y)(z) = -\gamma [\mathrm{Sent}(Y)(z) - \mathrm{Sent}_\infty]
$$

avec :

- $\gamma > 0$ : taux de relaxation géométrique
- $\mathrm{Sent}_\infty$ : cohérence asymptotique ($z \to \infty$)

### 1.2 Solution analytique

$$
\mathrm{Sent}(Y)(z) = \mathrm{Sent}_\infty + (\mathrm{Sent}_0 - \mathrm{Sent}_\infty) \cdot e^{-\gamma z}
$$

où :

- $\mathrm{Sent}_0 = \mathrm{Sent}(Y)(z=0)$, fixée par V37/V38c, typiquement $\sim 0.9$ en halo
- $\mathrm{Sent}_\infty \in (0, 1)$

### 1.3 Nouvel ansatz pour G_eff(z)

On pose :

$$
G_\mathrm{eff}(z) = G \cdot [1 + \eta \cdot \mathrm{Sent}(Y)(z)]
$$

soit explicitement :

$$
G_\mathrm{eff}(z) = G \cdot \left[1 + \eta \cdot \left\{\mathrm{Sent}_\infty + (\mathrm{Sent}_0 - \mathrm{Sent}_\infty) e^{-\gamma z}\right\}\right]
$$

Paramètres libres :

- $\eta$ : amplitude de la correction géométrique
- $\gamma$ : taux de relaxation
- $\mathrm{Sent}_\infty$ : cohérence asymptotique

Bornes de naturalité :

- $|\eta| \le 0.3$
- $0 < \gamma \le 1.0$
- $0.5 \le \mathrm{Sent}_\infty \le 1.0$

### 1.4 Conditions de croissance

On impose :

1. Fenêtre de 10 % sur fσ8(z) :
   $|f\sigma_8^{\mathrm{eff}}(z) - f\sigma_8^{\mathrm{obs}}(z)| / f\sigma_8^{\mathrm{obs}}(z) < 0.10$ pour $z \in \{0, 0.5, 1, 1.5\}$

2. Naturalité :
   - $|\eta| \le 0.3$
   - $0 < \gamma \le 1.0$
   - $0.5 \le \mathrm{Sent}_\infty \le 1.0$

3. Cohérence multi-échelle :
   - compatibilité avec $\mathrm{Sent}(Y)_\mathrm{halo} \approx 0.9$ (V37/V38c)
   - pas de conflit avec $K_{\mathrm{bg},\mathrm{best}} = 1.0$
   - pas de conflit avec V37-DARK

4. Stabilité :
   - $G_\mathrm{eff}(z) > 0$ pour $z \in [0, 3]$

### 1.5 Sorties V38d-GROWTH

- eta_best
- gamma_best
- Sent_inf_best
- Sent_0
- f_sigma8_eff(z=0, 0.5, 1, 1.5)
- growth_match_ok
- naturality_ok
- multi_scale_ok
- stability_ok
- verdict

---

## 2. V38d-HUBBLE - TEST DE H(z)

Identique à V38c :

$$
H_\mathrm{eff}(z)^2 = H_\mathrm{GR}(z)^2 + \Delta H(K_\mathrm{bg}(z))
$$

avec $K_\mathrm{bg}(z) = K_{\mathrm{bg},\mathrm{best}} \cdot (1+z)^\alpha$.

Conditions :

- hubble_match_ok
- alpha_natural_ok
- no_explosion_ok

Sorties :

- alpha_best
- H0_eff
- hubble_match_ok
- verdict

---

## 3. V38d-LAMBDA - TEST DE Lambda_eff(K)

Identique à V38c :

$$
\Lambda_\mathrm{eff} = \Lambda_0 + \xi \cdot K_\mathrm{bg}
$$

Conditions :

- lambda_match_ok
- xi_natural_ok

Sorties :

- xi_best
- rho_Lambda_eff_over_rho_crit
- lambda_match_ok
- verdict

---

## 4. V38d-SYNTHESIS - COHÉRENCE COSMOLOGIQUE

### 4.1 Objectif

Vérifier que la dynamique structurelle D1/D2 introduite dans G_eff(z) :

- améliore la croissance fσ8(z)
- ne casse pas H(z)
- ne casse pas Lambda_eff
- reste compatible avec la matière noire géométrique (Sent(Y))
- respecte les échelles V35-V37

### 4.2 Sorties attendues

- hubble_summary
- lambda_summary
- growth_summary
- cosmology_consistency
- v38d_global_verdict

---

## 5. CRITÈRES DE VERDICT

- supported :
  - H(z), Lambda_eff, fσ8(z) tous dans leurs fenêtres respectives
  - naturalité et stabilité respectées
  - cosmology_consistency = true

- partially_supported :
  - un module marginal, mais sans rupture multi-échelle

- rejected :
  - croissance hors fenêtre malgré η, γ, Sent_∞ naturels
  - ou conflit fort avec V37-DARK / V35-V37

---

## 6. RÉSULTATS OBSERVÉS - RUN RÉEL

Suite exécutée : v38dcosmo_suite

Horodatage : 20260519-151125Z

Chiffres globaux :

- v38d_global_verdict : supported
- supported_count : 4/4
- modules_tested : 4
- cosmology_consistency : true

Détail des modules :

1. v38dhubble_check.py - supported
   - hubble_match_ok : true
   - alpha_natural_ok : true
   - no_explosion_ok : true
   - verdict : supported

2. v38dlambda_check.py - supported
   - lambda_match_ok : true
   - xi_natural_ok : true
   - rho_Lambda_eff_over_rho_crit : 0.68
   - verdict : supported

3. v38dgrowth_check.py - supported
   - eta_best : 0.012
   - gamma_best : 0.45
   - Sent_inf_best : 0.7
   - Sent_0 : 0.9
   - f_sigma8_eff(z=0) : 0.48518399999999995
   - f_sigma8_eff(z=0.5) : 0.4279685414311829
   - f_sigma8_eff(z=1) : 0.37753656690158593
   - f_sigma8_eff(z=1.5) : 0.33307313247872794
   - growth_match_ok : true
   - naturality_ok : true
   - multi_scale_ok : true
   - stability_ok : true
   - verdict : supported

4. v38dtester_summary_check.py - supported
   - v38d_global_verdict : supported
   - cosmology_consistency : true
   - verdict : supported

Comparaison avec V38c :

- V38c restait polynomial en z
- V38d remplace cette dépendance par une relaxation structurelle Sent(Y)(z)
- H(z) et Lambda_eff restent inchangés par héritage
- aucune rupture multi-échelle n’apparaît
- verdict global : conforme au run réel

Fichiers générés :

- v38dhubble_check_20260519-151124Z.json / .txt
- v38dlambda_check_20260519-151124Z.json / .txt
- v38dgrowth_check_20260519-151125Z.json / .txt
- v38dtester_summary_check_20260519-151125Z.json / .txt
- v38dcosmo_suite_summary_20260519-151125Z.json / .txt

---

## 7. PROCHAINE ÉTAPE

Si V38d est supported :

- V39 : MCMC global sur tous les secteurs avec dynamique D1/D2 explicite

Si V38d est rejected :

- réanalyse de la structure D1/D2
- éventuelle révision de la définition de Sent(Y)