# V48 - TEST DU SECTEUR ELECTRON-5 / NEUTRINOS

Version : 0.1

Protocole precedent : [ProtocoleV47.md](ProtocoleV47.md)

Wrapper global suggere :
- [python/scripts/runv48neutrinos_suite.py](python/scripts/runv48neutrinos_suite.py)

Modules :

- V48-QUARK-MASS-DERIVATION - Cohérence des masses des quarks u, d, s, c, b, t
- V48-HADRON-COLLECTIVE-MODE - Cohérence des masses collectives des hadrons simples
- V48-PMNS-NEUTRINO - Angles PMNS, spectre leger et splittings neutrinos

## 0. Objectif

Tester si le modele geometrico-effectif reste compatible avec :

- les masses des quarks de base
- les masses hadroniques de reference
- la structure PMNS des neutrinos
- le spectre leger et les splittings mesurés

## 8. Resultats observes (run reel)

Suite executee : electron5_core
Horodatage : 20260517-142802Z

Chiffres globaux :
- overall_verdict : supported
- supported_count : 3/3

Points saillants :
- quark masses dans les tolerances visees pour u, d, s, c, b, t
- hadrons simples dans les tolerances visees pour pion, kaon, proton, neutron, lambda0, delta++
- angles PMNS tous supportes
- splittings neutrinos supportes

### 8.1 Resultats numeriques detailles

| Check | Verdict | Chiffres principaux |
|-------|---------|---------------------|
| Quark mass derivation | supported | ordered = true, tolerance_ok = true, light_ok = true, heavy_ok = true |
| Hadron collective mode | supported | ordered = true, all_match = true, meson_ok = true, baryon_ok = true |
| PMNS neutrino | supported | all_angles_ok = true, large_mixing_ok = true, hierarchy_ok = true, light_ok = true, splitting_ok = true |

### 8.2 Quark masses

| Quark | Masse predite (MeV) | Masse de reference (MeV) | Erreur relative |
|------|----------------------:|--------------------------:|----------------:|
| u | 2.5 | 2.2 | 0.136364 |
| d | 4.5 | 4.7 | 0.042553 |
| s | 95.0 | 93.0 | 0.021505 |
| c | 1270.0 | 1270.0 | 0.000000 |
| b | 4200.0 | 4180.0 | 0.004785 |
| t | 173000.0 | 172760.0 | 0.001389 |

### 8.3 Hadrons simples

| Hadron | Type | Quark content | Masse predite (MeV) | Masse de reference (MeV) | Erreur relative |
|-------|------|---------------|----------------------:|--------------------------:|----------------:|
| pion_plus | meson | u dbar | 140.0 | 139.57 | 0.003081 |
| kaon_plus | meson | u sbar | 494.0 | 493.68 | 0.000648 |
| proton | baryon | u u d | 938.5 | 938.27 | 0.000245 |
| neutron | baryon | u d d | 939.6 | 939.57 | 0.000032 |
| lambda0 | baryon | u d s | 1115.7 | 1115.68 | 0.000018 |
| delta_plus_plus | baryon | u u u | 1232.0 | 1232.0 | 0.000000 |

### 8.4 PMNS neutrinos

| Angle | Predicted (deg) | Reference (deg) | Erreur relative |
|-------|-----------------:|----------------:|----------------:|
| theta12 | 33.4 | 33.44 | 0.001196 |
| theta23 | 49.0 | 49.2 | 0.004065 |
| theta13 | 8.6 | 8.57 | 0.003501 |

Spectre neutrinos :

- m1 = 0.0010 eV
- m2 = 0.0087 eV
- m3 = 0.0500 eV

Splittings :

- delta_m21_sq_ev2 = 7.469e-05
- expected delta_m21_sq_ev2 = 7.42e-05
- delta_m31_sq_ev2 = 0.002499
- expected delta_m31_sq_ev2 = 0.002517

Lecture d'ensemble :

- le sous-ensemble electron5_core reste compatible avec les valeurs de reference
- aucune anomalie numerique ne sort des tolerances du run
- les resultats PMNS sont coherents avec un spectre leger et hierarchique