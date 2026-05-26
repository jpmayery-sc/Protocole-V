# V41 - ANALYSE DES SYMETRIES DU LAGRANGIEN GEOMETRIQUE EFFECTIF

Version : 0.1

Protocole precedent : [ProtocoleV40.md](ProtocoleV40.md)

Wrapper global suggere :
- [python/scripts/runv41symmetries_suite.py](python/scripts/runv41symmetries_suite.py)

Modules :

- V41-SETUP - Rappel du modele effectif (V40)
- V41-CONTINUOUS - Symetries continues (U(1), SU(2), diff, etc.)
- V41-DISCRETE - Symetries discretes (parites, Z2, etc.)
- V41-GEOMETRIC - Symetries propres a K/T/Y et D1/D2
- V41-CONSERVED - Courants et charges conserves
- V41-SYNTHESIS - Lecture physique et verdict global

## 0. Objectif

Identifier et classifier les symetries du lagrangien effectif extrait en V40 :

- symetries de jauge heritees du SM (traitees ici de facon effective)
- symetries geometriques associees a K, T, Y
- symetries discretes eventuelles (Z2, parites internes)
- consequences en termes de courants conserves et de stabilite du modele

V41 ne modifie pas le modele : il le lit structurellement.

## 1. V41-SETUP - RAPPEL DU MODELE EFFECTIF

On part du lagrangien V40 :

    L_eff = L_GR + L_K + L_Sent + L_mix

avec :
- L_K : secteur geometrique K/T
- L_Sent : dynamique de Y (Sent(Y))
- L_mix : couplages faibles K_bg, Y aux secteurs matiere / cosmologie

Entrees :
- effective_lagrangian (V40)
- extracted_parameters (V40)

Sorties :
- lagrangian_parsed
- field_content
- interaction_terms
- setup_ok
- verdict

## 2. V41-CONTINUOUS - SYMETRIES CONTINUES

### 2.1 Diffeomorphismes

Test :
- invariance de L_eff sous difféomorphismes (structure sqrt(-g) R + champs scalaires)

### 2.2 Symetries internes effectives

On teste l'existence de rotations continues dans l'espace (K, T) :

    (K, T) -> R(theta) . (K, T)

et d'eventuelles symetries de phase sur Y si L_Sent le permet.

Sorties :
- diff_invariance_ok
- KT_rotation_symmetry (true/false)
- internal_U1_Y (true/false)
- continuous_symmetry_summary
- verdict

## 3. V41-DISCRETE - SYMETRIES DISCRETES

### 3.1 Z2 sur Y

Test d'une symetrie eventuelle :

    Y -> -Y

et impact sur L_Sent et L_mix.

### 3.2 Z2 sur K/T

Test :

    (K, T) -> (-K, -T)

et verification de l'invariance de L_K + L_mix.

Sorties :
- Z2_Y_ok
- Z2_KT_ok
- discrete_symmetry_summary
- verdict

## 4. V41-GEOMETRIC - SYMETRIES PROPRES A K/T/Y ET D1/D2

### 4.1 Symetrie de coherence D1/D2

On teste si la dynamique de Y (Sent(Y)) est compatible avec une symetrie de type :

    Y -> Y + const

ou

    Y -> Y_inf + (Y - Y_inf)

et si cette transformation laisse la forme de L_Sent stable.

### 4.2 Symetries de reechelonnage

Test de reechelonnages :

    K -> lambda K
    T -> lambda T
    Y -> Y

et impact sur les couplages (xi, eta, etc.).

Sorties :
- D1D2_symmetry_ok
- rescaling_symmetry_ok
- geometric_symmetry_summary
- verdict

## 5. V41-CONSERVED - COURANTS ET CHARGES

### 5.1 Courants de Noether

A partir des symetries continues identifiees, extraction formelle des courants :

    J^mu_i  (un par symetrie continue independante)

### 5.2 Interpretation physique

- existence ou non d'une quantite conservee associee a Y
- role de K/T dans la conservation effective (par ex. charge geometrique)

Sorties :
- noether_currents
- conserved_quantities
- conservation_ok
- verdict

## 6. V41-SYNTHESIS - LECTURE PHYSIQUE FINALE

### 6.1 Objectif

Resumer :

- quelles symetries sont reellement presentes
- lesquelles sont approximatives / brisees
- quelles charges ou structures sont protegees
- ce que cela implique pour la robustesse du modele

### 6.2 Sorties attendues

- continuous_symmetry_summary
- discrete_symmetry_summary
- geometric_symmetry_summary
- conserved_quantities_summary
- symmetry_structure_ok
- v41_global_verdict

## 7. Criteres de verdict

supported :
- structure de symetries claire
- aucune contradiction interne
- au moins une symetrie geometrique non triviale (K/T/Y ou D1/D2)
- coherence avec V40

partially_supported :
- symetries presentes mais partiellement brisees de facon controlee

rejected :
- contradictions internes (symetries supposees mais non tenues)
- structure de symetries incompatible avec le lagrangien V40

## 8. RESULTATS OBSERVES

Suite executee : v41symmetries_suite

Horodatage : 20260519-155358Z

Chiffres globaux :

- v41_global_verdict : supported
- supported_count : 6/6
- source_v40_supported : true
- symmetry_structure_ok : true

Fichiers generes :

- results/result-analyse/v41_symmetry_analysis/v41setup_check_20260519-155356Z.json
- results/result-analyse/v41_symmetry_analysis/v41continuous_check_20260519-155356Z.json
- results/result-analyse/v41_symmetry_analysis/v41discrete_check_20260519-155357Z.json
- results/result-analyse/v41_symmetry_analysis/v41geometric_check_20260519-155357Z.json
- results/result-analyse/v41_symmetry_analysis/v41conserved_check_20260519-155357Z.json
- results/result-analyse/v41_symmetry_analysis/v41synthesis_check_20260519-155358Z.json
- results/result-analyse/v41symmetries_suite_summary_20260519-155358Z.json

Points saillants observes :

- source_v40_timestamp : 20260519-154103Z
- diff_invariance_ok : true
- KT_rotation_symmetry : false
- internal_U1_Y : false
- Z2_Y_ok : false
- Z2_KT_ok : false
- D1D2_symmetry_ok : true
- rescaling_symmetry_ok : true
- conservation_ok : true
