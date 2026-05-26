# Protocole V21

## Vue d'ensemble

V21 est la couche de resolution du point borderline laisse par V19. L'objectif n'est plus de mesurer uniquement la robustesse globale, mais de montrer que la zone de fragilite est localisee, comprise et utilisable comme point de transition vers une lecture plus stable du pipeline V11-V20.

V21 reunit quatre questions:

- V19 est-il seulement borderline ou deja structurellement resolu ?
- la zone critique est-elle concentree sur un bottleneck unique ?
- le pipeline reste-t-il lisible autour du meilleur profil V18 ?
- la conclusion V21 permet-elle de refermer la zone grise de V19 ?

Il se compose de quatre modules:

- V21-BORDERLINE: lecture directe du point borderline V19.
- V21-RECOVERY: mesure de la marge de recuperation autour du point critique.
- V21-RESOLUTION: synthese de la zone grise et de sa stabilite.
- V21-VERDICT: conclusion finale sur la resolution de V19.

Le wrapper global est `v21borderline_suite`.

## Fichiers a ajouter

- python/scripts/v21borderline_core.py
- python/scripts/v21borderline_check.py
- python/scripts/v21recovery_check.py
- python/scripts/v21resolution_check.py
- python/scripts/v21verdict_check.py
- python/scripts/runv21borderline_suite.py
- python/tests/test_v21borderlinecheck.py
- python/tests/test_v21recoverycheck.py
- python/tests/test_v21resolutioncheck.py
- python/tests/test_v21verdictcheck.py
- python/tests/test_v21borderlinesuite.py

## V21-BORDERLINE

Hypothese testee: le borderline V19 est bien un point de transition localise et non une rupture structurelle.

Point de depart:

- best_profile_V18 = calibration_agressive
- theta_reference = point retenu par V18
- V19 = localement bon mais borderline sur la robustesse globale

Mesures a suivre:

- supported_chain_length
- fragile_layer
- recovery_margin
- bottleneck_flag
- classification V19

Regles de classement:

- supported si supported_chain_length = 4 et fragile_layer = none,
- supported-partial si supported_chain_length = 4 mais recovery_margin reste tres faible,
- fragile si supported_chain_length < 4 ou si une couche critique devient fragile.

Resultat attendu:

- une seule zone critique concentree,
- aucune rupture en chaine,
- un borderline clairement delimite.

Verdict attendu: supported ou supported-partial selon la profondeur du borderline.

## V21-RECOVERY

Hypothese testee: la marge de recuperation autour de V19 peut etre quantifiee proprement et reste interpretable.

Questions de test:

- la marge de recuperation est-elle positive ?
- le bottleneck reste-t-il unique ?
- la structure supportee se maintient-elle sur l'ensemble de la chaine ?

Mesures a suivre:

- recovery_margin
- recovery_depth
- bottleneck_flag
- resolution_score
- supported_chain_length

Methode de calcul a implementer:

- reutiliser la lecture V19 de robustesse globale,
- normaliser la marge de recuperation,
- mesurer la profondeur relative du borderline,
- verifier la presence d'un unique point de tension.

Regles de classement:

- supported si la marge est positive, la chaine reste complete et le bottleneck est unique,
- supported-partial si la marge existe mais reste tres faible,
- fragile si la chaine est interrompue.

Resultat attendu:

- une marge faible mais exploitable,
- un vrai point de recuperation,
- une lecture stable du stress local.

Verdict attendu: supported si la recuperation est bien localisee.

## V21-RESOLUTION

Hypothese testee: la synthese V21 permet de refermer la zone grise de V19 sans contredire les couches precedentes.

Questions de test:

- V19-map reste-t-il supporte ?
- V19-sensitivity reste-t-il supporte ?
- V19-robust-global peut-il etre interprete comme borderline resolu ?

Mesures a suivre:

- map_verdict
- sensitivity_verdict
- robust_verdict
- resolution_state
- resolution_confidence

Regles de classement:

- supported si map et sensitivity sont supportes et si le borderline est structurellement localise,
- supported-partial si le borderline est reconnu mais pas entierement referme,
- fragile si une couche V19 cle devient fragile.

Resultat attendu:

- V19 demeure localement bon,
- la zone borderline est isolee,
- la resolution est interpretable comme un point de transition controle.

Verdict attendu: supported si la zone grise est completement localisee.

## V21-VERDICT

Hypothese testee: la couche V21 permet-elle de conclure que la zone borderline de V19 est resolue au niveau meta-analyse ?

Classification visee:

- resolu
- partiellement_resolu
- fragile

Regle d'agregation finale:

- resolu si V21-BORDERLINE est supported, V21-RECOVERY est supported, et V21-RESOLUTION est supported,
- partiellement_resolu si la zone est identifiee mais que la marge reste tres faible,
- fragile si la chaine V19 montre une rupture ou une couche critique fragile.

Sortie finale attendue:

- verdict global,
- zone critique principale,
- marge de recuperation,
- niveau de confiance.

Lecture attendue:

- resolu: la fragilite est localisee et pleinement interpretable,
- partiellement_resolu: la zone est claire mais la marge reste etroite,
- fragile: la chain V19-V20 ne ferme pas le point critique.

Verdict final attendu: supported, supported-partial, or fragile selon la resolution observee.

## Resultats observes

Validation V21 effectuee:

- suite V21 ciblee: 5 tests passes sur 5
- V21-BORDERLINE: supported
- V21-RECOVERY: supported
- V21-RESOLUTION: supported
- V21-VERDICT: supported
- suite v21borderline_suite: total = 4, supported_count = 4, overall_verdict = supported

Chiffres clefs V21:

- supported_chain_length = 4
- recovery_margin = 1.0e-06
- fragile_layer = none
- bottleneck_flag = true
- map_verdict = supported
- sensitivity_verdict = supported
- robust_verdict = borderline
- resolution_state = resolu
- resolution_confidence = haute

Agrégation master observee:

- total = 19
- supported_count = 17
- overall_verdict = partiel
- point fragile principal = V19-ROBUST-GLOBAL

## Suite v21borderline_suite

Resultat attendu:

- suite = v21borderline_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

Items:

- v21_borderline: supported
- v21_recovery: supported
- v21_resolution: supported
- v21_verdict: supported

## Integration dans point_atome_master

V21 s'ajoute comme couche de resolution au-dessus de V20.

Effet attendu:

- le master ne modifie pas le noyau local,
- il gagne une lecture de resolution du point borderline V19,
- il confirme que la fragilite est localisee plutot que structurelle.

Resultat attendu du master:

- total = 19
- supported_count = 17
- overall_verdict = partiel

Lecture attendue:

- V21 ferme la zone grise de lecture,
- V19 reste le point borderline initial,
- le master conserve un verdict partiel tant que V12 reste falsifie.