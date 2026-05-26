# Protocole V19

## Vue d'ensemble

V19 est la couche de meta-analyse globale du pipeline V11-V18. L'objectif n'est plus de changer la physique locale, mais d'evaluer si le pipeline complet est seulement acceptable ou vraiment solide sur l'ensemble de son espace de calibration.

V19 reunit quatre questions:

- le pipeline reste-t-il bon dans un voisinage du meilleur profil V18 ?
- quels parametres pilotent le plus fortement le score global ?
- y a-t-il des goulets d'etranglement de robustesse entre les couches ?
- la solution V11-V18 est-elle localement bonne ou globalement robuste ?

Il se compose de quatre modules:

- V19-MAP: cartographie locale autour du meilleur profil V18.
- V19-SENSITIVITY: analyse de sensibilite multi-parametres.
- V19-ROBUST-GLOBAL: robustesse globale du pipeline.
- V19-VERDICT: conclusion meta-calibree.

Le wrapper global est `v19metacalibration_suite`.

## Fichiers a ajouter

- python/scripts/v19metacalibration_core.py
- python/scripts/v19map_check.py
- python/scripts/v19sensitivity_check.py
- python/scripts/v19robustglobal_check.py
- python/scripts/v19verdict_check.py
- python/scripts/runv19metacalibration_suite.py
- python/tests/test_v19mapcheck.py
- python/tests/test_v19sensitivitycheck.py
- python/tests/test_v19robustglobalcheck.py
- python/tests/test_v19verdictcheck.py
- python/tests/test_v19metacalibrationsuite.py

## V19-MAP

Hypothese testee: un petit voisinage autour du profil V18 agressif permet de cartographier une zone de stabilite exploitable.

Point de depart:

- best_profile_V18 = calibration_agressive
- theta_reference = point retenu par V18

Protocole de balayage a implementer:

- utiliser theta_reference comme centre du voisinage,
- sonder chaque parametre de facon uniaxiale, un a la fois,
- garder tous les autres parametres fixes au centre,
- tester trois points par axe: centre, bas, haut.

Offsets exacts a appliquer autour de theta_reference:

- alpha0: pas de variation locale dans V19-MAP, valeur de reference seulement,
- s_geo: -0.0005 et +0.0005,
- s_atom: -0.0005 et +0.0005,
- A_kappa: -1.0e-6 et +1.0e-6,
- p: -0.005 et +0.005.

Les valeurs centre/bas/haut sont donc:

- centre = theta_reference,
- bas = theta_reference + delta_min,
- haut = theta_reference + delta_max.

Variables a sonder:

- alpha0
- s_geo
- s_atom
- A_kappa
- p

Mesures a suivre:

- deviation_score
- deviation_class
- internal_balance
- stability_state

Regles de classement:

- supported si comparison_ok = true, all_in_bounds = true, all_signs_ok = true, et deviation_score <= baseline_deviation_score + 0.002,
- supported-partial si comparison_ok = true mais deviation_score > baseline_deviation_score + 0.002,
- fragile si comparison_ok = false.

Resultat attendu:

- une zone centrale reste supportee,
- les bords du voisinage mettent en evidence les zones de decrochage,
- la carte distingue les zones confortables et les zones dangereuses.

Verdict attendu: supported ou supported-partial selon l'etendue de la zone stable.

## V19-SENSITIVITY

Hypothese testee: tous les parametres du noyau V15-V18 n'ont pas le meme poids dans le score global.

Derivees conceptuelles a estimer:

- d(deviation_score)/d(alpha0)
- d(deviation_score)/d(s_geo)
- d(deviation_score)/d(s_atom)
- d(deviation_score)/d(A_kappa)
- d(deviation_score)/d(p)

Methode de calcul a implementer:

- utiliser une difference finie centree,
- reevaluer le score en perturbant un seul parametre a la fois,
- conserver le meme theta_reference que V19-MAP,
- utiliser les memes pas locaux que V19-MAP,
- normaliser chaque derivee par le pas applique.

Formule cible pour chaque parametre x:

$$
\partial_x \approx \frac{score(x + \Delta x) - score(x - \Delta x)}{2\,\Delta x}
$$

Tri de sensibilite a produire:

- dominant si |partial_x| est dans le top 1,
- secondaire si |partial_x| est dans le top 2 ou top 3,
- faible si |partial_x| est dans le bas du classement.

Sorties attendues:

- un ranking des parametres les plus influents,
- une identification des parametres neutres ou secondaires,
- une lecture simple de la rigidite du pipeline.

Resultat attendu:

- au moins un parametre dominant,
- au moins un parametre secondaire,
- un score de sensibilite global interpretable,
- un classement stable si deux executions successives gardent le meme top-2.

Seuils d'acceptation:

- supported si le ranking top-2 est stable et la derivee dominante depasse la derivee mediane d'au moins 20%,
- supported-partial si le ranking existe mais reste trop serre,
- fragile si aucun parametre ne se detache franchement.

Verdict attendu: supported si le ranking est stable et lisible.

## V19-ROBUST-GLOBAL

Hypothese testee: un petit stress local sur V18 ne doit pas faire tomber V17, V16 ou V15.

Questions de test:

- si V18 bouge legerement, V17 reste-t-il supporte ?
- si V16 est perturbe, V15 conserve-t-il son noyau final ?
- existe-t-il une couche fragile qui casse la chaine ?

Mesures a suivre:

- supported_chain_length
- fragile_layer
- recovery_margin
- bottleneck_flag

Stress a appliquer:

- V18: appliquer les offsets V19-MAP sur theta_reference,
- V17: verifier que le verdict reste au moins supported,
- V16: verifier que external_ok et internal_ok restent vrais,
- V15: verifier que le noyau final reste supporte.

Definition des indicateurs:

- supported_chain_length: nombre de couches consecutives encore supportees en remontant depuis V18,
- fragile_layer: premiere couche qui passe a marginal, degraded ou falsified,
- recovery_margin: delta maximal admissible avant la premiere degradation,
- bottleneck_flag: vrai si une seule couche concentre la perte de robustesse.

Classes attendues:

- robust
- borderline
- fragile

Regles de verdict:

- robust si supported_chain_length = 4 et recovery_margin >= 0.002,
- borderline si supported_chain_length = 4 mais recovery_margin < 0.002,
- fragile si supported_chain_length < 4 ou si une couche critique tombe a falsified.

Resultat attendu:

- la chain V15-V18 reste majoritairement supportee,
- aucune couche critique ne doit devenir un point de rupture systematique,
- les goulets d'etranglement doivent etre identifies explicitement s'ils existent.

Verdict attendu: supported si le pipeline supporte les perturbations locales; partiel si une couche precise reste fragile.

## V19-VERDICT

Hypothese testee: le pipeline V11-V18 est-il globalement robuste ou seulement localement bon ?

Classification visee:

- localement bon
- globalement solide
- trop tendu
- fragile

Règle d'agrégation finale:

- globalement solide si V19-MAP est supported, V19-SENSITIVITY est supported, et V19-ROBUST-GLOBAL est robust,
- localement bon si V19-MAP est supported mais V19-ROBUST-GLOBAL est borderline,
- trop tendu si V19-MAP est supported-partial ou si la sensibilite est stable mais la marge est faible,
- fragile si V19-ROBUST-GLOBAL est fragile ou si la chaine supportee est rompue.

Sortie finale attendue:

- verdict global,
- couche critique principale,
- marge de manœuvre restante,
- niveau de confiance metrologique.

Lecture attendue:

- localement bon: le point calibre reste correct mais le voisinage est etroit.
- globalement solide: la zone stable reste large et la sensibilite est maitrisable.
- trop tendu: la solution marche, mais la marge est faible.
- fragile: le pipeline depend trop fortement d'un point de calibration.

Verdict final attendu: supported, supported-partial, or fragile selon la robustesse globale observee.

## Suite v19metacalibration_suite

Resultat attendu:

- suite = v19metacalibration_suite
- total = 4
- supported_count = a mesurer
- overall_verdict = a mesurer

Items:

- v19_map: a mesurer
- v19_sensitivity: a mesurer
- v19_robust_global: a mesurer
- v19_verdict: a mesurer

## Integration dans point_atome_master

V19 s'ajoute comme couche de meta-analyse au-dessus de V18.

Effet attendu:

- le master ne change pas la physique locale,
- il gagne une lecture de robustesse globale,
- il permet de separer un bon point de calibration d'un pipeline vraiment solide.

Resultat attendu du master:

- total = a mettre a jour apres integration,
- supported_count = a mettre a jour apres integration,
- overall_verdict = a determiner apres execution.

## Bilan attendu

V19 ne cherche pas a ajuster encore les equations locales. Elle sert a repondre a une question plus large:

- le pipeline V11-V18 est-il stable, lisible et robuste, ou simplement bien calibre au point courant ?

Critere de confiance metrologique:

- haute si les trois modules techniques sont supportes,
- moyenne si un seul module est borderline,
- faible si deux modules ou plus sont borderline ou fragiles.

Conclusion courte:

- V19 est une couche de meta-analyse globale.
- V19 mesure la sensibilite, la robustesse et la marge de manœuvre.
- V19 doit dire si le pipeline est globalement solide ou seulement localement bon.