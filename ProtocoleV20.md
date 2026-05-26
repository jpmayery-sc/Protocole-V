# Protocole V20

## Vue d'ensemble

V20 est la couche de recherche hierarchique finale du pipeline V11-V19. L'objectif n'est plus de recalibrer le noyau local, mais de verifier si la structure reduite V15-V19 presente une coherence de niveau recherche, stable sur trois axes: geometrie, torsion et hierarchie.

V20 reunit quatre questions:

- la structure V18-V19 reste-t-elle lisible autour du meilleur profil V18 ?
- quels axes dominent la lecture globale du noyau reduit ?
- la torsion et la geometrie restent-elles compatibles avec le verrouillage V15 ?
- la hierarchie des parametres confirme-t-elle une structure coherente et exploitable ?

Il se compose de quatre modules:

- V20-GEO: lecture geometrique locale autour du profil de reference.
- V20-TORSION: lecture de la torsion gravitationnelle effective.
- V20-HIERARCHY: lecture de l'ordre hierarchique des parametres.
- V20-VERDICT: conclusion de recherche et de coherence globale.

Le wrapper global est `v20research_suite`.

## Fichiers a ajouter

- python/scripts/v20research_core.py
- python/scripts/v20geo_check.py
- python/scripts/v20torsion_check.py
- python/scripts/v20hierarchy_check.py
- python/scripts/v20verdict_check.py
- python/scripts/runv20research_suite.py
- python/tests/test_v20geocheck.py
- python/tests/test_v20torsioncheck.py
- python/tests/test_v20hierarchycheck.py
- python/tests/test_v20verdictcheck.py
- python/tests/test_v20researchsuite.py

## V20-GEO

Hypothese testee: la geometrie locale autour du meilleur profil V18 conserve une structure stable et interpretable.

Point de depart:

- best_profile_V18 = calibration_agressive
- theta_reference = point retenu par V18

Protocole de balayage a implementer:

- utiliser theta_reference comme centre du voisinage,
- sonder un sous-ensemble compact des axes de structure,
- garder les autres parametres fixes au centre,
- tester les perturbations locales autour du profil de reference.

Variables a sonder:

- alpha0
- s_geo
- s_atom
- A_kappa
- p

Mesures a suivre:

- geo_gradient
- atom_gradient
- mod_geo_gradient
- mod_atom_gradient
- canal_gradient
- alpha0_geometriclink
- curvature_indicator
- metric_consistency
- geostructureok

Regles de classement:

- supported si metric_consistency = true, geostructureok = true, et curvature_indicator <= 1.0e-4,
- supported-partial si geostructureok = true mais curvature_indicator reste au-dessus du seuil,
- fragile si geostructureok = false.

Resultat attendu:

- une structure geometrique lisible autour du meilleur profil,
- une liaison forte entre alpha0 et la dynamique gravitationnelle effective,
- une courbure locale faible ou controllee.

Verdict attendu: supported ou supported-partial selon la courbure locale observee.

## V20-TORSION

Hypothese testee: la torsion effective reste stable sous perturbation locale du noyau reduit.

Questions de test:

- la torsion effective reste-t-elle non nulle et mesurable ?
- le couplage en A_kappa reste-t-il lisible ?
- la derivation par rapport a p garde-t-elle une signature nette ?

Mesures a suivre:

- torsion_strength
- torsion_p_derivative
- torsion_kappa_coupling
- torsion_stability
- affine_signature
- canal_coupling

Stress a appliquer:

- p: perturbation locale symetrique,
- A_kappa: perturbation locale symetrique,
- lecture du canal: maintien du centre de reference.

Definition des indicateurs:

- torsion_strength: amplitude absolue de la torsion effective au centre,
- torsion_p_derivative: sensibilite locale de la torsion a p,
- torsion_kappa_coupling: sensibilite locale de la torsion a A_kappa,
- torsion_stability: vrai si la variation locale reste tres faible,
- affine_signature: signe des derivees locales par axe.

Classes attendues:

- supported
- supported-partial
- fragile

Regles de verdict:

- supported si torsion_stability = true et si les deux derivees principales restent non nulles,
- supported-partial si la torsion reste presente mais qu'une partie du couplage est limitee,
- fragile si la torsion devient trop faible ou incoherente.

Resultat attendu:

- une torsion effective presente et interpretable,
- un couplage A_kappa lisible,
- une signature affine non triviale.

Verdict attendu: supported si la torsion reste stable et structuree.

## V20-HIERARCHY

Hypothese testee: le classement des parametres du noyau reduit confirme une hierarchie stable et coherente.

Questions de test:

- quel parametre domine le plus fortement le classement ?
- les parametres metriques s_geo et s_atom restent-ils le couple de base ?
- p et A_kappa gardent-ils leur role de torsion et de couplage ?

Mesures a suivre:

- ranking
- dominant_parameter
- metric_parameters
- torsion_parameter
- coupling_parameter
- stable_hierarchy

Methode de calcul a implementer:

- reutiliser l'analyse de sensibilite V19,
- ordonner les parametres selon la derivee absolue,
- comparer la stabilite du top-2,
- extraire le role fonctionnel de chaque axe.

Regles de classement:

- supported si la hierarchie est stable et si le rang dominant reste lisible,
- supported-partial si la hiérarchie existe mais reste plus serree,
- fragile si aucun axe ne se detache franchement.

Resultat attendu:

- alpha0 comme ancre dominante de la hierarchie,
- s_geo et s_atom comme couple metrique,
- p comme axe torsion,
- A_kappa comme axe de couplage.

Verdict attendu: supported si la hierarchie reste stable et interpretable.

## V20-VERDICT

Hypothese testee: la couche de recherche V20 confirme-t-elle une coherence globale du noyau reduit ?

Classification visee:

- coherent
- emergent
- fragile

Regle d'agregation finale:

- coherent si V20-GEO est supported, V20-TORSION est supported, et V20-HIERARCHY est supported,
- emergent si deux modules sont supported et qu'un module reste supported-partial,
- fragile si un module central tombe a fragile.

Sortie finale attendue:

- verdict global,
- structure detectee,
- niveau de confiance,
- zone de recherche prioritaire.

Lecture attendue:

- coherent: la structure reduite est stable et la lecture hierarchique est nette,
- emergent: la structure est presente mais une partie de la lecture reste a renforcer,
- fragile: la couche de recherche depend trop d'un point local.

Verdict final attendu: supported, supported-partial, or fragile selon la coherence globale observee.

## Resultats observes

Validation V20 effectuee:

- suite V20 ciblée: 9 tests passes sur 9
- V20-GEO: supported
- V20-TORSION: supported
- V20-HIERARCHY: supported
- V20-VERDICT: supported
- suite v20research_suite: total = 4, supported_count = 4, overall_verdict = supported

Chiffres clefs V20:

- geo_gradient = 9.999999999979575e-08
- atom_gradient = 1.999999999995915e-07
- mod_geo_gradient = 5.999999999996216e-08
- mod_atom_gradient = 5.999999999996216e-08
- alpha0_geometriclink = 999999.9960041972
- curvature_indicator = 0.0
- torsion_strength = 0.00011999000000000001
- torsion_kappa_coupling = 5.999999999996216e-08
- torsion_stability = true
- dominant_parameter = alpha0
- metric_parameters = s_geo, s_atom
- stable_hierarchy = true
- verdict_global = supported
- structure_detectee = coherente
- niveau_de_confiance = haute

Agrégation master observee:

- total = 18
- supported_count = 16
- overall_verdict = partiel
- point fragile principal = V19-ROBUST-GLOBAL

## Suite v20research_suite

Resultat attendu:

- suite = v20research_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

Items:

- v20_geo: supported
- v20_torsion: supported
- v20_hierarchy: supported
- v20_verdict: supported

## Integration dans point_atome_master

V20 s'ajoute comme couche de recherche au-dessus de V19.

Effet attendu:

- le master ne change pas le noyau local,
- il gagne une lecture de coherence hierarchique,
- il distingue un pipeline seulement partiellement robuste d'une structure de recherche coherente.

Resultat attendu du master:

- total = 18
- supported_count = 16
- overall_verdict = partiel

Lecture attendue:

- V20 renforce la structure globale,
- V19 reste le point de fragilite localise,
- le master conserve un verdict partiel tant que V19 reste borderline.

Le prochain travail logique est une extension V21 centrée sur la résolution de la zone borderline de V19