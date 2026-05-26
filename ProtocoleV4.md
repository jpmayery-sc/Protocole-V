# Protocole V4

## Objectif

Ce document résume tout ce qui a été mis en place pour le protocole V4, depuis la vérification des CSV de l’article jusqu’à l’intégration complète du nouveau test dans les suites de plus haut niveau.

## Ce qui a été fait

### 1. Vérification des CSV de l’article

J’ai confirmé la présence locale des exports liés à l’article, notamment les CSV bruts Zenodo et les exports MOESM. Les données étaient donc récupérables et exploitables dans le workspace.

### 2. Mise en place du protocole V4

Le premier bloc V4 a été construit autour d’un contrôle de stabilité nucléaire avec les noyaux suivants : H-1, He-4, C-12, O-16, Fe-56, Pb-208 et U-238.

Le protocole calcule maintenant :

- le nombre de masse
- la charge
- le rapport neutron/proton
- la distance à la courbe de stabilité
- le verdict de courbe
- la forme globale, notée cloche quand la courbe est cohérente

Le cœur du protocole est resté compatible avec l’existant, puis a été rendu réutilisable via un stem d’export configurable.

### 3. Nommage explicite du protocole

Pour rendre le V4 plus lisible, un wrapper explicite a été ajouté sous le nom nzstability. Cela permet de distinguer clairement la logique V4 du fichier historique h_fe_pb_check sans dupliquer le calcul.

### 4. Intégration dans les suites

Le nouveau protocole a ensuite été propagé dans les niveaux d’agrégation existants :

- atom_basics
- point_atome_protocol
- point_atome_master
- s_law
- experience4_global

Cette hiérarchie permet de valider le nouveau contrôle à la fois localement et dans les couches supérieures.

## Hiérarchie finale

1. h_fe_pb_check
2. nzstability_check
3. run_nzstability_suite
4. run_atom_basics_suite
5. run_point_atome_protocol_suite
6. run_point_atome_master_suite
7. run_s_law_suite
8. run_experience4_global_suite

## Fichiers ajoutés ou modifiés

- [python/scripts/h_fe_pb_check.py](python/scripts/h_fe_pb_check.py)
- [python/scripts/nzstability_check.py](python/scripts/nzstability_check.py)
- [python/scripts/run_nzstability_suite.py](python/scripts/run_nzstability_suite.py)
- [python/scripts/run_atom_basics_suite.py](python/scripts/run_atom_basics_suite.py)
- [python/scripts/run_point_atome_protocol_suite.py](python/scripts/run_point_atome_protocol_suite.py)
- [python/scripts/run_point_atome_master_suite.py](python/scripts/run_point_atome_master_suite.py)
- [python/scripts/run_s_law_suite.py](python/scripts/run_s_law_suite.py)
- [python/scripts/run_experience4_global_suite.py](python/scripts/run_experience4_global_suite.py)
- [python/tests/test_h_fe_pb_check.py](python/tests/test_h_fe_pb_check.py)
- [python/tests/test_nzstability_suite.py](python/tests/test_nzstability_suite.py)
- [python/tests/test_atom_basics_suite.py](python/tests/test_atom_basics_suite.py)
- [python/tests/test_point_atome_protocol_suite.py](python/tests/test_point_atome_protocol_suite.py)
- [python/tests/test_point_atome_master_suite.py](python/tests/test_point_atome_master_suite.py)
- [python/tests/test_s_law_suite.py](python/tests/test_s_law_suite.py)
- [python/tests/test_experience4_global_suite.py](python/tests/test_experience4_global_suite.py)

## Tests et résultats

### Détail chiffré par test

#### `test_h_fe_pb_check.py`

Ce test valide le noyau historique du protocole V4. Les quatre critères de base passent: `minimal_ok = true`, `balance_ok = true`, `heavy_ok = true`, `order_ok = true`. La séquence contrôlée contient 3 noyaux: H-1, Fe-56 et Pb-208.

Les chiffres clés extraits sont les suivants: H-1 a `protons = 1`, `neutrons = 0`, `electrons = 1`, `charge = 0`, `neutron_to_proton = 0.0`, `balance_distance = 1.0`. Fe-56 a `protons = 26`, `neutrons = 30`, `electrons = 26`, `neutron_to_proton = 1.1538461538461537`, `balance_distance = 0.15384615384615374`. Pb-208 a `protons = 82`, `neutrons = 126`, `electrons = 82`, `neutron_to_proton = 1.5365853658536586`, `balance_distance = 0.5365853658536586`. Résultat final: `supported`.

#### `test_nzstability_suite.py`

Ce wrapper explicite reprend le même cœur V4 avec le nom lisible `nzstability`. Le test confirme la courbe de stabilité sur 7 noyaux: H-1, He-4, C-12, O-16, Fe-56, Pb-208 et U-238. Les indicateurs sont tous vrais: `curve_ok = true`, `shape = cloche`, `light_side_ok = true`, `heavy_side_ok = true`, `rising_branch_ok = true`, `falling_branch_ok = true`.

Le pic observé est Fe-56 avec `binding_energy_per_nucleon_mev = 8.7904`, `mass_number = 56`, `charge = 0`, `neutron_to_proton = 1.1538461538461537` et `balance_distance = 0.15384615384615374`. Les autres points marquants sont He-4 à `7.0739`, C-12 à `7.6801`, O-16 à `7.9762`, Pb-208 à `7.8675` et U-238 à `7.5701` MeV par nucléon. Résultat final: `supported`.

#### `test_atom_basics_suite.py`

La suite `atom_basics` agrège 4 contrôles: `neutral_atom`, `iron_rust`, `h_fe_pb` et `nzstability`. Le bilan est `supported_count = 4`, `total = 4`, donc `supported` au niveau de la suite.

Les valeurs retenues pour la doc sont: `neutral_atom = supported`, `iron_rust = supported`, `h_fe_pb = supported`, `nzstability = supported`.

#### `test_point_atome_protocol_suite.py`

La suite protocolaire intermédiaire regroupe 5 blocs: `saturation_magnetic`, `omega_structure`, `heavy_border`, `atom_basics` et `regime_physics`. Le bilan global est `supported_count = 5`, `total = 5`, donc `supported`.

Les sous-résultats chiffrés sont: `saturation_magnetic = conforme strict`, `omega_structure = supported`, `heavy_border = supported`, `atom_basics = supported`, `regime_physics = supported`. À l’intérieur de `regime_physics`, les 5 sous-tests `atomique`, `metal`, `lanthanide`, `dense` et `flow` sont tous `supported`.

#### `test_point_atome_master_suite.py`

La suite master de `point_atome` agrège 5 blocs: `point_atome_protocol`, `atom_basics`, `d1d4`, `electron5_core` et `electron5_extended`. Le bilan est `supported_count = 5`, `total = 5`, donc `supported`.

Les cinq entrées sont toutes au verdict `supported`. Ce test sert surtout de contrôle de propagation: il confirme que le bloc V4 remonte bien jusqu’au niveau master sans casser les autres branches.

#### `test_s_law_suite.py`

La suite `s_law_master` regroupe 10 éléments au total, avec `supported_count = 8`, `support_total = 8`, `falsifier_ok = 2`, `falsifier_total = 2`. Le verdict global reste `supported`.

Les 8 éléments de support sont: `screening_law_saturation`, `radius_predictivity`, `fine_variation_equivalence`, `regime_physics`, `alpha_phase_observable`, `point_atome_master`, `lanthanide_internal_residual` et `heavy_border`. Les 2 falsificateurs sont: `family_l_slope` et `alpha_constant`, tous les deux au verdict `falsifie`.

#### `test_experience4_global_suite.py`

La suite globale finale reprend 4 blocs: `atom_basics`, `point_atome_protocol`, `point_atome_master` et `s_law_master`. Le bilan est `supported_count = 4`, `total = 4`, donc `supported`.

Cette étape confirme que toute la chaîne V4 est cohérente de bout en bout, du contrôle atomique de base jusqu’au résumé global.

### Synthèse d’exécution

- python -m pytest python/tests/test_h_fe_pb_check.py -q → 2 passed
- python -m pytest python/tests/test_nzstability_suite.py -q → 2 passed
- python -m pytest python/tests/test_atom_basics_suite.py -q → 2 passed
- python -m pytest python/tests/test_point_atome_protocol_suite.py -q → 2 passed
- python -m pytest python/tests/test_point_atome_master_suite.py -q → 2 passed
- python -m pytest python/tests/test_s_law_suite.py -q → 2 passed
- python -m pytest python/tests/test_experience4_global_suite.py -q → 2 passed

### Validation globale

- python -m pytest python/tests/test_h_fe_pb_check.py python/tests/test_nzstability_suite.py python/tests/test_atom_basics_suite.py python/tests/test_point_atome_protocol_suite.py python/tests/test_point_atome_master_suite.py python/tests/test_s_law_suite.py python/tests/test_experience4_global_suite.py -q → 14 passed in 46.90s

## Résultat final

Le protocole V4 est maintenant complet, nommé explicitement, intégré dans les suites supérieures et validé par les tests. Le point important est que la chaîne complète fonctionne du test de base jusqu’au résumé global.
