# Protocole V6

## Vue d'ensemble

V6 relie explicitement la porte alpha a un mouvement en D2 et au canal electronique associe.

Le protocole est structure en deux axes:

- V6-D2: mouvement effectif en D2 pilote par la porte alpha.
- V6-e: statut de l'electron comme canal D1-D2-D3, teste numeriquement via les pentes V5-N.

Le wrapper global est `v6_d2_electron` et il reproduit la meme logique que V4/V5: chaque test produit un JSON et un TXT, puis la suite emet un verdict global.

## Fichiers ajoutes

- python/scripts/d2motionfromalphaport_check.py
- python/scripts/electronchannelfromalphacheck.py
- python/scripts/runv6suite.py
- python/tests/test_d2motionfromalphaport_check.py
- python/tests/test_electronchannelfromalphacheck.py
- python/tests/test_v6suite.py

## V6-D2

Hypothese testee: une variation de la porte alpha se traduit en un mouvement effectif en D2 via le deficit angulaire, la torsion et la polarisation.

Base numerique heritee de V5-G:

- alpha_ref = 0.0072973525692838015
- alpha_approx = 0.0072992700729927005
- delta_alpha = -1.917503708899e-06
- delta_Dtheta_rad = -1.2048031130217074e-05
- delta_Dtheta_deg = -0.0006903013352036694

Constantes normalisees pour la canalisation D2:

- K_PHI = 10.0
- TAU_CRIT = 0.05
- L = 2.0
- rayons testes: 1.0, 2.0, 5.0

Observables et verifications:

- delta_theta est non nul et tres petit.
- delta_tau suit exactement une loi en 1/r.
- delta_phi et delta_P restent non nuls mais faibles.

Resultats par rayon:

- r = 1.0: delta_tau = -1.917503708899e-06, delta_phi_ref = 3.108751269820e-03, delta_phi_approx = 3.111202545897e-03, delta_P = -3.811699852460e-09
- r = 2.0: delta_tau = -9.587518544494e-07, delta_phi_ref = 7.771878174550e-04, delta_phi_approx = 7.778006364743e-04, delta_P = -2.382316008046e-10
- r = 5.0: delta_tau = -3.835007417798e-07, delta_phi_ref = 1.243500507928e-04, delta_phi_approx = 1.244481018359e-04, delta_P = -6.098729579309e-12

Verdict attendu: conforme.

## V6-e

Hypothese testee: l'electron est un canal D1-D2-D3 dont la reponse effective se lit dans la suite V5-N.

Base numerique heritee de V5-N:

- kappa_2 = 0.002725
- kappa_3 = 0.00031666666666666665
- kappa_4 = 9e-05

Ajustement loi puissance:

- exponent = 4.9456681557600435
- slope = -4.9456681557600435
- rmse = 6.944686902903456e-05
- relative_rmse = environ 0.0667

Verifications:

- la sequence kappa_n est monotone decroissante.
- un seul exposant positif ajuste correctement les trois points.
- le residu relatif reste faible.

Verdict attendu: conforme.

## Suite v6_d2_electron

Le wrapper `runv6suite.py` agrège:

- d2_motion_from_alpha_port
- electron_channel_from_alpha

Resultat attendu:

- suite = v6_d2_electron
- total = 2
- supported_count = 2
- overall_verdict = supported

## Integration dans S-law et Experience 4

V6 est remonte explicitement:

- dans `s_law_master` comme support additionnel,
- dans `experience4_global` comme niveau visible de plus.

## Tests

- test_d2motionfromalphaport_check.py: passe
- test_electronchannelfromalphacheck.py: passe
- test_v6suite.py: passe

## Lecture physique

- V6-D2 montre qu'une variation de alpha reste geometriquement lisible dans D2.
- V6-e montre que l'electron peut etre lu comme canal structurant et non comme objet isole.
- V6 ferme la boucle entre alpha, D2 et electron sans pretendre encore a une loi fondamentale.

## Compte rendu de tests

### Tests unitaires V6

Validation focale lancee sur les trois fichiers de test V6:

- `python/tests/test_d2motionfromalphaport_check.py`
- `python/tests/test_electronchannelfromalphacheck.py`
- `python/tests/test_v6suite.py`

Resultat: 10 tests passes en 43.98 s pour la tranche V6 ciblee, en incluant les suites recablees.

### V6-D2: details numeriques

Dernier rapport: `d2motionfromalphaport_check_20260517-150925Z`

- alpha_ref = 0.0072973525692838015
- alpha_approx = 0.0072992700729927005
- delta_alpha = -1.9175037088989613e-06
- delta_theta_rad = -1.2048031130217074e-05
- delta_theta_small_ok = true
- tau_shape_ok = true
- tau_inverse_ok = true
- effect_structured_ok = true
- verdict = conforme

Constantes de canalisation utilisees:

- K_PHI = 10.0
- TAU_CRIT = 0.05
- L = 2.0
- rayons testes = 1.0, 2.0, 5.0

Resultats par rayon:

- r = 1.0: delta_tau = -1.9175037088989613e-06, delta_phi_ref = 3.1087512698201886e-03, delta_phi_approx = 3.1112025458970424e-03, delta_P = -3.811699852460365e-09
- r = 2.0: delta_tau = -9.587518544494807e-07, delta_phi_ref = 7.771878174550472e-04, delta_phi_approx = 7.778006364742606e-04, delta_P = -2.382316008045684e-10
- r = 5.0: delta_tau = -3.8350074177970553e-07, delta_phi_ref = 1.2435005079280756e-04, delta_phi_approx = 1.2444810183588167e-04, delta_P = -6.0987295793089045e-12

Lecture: le mouvement en D2 est petit mais structuré, avec une torsion strictement en 1/r et un effet de polarisation non nul.

### V6-e: details numeriques

Dernier rapport: `electronchannelfromalphacheck_20260517-150925Z`

- n_values = 2.0, 3.0, 4.0
- kappas = 0.002725, 0.00031666666666666665, 9e-05
- exponent = 4.9456681557600435
- slope = -4.9456681557600435
- rmse = 6.944686902903456e-05
- relative_rmse = 0.06652706985218851
- decreasing_ok = true
- exponent_ok = true
- fit_quality_ok = true
- channel_ok = true
- verdict = conforme

Lecture: la reponse de l'electron suit bien une loi puissance simple et monotone sur les trois points V5-N.

### Suite v6_d2_electron

Dernier resume: `v6_d2_electron_suite_summary_20260517-150925Z`

- overall_verdict = supported
- supported_count = 2
- total = 2
- d2_motion_from_alpha_port = conforme
- electron_channel_from_alpha = conforme

### Integration S-law

Dernier resume: `s_law_master_suite_summary_20260517-150924Z`

- overall_verdict = supported
- supported_count = 10
- support_total = 10
- falsifier_ok = 2
- falsifier_total = 2
- total = 12
- alphaportsuite = supported
- v6_d2_electron = supported
- alpha_phase_observable = supported
- alpha_constant = falsifie

### Integration Experience 4 globale

Dernier resume: `experience4_global_suite_summary_20260517-150925Z`

- overall_verdict = supported
- supported_count = 6
- total = 6
- atom_basics = supported
- point_atome_protocol = supported
- point_atome_master = supported
- s_law_master = supported
- alphaportsuite = supported
- v6_d2_electron = supported

### Bilan de validation

- 6 tests V6 passes en 43.98 s pour la tranche ciblee
- 10 tests passes quand on inclut les suites recablees
- toutes les couches V6, S-law et Experience 4 globale sont au verdict supported