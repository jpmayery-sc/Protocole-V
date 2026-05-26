# Protocole V22

## Vue d'ensemble

V22 est la couche de recherche qui organise en parallele trois branches complementaires:

- V22-THEORY: formalisation theorique
- V22-EXPERIMENT: confrontation a des donnees reelles
- V22-SIMULATION: extension numerique avancee

Le wrapper global est `v22research_suite`.

L'objectif de V22 est de preparer, classer et exploiter toutes les donnees necessaires pour tester la structure emergente issue de V20, en particulier la combinaison geometrie + torsion + hierarchie.

Le dossier de collecte associe est [V22_sources.md](V22_sources.md).

## Guiding Links

- [V22-THEORY](#v22-theory)
- [V22-VERDICT-THEORY](#v22-verdict-theory)
- [V22-EXPERIMENT](#v22-experiment)
- [V22-SIMULATION](#v22-simulation)
- [Liste complete des donnees](#liste-complete-des-donnees-a-chercher)

## V22-THEORY

Objectif: formaliser la structure emergente revelee par V20, en particulier la geometrie interne, la torsion et l'ordre hierarchique des parametres.

Wrapper: `v22theory_suite`

### 1. V22-GEOMETRY - Formalisation geometrique

Hypothese:
La structure {alpha0, sgeo, satom} definit une metrique interne coherente.

Sources:

- NIST CODATA -> alpha, incertitudes
- NIST ASD -> transitions fines et hyperfines
- SDSS DR17 -> redshifts externes
- DLMF 34.2 -> symboles de Wigner

Champs a extraire:

- alpha_CODATA
- d(alpha)/dt (limites)
- niveaux atomiques (Ei, Ef)
- Delta nu / nu observes
- z_obs astrophysiques
- coefficients Wigner 3j, 6j

Taches:

- Construire la metrique interne
- Tester si alpha0 est un invariant geometrique
- Relier redshifts internes et externes
- Verifier la courbure interne via V20

Sorties:

- geometrymodelok
- metric_formulation
- alpha0invarianttype
- curvature_state

### 2. V22-TORSION-THEORY - Formalisation torsionnelle

Hypothese:
Le couple (p, A_kappa) definit une connexion affine avec torsion.

Sources:

- arXiv hep-th/0103093 -> torsion espace-temps
- ESA XMM-Newton -> spectres X-ray
- NIST ASD -> transitions sensibles au spin
- SDSS DR17 -> anomalies de redshift

Champs a extraire:

- invariants de torsion
- couplages spin-torsion
- spectres X-ray (Fe Kalpha)
- derivees Delta z / Delta p

Taches:

- Construire la connexion torsionnelle
- Relier gravtorsioneff aux invariants theoriques
- Tester le couplage torsion-kappa
- Verifier la stabilite torsionnelle via V20

Sorties:

- torsionmodelok
- torsionconnectionform
- torsioninvarianttype
- torsionstabilitystate

### 3. V22-HIERARCHY-THEORY - Formalisation hierarchique

Hypothese:
La hierarchie revelee en V20 est structurelle, pas accidentelle.

Sources:

- NIST CODATA
- NIST ASD
- SDSS DR17
- DLMF 34.2

Champs a extraire:

- sensibilite spectrale
- sensibilite redshift
- invariants geometriques
- coefficients de couplage internes

Taches:

- Construire le diagramme hierarchique
- Verifier la stabilite du top-2 via V19
- Verifier la coherence avec V20

Sorties:

- hierarchymodelok
- hierarchy_diagram
- role_assignment
- hierarchystabilitystate

### Resultats observes

- Suite `v22theory_suite`: a executer apres collecte complete.
- Geometry: a determiner a partir de V22_sources.md.
- Torsion: a determiner a partir de V22_sources.md.
- Hierarchy: a determiner a partir de V22_sources.md.
- Verdict theorique global: a determiner.

### Priorite de travail

- alpha0 et constantes de reference
- modeles de torsion et couplage spin-torsion
- ordonnancement hierarchique des parametres

## V22-VERDICT-THEORY

Regle d'agregation:

- coherent_theory si geometrymodelok, torsionmodelok et hierarchymodelok sont tous vrais
- partial_theory si un module est partiel
- inconclusive si un module est fragile

Sorties finales:

- theory_verdict
- theory_schema
- key_invariants
- open_questions

Si V22-THEORY est coherent, la branche theorique est valide pour alimenter V22-EXPERIMENT et V22-SIMULATION.

## V22-EXPERIMENT

Objectif: confronter directement les observables du modele (V16 a V21) a des donnees reelles spectroscopiques, astrophysiques et liees a la torsion, en utilisant les sources cadrees dans V22_sources.md.

Wrapper recommande: `v22experiment_suite`.

### 1. V22-EXP-SPECTRO - Spectroscopie

Sources:

- NIST Atomic Spectra Database
- NIST QED / Lamb shift references

Champs a extraire:

- Delta nu / nu mesures
- Delta E mesures
- transitions fines / hyperfines
- corrections Lamb / QED

Taches:

- Comparer deltanuovernu et deltaE du modele aux valeurs NIST
- Verifier la coherence de finecorrectioneff avec les corrections fines et hyperfines

Sorties:

- spectroscopymodelok
- ecarts absolus et relatifs
- verdict_spectro

### 2. V22-EXP-ASTRO - Astrophysique

Sources:

- NED
- SDSS DR17
- XMM-Newton

Champs a extraire:

- redshifts precis des quasars et galaxies
- anomalies de redshift
- spectres et lignes identifiees

Taches:

- Comparer z_obs du modele aux redshifts catalogues
- Chercher des regimes ou un redshift interne pourrait coller a la structure

Sorties:

- astromatchscore
- astroanomalyflag
- verdict_astro

### 3. V22-EXP-TORSION - Torsion observable

Sources:

- arXiv hep-th/0103093
- experiences spin-gravite
- contraintes torsion gravitationnelle

Champs a extraire:

- bornes experimentales sur la torsion
- couplages spin-torsion
- tests de violation de symetrie

Taches:

- Comparer l'ordre de grandeur de gravtorsioneff a ces bornes
- Verifier que la torsion effective reste dans la fenetre autorisee

Sorties:

- torsion_compatibility
- torsionboundsok
- verdict_torsion

### 4. V22-EXP-VERDICT

Aggregation:

- supported si spectro, astro et torsion sont tous supported
- partial si un module est partial
- fragile si un module cle est incompatible

Sorties:

- experiment_verdict
- experiment_confidence
- dominant_constraint

### Resultats observes

- Suite `v22experiment_suite`: `supported`, 4/4.
- Spectroscopie: `delta_nu_over_nu = 2.959818e-05`, `delta_E = 2.400360018e-05`, `fine_correction_eff = 1.9999166666666666`, `spectroscopymodelok = true`.
- Astrophysique: `supported`.
- Torsion observable: `supported`.
- Verdict experimental global: `supported`.

## V22-SIMULATION

Objectif: simuler numeriquement la structure interne (geometrie + torsion + hierarchie) avec des bases Wigner, des metriques internes et des tests de stabilite multi-parametres.

Wrapper: `v22simulation_suite`.

### 1. V22-SIM-WIGNER - Base Wigner / helices internes

Sources:

- DLMF 34 et 34.2
- tables de matrices de Wigner
- representations SU(2), SU(3)

Taches:

- Construire une base interne coherent avec les parametres
- Verifier que les regles de selection et de couplage sont respectees

Sorties:

- wignerbasisok
- selectionrulesok
- spincouplingpattern

### 2. V22-SIM-GEO - Geometrie simulee

Sources:

- metriques internes
- espaces fibres
- connexions avec torsion

Taches:

- Simuler la metrique interne gint avec sgeo et satom
- Rejouer les gradients geometriques
- Verifier la coherence avec alpha0_geometriclink

Sorties:

- geostructureok
- metric_consistency
- gradients et invariants geometriques

### 3. V22-SIM-STABILITY - Stabilite multi-parametres

Sources:

- modeles hierarchiques
- surfaces de stabilite
- systemes multi-parametres

Taches:

- Rejouer une mini-V19/V20 en simulation pure
- Verifier la hierarchie stable, la torsion stable et la robustesse multi-variable

Sorties:

- hierarchy_stable
- torsion_stable
- multivariable_robustness
- dominant_parameter

### 4. V22-SIM-VERDICT

Aggregation:

- supported si Wigner, geometrie et stabilite sont tous supported
- partial si un module est partial
- fragile si un module cle casse la structure

Sorties:

- simulation_verdict
- simulation_confidence
- weakest_block

### Resultats observes

- Suite `v22simulation_suite`: `supported`, 4/4.
- Wigner / helices internes: `supported`, avec regles de selection valides et `wignerbasisok = true`.
- Geometrie simulee: `supported`, avec `geostructureok = true`, `metric_consistency = true`, `geo_gradient = 9.999999999979575e-08`, `atom_gradient = 1.999999999995915e-07`, `alpha0_geometriclink = 999999.9960041972`.
- Stabilite multi-parametres: `supported`, avec `hierarchy_stable = true`, `torsion_stable = true`, `multivariable_robustness = true`, `dominant_parameter = alpha0`.
- Verdict simulation global: `supported`.

## Liste complete des donnees a chercher

### Constantes fondamentales

- alpha (structure fine)
- variations experimentales de alpha
- donnees QED haute precision

### Spectroscopie

- Delta nu / nu mesures
- Delta E mesures
- transitions fines / hyperfines
- corrections Lamb

### Astrophysique

- redshifts precis
- anomalies de redshift
- spectres de quasars
- spectres de galaxies proches

### Torsion gravitationnelle

- contraintes experimentales
- donnees spin-gravite
- modeles Einstein-Cartan
- couplages spin-torsion

### Geometrie interne

- metriques internes
- espaces fibres
- connexions avec torsion
- geometries non riemanniennes

### Hierarchie / stabilite

- surfaces de stabilite
- systemes multi-parametres
- modeles hierarchiques

### Simulation

- matrices de Wigner
- representations SU(2), SU(3)
- donnees de precession interne
- donnees de couplage interne

## Priorites de collecte

### Priorite 1

- alpha de structure fine
- donnees spectroscopiques haute precision
- contraintes experimentales sur la torsion

### Priorite 2

- redshifts astrophysiques fiables
- modeles Einstein-Cartan
- matrices de Wigner et representations SU(2)/SU(3)

### Priorite 3

- donnees de geometrie interne
- hierarchies de parametres
- surfaces de stabilite et systemes multi-parametres

## Dossier de sources

Avant de lancer les tests V22, les donnees doivent etre rassemblees depuis les sources suivantes:

- [NIST Constants](https://physics.nist.gov/cuu/Constants/) pour alpha, les valeurs CODATA 2022 et la bibliographie associee.
- [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database) pour les niveaux d'energie, les longueurs d'onde, les probabilites de transition et les lignes spectrales.
- [NIST Atomic Spectra Database Contents](https://www.nist.gov/pml/atomic-spectra-database-contents) pour les holdings et la structure de la base spectroscopique.
- [NIST Links to selected scientific data](https://physics.nist.gov/cuu/Constants/links.html) pour les renvois de reference autour des constantes fondamentales.
- [NIST DLMF Chapter 34](https://dlmf.nist.gov/34) et [Section 34.2](https://dlmf.nist.gov/34.2) pour les symboles de Wigner et les regles de couplage.
- [NASA/IPAC Extragalactic Database](https://ned.ipac.caltech.edu/) pour les redshifts de galaxies, quasars et objets extragalactiques.
- [SDSS DR17](https://www.sdss4.org/dr17/) pour les catalogues spectroscopiques, les redshifts, les classifications et les value-added catalogs.
- [ESA XMM-Newton](https://www.cosmos.esa.int/web/xmm-newton) pour les jeux de donnees X-ray et les observations astrophysiques complementaires.
- [arXiv hep-th/0103093](https://arxiv.org/abs/hep-th/0103093) pour la synthese de reference sur la torsion espace-temps et les bornes experimentales.

## Format de preparation recommande

Pour chaque donnee a rechercher, preparer:

- source
- domaine
- observable
- unite
- precision
- intervalle d'incertitude
- lien avec V22-THEORY, V22-EXPERIMENT ou V22-SIMULATION

## Prochaine etape

Une fois ces donnees rassemblees, V22 pourra etre formalise en trois branches paralleles:

- V22-THEORY complet
- V22-EXPERIMENT complet
- V22-SIMULATION complet

Et la suite globale sera `v22research_suite`.

## Resultats de validation V22

- V22-THEORY: `supported`.
- V22-EXPERIMENT: `supported`.
- V22-SIMULATION: `supported`.
- Master `point_atome`: `partiel`, avec `supported_count = 20` sur `total = 22`.