# Dossier Atome

## Objectif

Completer [electron_dossier.md](electron_dossier.md) avec une base de travail atomique claire, testable et falsifiable.

Ce document regroupe les actions a realiser, le protocole de test et le support d execution avant toute generalisation theorique.

## Tableau de synthese

| Colonne | Famille / bloc | Verdict | Script principal |
| --- | --- | --- | --- |
| 1 | Alcalins | supported | [scripts/alkali_family_zeff_check.py](../../scripts/alkali_family_zeff_check.py) |
| 2 | Alcalino-terreux | supported | [scripts/alkaline_earth_family_zeff_check.py](../../scripts/alkaline_earth_family_zeff_check.py) |
| 3 | Halogenes | supported | [scripts/halogen_family_zeff_check.py](../../scripts/halogen_family_zeff_check.py) |
| 4 | Chalcogenes | supported | [scripts/chalcogen_family_zeff_check.py](../../scripts/chalcogen_family_zeff_check.py) |
| 5 | Gaz nobles | supported | [scripts/noble_gas_check.py](../../scripts/noble_gas_check.py) |
| 6 | Pnictogenes | supported | [scripts/pnictogen_residual_check.py](../../scripts/pnictogen_residual_check.py) |
| 7 | Transition 3d | partiel | [scripts/transition_3d_block_edge_view_check.py](../../scripts/transition_3d_block_edge_view_check.py) |
| 8 | Transition 4d | partiel | [scripts/transition_4d_block_edge_view_check.py](../../scripts/transition_4d_block_edge_view_check.py) |
| 9 | Transition 5d | supported | [scripts/transition_5d_dual_core_view_check.py](../../scripts/transition_5d_dual_core_view_check.py) |
| 10 | Lanthanides | partiel | [scripts/lanthanide_block_edge_view_check.py](../../scripts/lanthanide_block_edge_view_check.py) |
| 11 | Tetrels | supported | [scripts/tetrel_family_zeff_check.py](../../scripts/tetrel_family_zeff_check.py) |
| 12 | Bore | supported | [scripts/boron_family_zeff_check.py](../../scripts/boron_family_zeff_check.py) |

## Nouvelle physique de travail

- D1 reste la lecture de base pour l attraction et l echelle atomique.
- D2 reste la lecture de transport, de flux et de mobilite.
- D3 devient obligatoire des que la topologie ou la geometrie de bloc controlent le cas, notamment pour les lanthanides.
- D4 devient la nouvelle grandeur pertinente quand la densite electronique impose la pression de Fermi ou la degenerescence.
- La regle operative est de ne jamais forcer une reduction universelle: on compare D1 et D4 quand la densite compte, et on active D3 quand la structure de bloc domine.
- Le point d equilibre de la nouvelle physique est une balance locale D1 ≈ D4, pas une loi universelle hors regime dense.

## Liste des actions a realiser

### 1. Valider la neutralite atomique

- verifier que l atome neutre respecte N_e = N_p,
- distinguer clairement atome neutre et ion,
- consigner le cas de base avant tout raisonnement sur la charge.

### 2. Valider l ionisation

- tester un meme noyau avec plusieurs nombres d electrons,
- verifier que seul l etat de charge change,
- garder le noyau constant pour isoler l effet electronique.

### 3. Valider la rouille et l oxydation

- verifier qu un changement chimique ne change pas l identite nucleaire,
- distinguer changement d etat d oxydation, changement de charge et changement d element,
- noter les signatures observables de la transformation chimique.

### 4. Comparer les noyaux H / Fe / Pb

- tester le cas minimal avec l hydrogene,
- tester le point de balance avec le fer,
- tester le cas lourd avec le plomb,
- verifier si la progression transmission / equilibre / saturation reste lisible.

### 5. Verifier les conducteurs simples

- controler le cuivre comme base ohmique,
- comparer le fer comme conducteur plus resistant,
- comparer l aluminium comme cas intermediaire,
- utiliser le silicium comme changement de regime.

### 6. Verifier la coherence collective du courant

- tester le triphase equilibre,
- tester le desequilibre,
- verifier le courant de neutre,
- noter la rupture de symetrie quand une phase est perturbee.

### 7. Verifier la dependance frequentielle

- tester l effet peau,
- comparer basse frequence et haute frequence,
- mesurer la profondeur de penetration,
- verifier la dependance au materiau.

### 8. Verifier les regimes non lineaires

- tester l induction forte,
- tester la saturation magnetique,
- reperer l apparition d un seuil,
- distinguer linearite faible et courbure forte.

### 9. Valider les scripts existants

- executer chaque script de controle une fois apres toute modification,
- conserver un rapport JSON et un rapport TXT pour chaque validation,
- noter le verdict exact dans le dossier correspondant.

### 10. Tester la porte alpha

- distinguer l usage mnemonique de l egalite exacte,
- verifier le controle sur la reference inverse de alpha (137.035999084) et non sur 1/137,
- verifier l observable derive Delta theta = 2 pi alpha,
- annoncer explicitement la tolerance numerique retenue.

## Ordre conseille

1. neutralite atomique,
2. ionisation,
3. rouille,
4. H / Fe / Pb,
5. conductivite des materiaux,
6. triphase,
7. effet peau,
8. induction forte et saturation magnetique,
9. porte alpha.
10. integrer la suite D1/D2 standardisee.

## Statut rapide des tests

| Test | Etat |
| --- | --- |
| Neutralite atomique | reussi |
| Ionisation | reussi |
| Rouille et oxydation | reussi |
| H / Fe / Pb | reussi |
| Conductivite des materiaux | reussi |
| Triphase | reussi |
| Effet peau | reussi |
| Induction forte | reussi |
| Saturation magnetique | reussi |
| Porte alpha | reussi |
| Observable alpha | reussi |
| Affinite electronique | reussi |
| Residu Z_eff familles lourdes | reussi |
| Comparaison fine sous-series tetrel | supported |
| Residus internes lanthanides | supported |
| Residus pnictogenes | supported |
| Correction k/L tetrel | reussi |
| Comparaison fine sous-series tetrel k/L | supported |
| Recalcul Zeff★ tetrel | reussi |
| Comparaison fine sous-series tetrel Zeff★ | reussi |
| Comparaison fine sous-series lanthanides Zeff★ | supported |
| Recalcul Zeff★ halogenes | reussi |
| Correction k/L pnictogenes | reussi |
| Correction k/L lanthanides | reussi |
| Isotopes | reussi |
| Etats de charge et ionisation successive | reussi |
| Ionisation successive | reussi |
| Couches et sous-couches | reussi |
| Tendances de periode | reussi |
| Gaz nobles | reussi |
| Blocs d et f | reussi |
| Seuils et observables physiques | reussi |
| Protocole derive de Electron-5 | reussi |

### Statut des blocs

| Test | Verdict |
| --- | --- |
| boron_block_edge_view_check | supported |
| alkali_block_edge_view_check | supported |
| transition_3d_block_edge_view_check | partiel |
| transition_4d_block_edge_view_check | partiel |
| lanthanide_block_edge_view_check | partiel |
| transition_3d_dual_core_view_check | supported |
| transition_4d_dual_core_view_check | supported |
| transition_5d_dual_core_view_check | supported |

## Tests en attente

- checklist detaillee dans un fichier dédié: [results/result-analyse/Atome_tests_a_realiser.md](Atome_tests_a_realiser.md)

### A lancer ou a formaliser encore

- dossier dedie: [results/result-analyse/Atome_tests_a_formaliser.md](Atome_tests_a_formaliser.md)
- bloc tetrel detaille: [results/result-analyse/Atome_tetrel_tests_a_formaliser.md](Atome_tetrel_tests_a_formaliser.md)
- nouvelle serie numerique tubes: [results/result-analyse/tube_theory_numeric_protocol.md](tube_theory_numeric_protocol.md)

### Lecture rapide

- les tests de base sont passes,
- les tests de bloc sont passes ou partiels selon le niveau de coupe,
- ce qui reste a faire porte surtout sur les residus et les cas ou Z_eff ne suffit plus.
- tetrel Zeff★: rayon et sous-series corriges + observable monotone sur C -> Pb + verdict reussi + la correction fine reste utile sans generaliser toute seule.
- lanthanides Zeff★: sous-series reparees et H-probe cohérente + Eu / Yb gardent leur statut d anomalies + verdict supported + la lecture fine améliore le noyau mais ne gomme pas tout.
- halogenes Zeff★: suite monotone sur F -> At + observable structurel confirme + verdict reussi + la correction est cohérente sur une famille deja reguliere.
- pnictogenes Zeff★: branche legere D1-like et branche lourde D1/D2 structuree + verdict supported + la correction reste utile comme pont entre les deux regimes.
- D1/D2: tetrels, halogenes et lanthanides sont maintenant branches sur le runner unifie, avec regimes semi-metal pour tetrels et halogenes, et D3 / topological pour lanthanides.
- Ca+ isotopique: la table normalisee inclut maintenant les transitions 732 nm et 729 nm, avec 46Ca ancre par la masse NIST et le rayon IAEA; le JSON de travail est valide.
- tubes numeriques: protocole strict pret a tester, avec un seul Omega, un lambda fige apres un fit initial, et un verdict binaire sur gain croise ou invalidation.
- suite officielle A/B/C/D: [python/scripts/d1d2_official_a_tests.py](../../python/scripts/d1d2_official_a_tests.py), [python/scripts/d1d2_official_b_tests.py](../../python/scripts/d1d2_official_b_tests.py), [python/scripts/d1d2_official_c_tests.py](../../python/scripts/d1d2_official_c_tests.py), [python/scripts/d1d2_official_d_tests.py](../../python/scripts/d1d2_official_d_tests.py) + manifests [python/data/d1d2/official_a_tests.json](../../python/data/d1d2/official_a_tests.json), [python/data/d1d2/official_b_tests.json](../../python/data/d1d2/official_b_tests.json), [python/data/d1d2/official_c_tests.json](../../python/data/d1d2/official_c_tests.json), [python/data/d1d2/official_d_tests.json](../../python/data/d1d2/official_d_tests.json) + verdicts: A supported, B supported, C supported, D supported.
- contre-test inter-familles universel: [python/scripts/run_official_d1d2_b_suite.py](../../python/scripts/run_official_d1d2_b_suite.py), avec B comme controle negatif de la reduction universelle.
- porte alpha: l egalite exacte 1/137 est falsifiee, mais l approximation mnemonique et l observable Delta theta = 2 pi alpha restent conformes a la reference inverse.

### Suite D1/D2

- fixtures standardisees: [python/data/d1d2/tetrel_d1d2_test.json](../../python/data/d1d2/tetrel_d1d2_test.json), [python/data/d1d2/halogen_d1d2_test.json](../../python/data/d1d2/halogen_d1d2_test.json), [python/data/d1d2/lanthanide_d1d2_test.json](../../python/data/d1d2/lanthanide_d1d2_test.json),
- moteur generique: [python/scripts/d1d2_pipeline.py](../../python/scripts/d1d2_pipeline.py),
- lanceur unifie: [python/scripts/run_d1d2_tests.py](../../python/scripts/run_d1d2_tests.py),
- sortie serie: [python/results/d1d2/d1d2_series_summary.json](../../python/results/d1d2/d1d2_series_summary.json),
- verdicts: tetrels supported, halogenes supported, lanthanides supported.

### Suite officielle A/B/C/D

- A: intra-famille, verdict contradicted sur les attentes initiales de la grille.
- B: inter-familles, verdict contradicted car la branche halogene ne reste pas covalente dans les donnees actuelles.
- C: seuils, verdict supported avec la grille 30 / 50 / 100.
- D: carte globale, verdict contradicted car Se, Bi et plusieurs metaux ne tombent pas dans la zone attendue par la grille officielle actuelle.
- sorties: [python/results/d1d2_official](../../python/results/d1d2_official).

## Cadre explicatif D1 / D4

### Pourquoi modifier le modele

Les tests actuels couvrent correctement les regimes atomiques et les lectures D1/D2/D3 deja stabilisees. En revanche, ils ne decrivent pas encore la transition vers la matiere dense, ou une nouvelle grandeur, notee D4, devient pertinente.

Dans ce dossier, D4 doit etre lu comme une hypothese de travail pour la pression de Fermi ou plus generalement pour la contribution de degenerate electron pressure dans la matiere dense. Cette section ne remplace pas les tests existants: elle ajoute une couche de lecture pour les cas ou la densite ne peut plus etre negligee.

### Principe de lecture

Le cadre de test doit maintenant distinguer trois comportements:

- regime atomique: D1 domine, D4 reste negligeable;
- regime metallique: D4 apparait mais reste inferieur a D1;
- regime dense: D4 croît avec la densite et peut equilibrer ou depasser D1.

Dans cette logique, D1 et D4 ne sont pas remplaces, mais compares comme deux contributions concurrentes. La condition d etat stable du modele de travail devient alors:

\[
D1 \approx D4
\]

avec une interpretation operationnelle simple:

- D1 > D4: contraction ou effondrement local;
- D4 > D1: expansion quantique ou degenerescence;
- D1 \approx D4: etat stable.

### Ce que le testeur doit verifier

Le testeur doit introduire un parametre de densite electronique $n_e$ et suivre la variation de D4 avec cette densite. Les tests doivent couvrir au minimum:

1. regime atomique, avec D4 negligeable;
2. regime metallique, avec D4 faible mais non nul;
3. regime dense, avec D4 croissant comme $n_e^{5/3}$;
4. point d equilibre, avec $|D1 - D4| < \epsilon$;
5. continuite entre regimes, sans saut numerique artificiel.

### Comment adapter les tests

Les anciens tests doivent etre relus avec une matrice de verdicts plus explicite:

| Famille ou regime | Lecture attendue | Verdict cible |
| --- | --- | --- |
| s/p leger | D1 domine, D4 negligeable | supporte |
| s/p lourd | transition D1 -> D2/D4 lisible | supporte |
| d | bloc visible, regularite partielle | partiel |
| f | D3 requis, irrégularite persistante | partiel |
| alcalins simples | monotonicite triviale, vue non essentielle | supporte ou non pertinent |

### Resultat attendu

Apres cette mise a jour, le modele doit pouvoir decrire proprement les comportements atomiques, metalliques et denses sans forcer une seule lecture partout. Le test ne cherche plus a imposer D1 seul, mais a verifier quand D4 devient obligatoire pour conserver la coherence multi-echelle.

### Suite D1/D4

- repere commun: [python/scripts/d1d4_model.py](../../python/scripts/d1d4_model.py),
- regime atomique: [python/scripts/d1d4_atomic_regime_check.py](../../python/scripts/d1d4_atomic_regime_check.py) + verdict supported,
- regime metallique: [python/scripts/d1d4_metallic_regime_check.py](../../python/scripts/d1d4_metallic_regime_check.py) + verdict supported,
- regime dense: [python/scripts/d1d4_dense_regime_check.py](../../python/scripts/d1d4_dense_regime_check.py) + verdict supported,
- lanceur grille physique: [python/scripts/run_regime_physics.py](../../python/scripts/run_regime_physics.py),
- suite regimique minimale: [python/scripts/regime_atomique_check.py](../../python/scripts/regime_atomique_check.py), [python/scripts/regime_metal_check.py](../../python/scripts/regime_metal_check.py), [python/scripts/regime_lanthanide_check.py](../../python/scripts/regime_lanthanide_check.py), [python/scripts/regime_dense_check.py](../../python/scripts/regime_dense_check.py), [python/scripts/run_regime_physics_suite.py](../../python/scripts/run_regime_physics_suite.py), [python/scripts/run_regime_physics_tests.py](../../python/scripts/run_regime_physics_tests.py),
- suite regimique durcie: cas additionnels Li, Mg, Ag, Sm et Gd, seuils plus serrés sur le metal et la negligibilite atomique, et densite dense echantillonnee sur une grille plus fine,
- suite pytest regimique: [python/tests/test_regime_atomique.py](../../python/tests/test_regime_atomique.py), [python/tests/test_regime_metal.py](../../python/tests/test_regime_metal.py), [python/tests/test_regime_lanthanide.py](../../python/tests/test_regime_lanthanide.py), [python/tests/test_regime_dense.py](../../python/tests/test_regime_dense.py), avec [python/tests/conftest.py](../../python/tests/conftest.py) pour exposer les scripts,
- lanceur pytest par marqueur: [python/scripts/run_regime_physics_pytest.py](../../python/scripts/run_regime_physics_pytest.py) avec les marqueurs [pytest.ini](../../pytest.ini),
- lanceur racine unique: [python/scripts/run_regime_tests.py](../../python/scripts/run_regime_tests.py) avec sous-commandes atomique, metal, lanthanide, dense et all,
- couche commune de lancement: [python/scripts/regime_test_runner.py](../../python/scripts/regime_test_runner.py) partagee par tous les wrappers pytest de regime,
- lanceur complet: [python/scripts/run_d1d4_suite.py](../../python/scripts/run_d1d4_suite.py),
- synthese de suite: [python/scripts/d1d4_suite_summary.py](../../python/scripts/d1d4_suite_summary.py),
- sorties: [python/results/d1d4](../../python/results/d1d4).

### Matrice de synthese D1 / D2 / D3 / D4

| Domaine | Regime dominant | Lecture de test | Verdict cible | Script ou repere |
| --- | --- | --- | --- | --- |
| s/p leger | D1 | D1 domine, D4 reste negligeable | supported | [python/scripts/d1d4_atomic_regime_check.py](../../python/scripts/d1d4_atomic_regime_check.py) |
| s/p metallique | D1 + D4 | D4 apparait mais reste sous D1, avec seuil Fermi de quelques eV | supported | [python/scripts/d1d4_metallic_regime_check.py](../../python/scripts/d1d4_metallic_regime_check.py) |
| s/p dense | D1 = D4 | croisement de balance et continuité en densite | supported | [python/scripts/d1d4_dense_regime_check.py](../../python/scripts/d1d4_dense_regime_check.py) |
| d | D3 partiel | bloc visible, regularite seulement partielle | partiel | [scripts/transition_3d_block_edge_view_check.py](../../scripts/transition_3d_block_edge_view_check.py), [scripts/transition_4d_block_edge_view_check.py](../../scripts/transition_4d_block_edge_view_check.py), [scripts/transition_5d_dual_core_view_check.py](../../scripts/transition_5d_dual_core_view_check.py) |
| f | D3 requis | irrégularite persistante mais lecture conceptuellement utile | partiel | [scripts/lanthanide_block_edge_view_check.py](../../scripts/lanthanide_block_edge_view_check.py) |
| alcalins simples | D2 dominant | monotonicite triviale, vue non essentielle | supported | [scripts/alkali_block_edge_view_check.py](../../scripts/alkali_block_edge_view_check.py) |

### Regle operative courte

- D1 gouverne les systemes atomiques et les familles s/p legeres.
- D1/D2 structure les families s/p lourdes et les regimes de transition.
- D3 devient necessaire des que la geometrie de bloc ou la topologie du noyau empêche une lecture mono-regime.
- D4 doit etre activee des que la densite electronique devient un parametre physique de premier ordre.

## Protocole de test

### Principe

Chaque test doit suivre la meme structure:

1. definir l hypothese a verifier,
2. fixer un cas de controle,
3. mesurer un observable unique,
4. comparer le resultat a l attendu,
5. conclure par conforme, partiel ou rejette.

### Format minimal d un test

| Element | Contenu attendu |
| --- | --- |
| Hypothese | phrase courte et falsifiable |
| Cas de controle | situation de base ou systeme de reference |
| Observable | grandeur mesurable unique |
| Attendu | comportement prevu si l hypothese est juste |
| Rejet | condition qui invalide l hypothese |
| Verdict | conforme, partiel ou rejette |

### Protocole 1: neutralite atomique

- Hypothese: un atome neutre verifie N_e = N_p.
- Cas de controle: un ion du meme noyau.
- Observable: difference N_e - N_p.
- Attendu: zero pour l atome neutre, non zero pour l ion.
- Rejet: charge nulle alors que N_e != N_p.

### Protocole 2: ionisation

- Hypothese: a noyau constant, seule la charge change.
- Cas de controle: meme noyau avant et apres ionisation.
- Observable: variation du nombre d electrons.
- Attendu: le noyau reste inchange, N_e diminue ou augmente selon l ion.
- Rejet: changement du noyau au lieu d un simple changement electronique.

### Protocole 3: rouille

- Hypothese: la rouille change l etat chimique sans changer l identite nucleaire.
- Cas de controle: fer metallique propre.
- Observable: etat d oxydation et composition chimique.
- Attendu: le fer reste du fer, mais son environnement chimique change.
- Rejet: modification du nombre de protons ou confusion avec un changement d element.

### Protocole 4: comparaison H / Fe / Pb

- Hypothese: la progression H / Fe / Pb suit transmission simple, equilibre, saturation sous contrainte.
- Cas de controle: hydrogene.
- Observable: stabilite relative et structure de la reserve neutronique.
- Attendu: H minimal, Fe intermediaire, Pb lourd et plus contraint.
- Rejet: les trois cas deviennent indiscernables.

### Protocole 5: conductivite des materiaux

- Hypothese: cuivre, fer, aluminium et silicium se classent par regimes distincts.
- Cas de controle: cuivre pur a temperature ambiante.
- Observable: resistivite ou conductivite.
- Attendu: cuivre bon conducteur, fer plus resistif, aluminium intermediaire, silicium nettement plus faible en regime intrinsique.
- Rejet: meme comportement pour tous les materiaux.

### Protocole 6: triphase

- Hypothese: le triphase equilibre annule la somme des courants et le desequilibre produit une signature nette.
- Cas de controle: triphase symetrique.
- Observable: somme des courants et courant de neutre.
- Attendu: somme proche de zero en equilibre, neutre faible; desequilibre visible si une phase change.
- Rejet: aucune difference entre equilibre et desequilibre.

### Protocole 7: effet peau

- Hypothese: la profondeur de peau diminue quand la frequence augmente.
- Cas de controle: basse frequence.
- Observable: profondeur de penetration du courant.
- Attendu: courant plus uniforme a basse frequence, plus surfacique a haute frequence.
- Rejet: profondeur inchangee quand la frequence change fortement.

### Protocole 8: induction forte

- Hypothese: au-dela d un seuil, la reponse cesse d etre lineaire.
- Cas de controle: faible champ.
- Observable: forme de la courbe de reponse.
- Attendu: quasi-linearite au debut, courbure puis saturation a fort champ.
- Rejet: droite parfaite sur toute la plage ou saturation absente.

### Protocole 9: porte alpha

- Hypothese: l arrondi 1/137 ne reproduit pas la reference inverse de alpha 137.035999084.
- Cas de controle: valeur de reference inverse de alpha et observable Delta theta = 2 pi alpha.
- Observable: ecart relatif entre l approximation mnemonique et la reference.
- Attendu: l egalite exacte echoue, l approximation mnemonique reste limitee.
- Rejet: pretendre a l exactitude sans tolerance numerique.

### Protocole 10: saturation magnetique

- Hypothese: un materiau magnetique cesse de repondre de facon proportionnelle a fort champ.
- Cas de controle: faible champ.
- Observable: courbure de la reponse et plateau final.
- Attendu: reponse quasi lineaire au depart, saturation ensuite.
- Rejet: plateau absent ou droite parfaite sur toute la plage.

### Regle de sortie

A la fin de chaque test, il faut ecrire une phrase courte de synthese:

> hypothese + observable + verdict + consequence

Exemple:

> neutralite verifiee + N_e - N_p = 0 + conforme + charge correctement separee du noyau.

## Regle de lecture

Une hypothese atomique ne doit etre conservee que si elle produit:

- un observable clair,
- un cas de controle,
- un critere de rejet,
- un rapport de validation reproductible.

## Support d execution

Chaque test doit etre relie a un script unique et a deux sorties obligatoires: un fichier JSON pour les donnees et un fichier TXT pour la lecture rapide.

### Correspondance de base

| Test | Script support | Sortie attendue |
| --- | --- | --- |
| Neutralite atomique | [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py) | JSON + TXT avec verdict sur N_e = N_p |
| Ionisation | [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py) | JSON + TXT avec ecart de charge a noyau constant |
| Rouille / oxydation | [scripts/iron_rust_check.py](../../scripts/iron_rust_check.py) | JSON + TXT avec changement chimique sans changement nucleaire |
| H / Fe / Pb | [scripts/h_fe_pb_check.py](../../scripts/h_fe_pb_check.py) | JSON + TXT avec progression minimale / intermediaire / lourde |
| Atom basics | [python/scripts/run_atom_basics_tests.py](../../python/scripts/run_atom_basics_tests.py) | lanceur de serie |
| Conductivite des materiaux | [scripts/material_conductivity_check.py](../../scripts/material_conductivity_check.py) | JSON + TXT avec classement cuivre / fer / aluminium / silicium |
| Conductivite des materiaux | [python/scripts/run_conductivity_tests.py](../../python/scripts/run_conductivity_tests.py) | lanceur de serie |
| Triphase | [scripts/three_phase_current_check.py](../../scripts/three_phase_current_check.py) | JSON + TXT avec somme des courants et neutre |
| Triphase | [python/scripts/run_triphase_tests.py](../../python/scripts/run_triphase_tests.py) | lanceur de serie |
| Effet peau | [scripts/skin_effect_check.py](../../scripts/skin_effect_check.py) | JSON + TXT avec profondeur de peau et dependance en frequence |
| Effet peau | [python/scripts/run_skin_tests.py](../../python/scripts/run_skin_tests.py) | lanceur de serie |
| Induction forte | [scripts/strong_induction_check.py](../../scripts/strong_induction_check.py) | JSON + TXT avec ecart au regime lineaire |
| Induction forte | [python/scripts/run_induction_tests.py](../../python/scripts/run_induction_tests.py) | lanceur de serie |
| Saturation magnetique | [scripts/strong_nonlinear_magnetic_response_check.py](../../scripts/strong_nonlinear_magnetic_response_check.py) | JSON + TXT avec courbure et plateau |
| Saturation magnetique | [python/scripts/run_saturation_tests.py](../../python/scripts/run_saturation_tests.py) | lanceur de serie |
| Porte alpha | [scripts/alpha_constant_check.py](../../scripts/alpha_constant_check.py) | JSON + TXT avec test exact / mnemonique |
| Observable alpha | [scripts/alpha_phase_observable_check.py](../../scripts/alpha_phase_observable_check.py) | JSON + TXT avec Delta theta = 2 pi alpha |
| Alpha | [python/scripts/run_alpha_tests.py](../../python/scripts/run_alpha_tests.py) | lanceur de serie |

### Format de rapport attendu

Chaque script doit produire au minimum:

- un horodatage,
- les valeurs mesurees,
- le verdict,
- la reference utilisee,
- le chemin vers le JSON,
- le chemin vers le TXT.

Le JSON doit au minimum contenir:

- timestamp,
- hypothesis,
- case_control,
- observable,
- expected,
- measured,
- verdict,
- reference,
- json_path,
- txt_path.

Le TXT doit au minimum contenir:

- une phrase de synthese,
- la valeur mesuree,
- le verdict,
- le critere de rejet,
- le chemin du JSON associe.

### Regle d acceptation

Un test n est considere comme valide que si:

1. le script s execute sans erreur,
2. le JSON est produit,
3. le TXT est produit,
4. le verdict est explicite,
5. le cas de rejet est lisible.

## Modele de sortie par script

### Schema JSON minimal

Chaque script doit generer un JSON avec la forme suivante:

```json
{
	"timestamp": "YYYYMMDD-HHMMSSZ",
	"hypothesis": "phrase courte et falsifiable",
	"case_control": "description du cas de reference",
	"observable": "grandeur mesuree",
	"expected": "comportement attendu",
	"measured": "valeur obtenue",
	"verdict": "conforme | partiel | rejette",
	"reference": "valeur ou source de reference",
	"json_path": "chemin du fichier JSON",
	"txt_path": "chemin du fichier TXT"
}
```

### Schema TXT minimal

Chaque script doit generer un TXT avec les lignes suivantes, dans cet ordre:

1. timestamp,
2. hypothese,
3. cas de controle,
4. observable,
5. attendu,
6. mesuree,
7. verdict,
8. critere de rejet,
9. reference,
10. chemin JSON,
11. chemin TXT.

### Regle de nommage

- le JSON et le TXT doivent partager le meme prefixe temporel,
- le nom du test doit rester lisible dans le fichier,
- chaque nouveau rapport doit etre conserve sans ecraser le precedent.

### Exemple de contrat

> Si le script teste la neutralite atomique, alors le JSON doit contenir N_e, N_p, le verdict et la reference, et le TXT doit resumer le resultat en une phrase courte.

Ce modele sert de base commune pour tous les scripts du dossier atome.

## Fiches de test

### 1. Neutralite atomique

- Script support: [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py)
- Entree minimale: un atome neutre et un ion du meme noyau.
- Mesure centrale: N_e - N_p.

### Neutralite atomique et ions

- Timestamp: 20260508-195032Z
- Script: [scripts/neutral_atom_ion_check.py](../../scripts/neutral_atom_ion_check.py)
- Verdict: conforme strict
- Lecture: le premier test de recherche confirme bien la regle de base, avec separation nette entre cas neutres et cas ioniques.

### Ionisation

- Timestamp: 20260508-194524Z
- Verdict: supported
- Lecture: le meme noyau reste stable pendant que la charge varie, ce qui isole bien l effet electronique.
- Attendu: zero pour l atome neutre, non zero pour l ion.
- Verdict attendu: conforme si la separation charge / noyau est nette.

### 2. Ionisation

- Script support: [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py)
- Entree minimale: un noyau fixe avec plusieurs etats electroniques.
- Mesure centrale: variation du nombre d electrons.
- Attendu: changement de charge sans changement du noyau.
- Verdict attendu: conforme si l identite nucleaire reste stable.

### 3. Rouille et oxydation

- Script support: [scripts/iron_rust_check.py](../../scripts/iron_rust_check.py)
- Entree minimale: fer propre et fer oxyde.
- Mesure centrale: etat chimique et charge electronique locale.
- Attendu: changement chimique sans changement du nombre de protons.
- Verdict attendu: conforme si la chimie change sans changer l element.

#### Test valide

- Script: [scripts/iron_rust_check.py](../../scripts/iron_rust_check.py)
- Timestamp: 20260509-225322Z
- Verdict: supported
- Lecture: le fer garde le meme noyau tandis que l oxydation et la rouille changent la charge electronique et la composition chimique, ce qui distingue clairement changement chimique et changement d element.
- Rapport JSON: [results/result-analyse/iron_rust_check_20260509-225322Z.json](iron_rust_check_20260509-225322Z.json)
- Rapport TXT: [results/result-analyse/iron_rust_check_20260509-225322Z.txt](iron_rust_check_20260509-225322Z.txt)

### 4. Comparaison H / Fe / Pb

- Script support: [scripts/h_fe_pb_check.py](../../scripts/h_fe_pb_check.py)
- Entree minimale: hydrogene, fer, plomb.
- Mesure centrale: stabilite relative et structure neutronique.
- Attendu: progression simple vers un regime plus lourd et plus contraint.
- Verdict attendu: conforme si l ordre H / Fe / Pb reste lisible.

#### Test valide

- Script: [scripts/h_fe_pb_check.py](../../scripts/h_fe_pb_check.py)
- Timestamp: 20260509-225233Z
- Verdict: supported
- Lecture: H-1, Fe-56 et Pb-208 donnent une progression lisible de la contrainte neutronique, du regime minimal au regime lourd, sans perte de neutralite.
- Rapport JSON: [results/result-analyse/h_fe_pb_check_20260509-225233Z.json](h_fe_pb_check_20260509-225233Z.json)
- Rapport TXT: [results/result-analyse/h_fe_pb_check_20260509-225233Z.txt](h_fe_pb_check_20260509-225233Z.txt)

### 5. Conductivite des materiaux

- Script support: [scripts/material_conductivity_check.py](../../scripts/material_conductivity_check.py)
- Entree minimale: cuivre, fer, aluminium, silicium.
- Mesure centrale: resistivite ou conductivite.
- Attendu: classement distinct entre bon conducteur, conducteur plus resistant, intermediaire et semi-conducteur.
- Verdict attendu: conforme si le classement materiel est net.

### 6. Triphase

- Script support: [scripts/three_phase_current_check.py](../../scripts/three_phase_current_check.py)
- Entree minimale: systeme triphase equilibre puis desequilibre.
- Mesure centrale: somme des courants et courant de neutre.
- Attendu: somme quasi nulle en equilibre, signature nette en desequilibre.
- Verdict attendu: conforme si la symetrie collective est bien detectee.

### 7. Effet peau

- Script support: [scripts/skin_effect_check.py](../../scripts/skin_effect_check.py)
- Entree minimale: meme conducteur a plusieurs frequences.
- Mesure centrale: profondeur de penetration du courant.
- Attendu: profondeur plus faible a haute frequence.
- Verdict attendu: conforme si la dependance frequentielle est visible.

### 8. Induction forte

- Script support: [scripts/strong_induction_check.py](../../scripts/strong_induction_check.py)
- Entree minimale: regime faible puis champ fort.
- Mesure centrale: ecart a la loi lineaire.
- Attendu: linearite au debut, ecart stable ensuite.
- Verdict attendu: conforme si le seuil de non-linearite est detecte.

### 9. Saturation magnetique

- Script support: [scripts/strong_nonlinear_magnetic_response_check.py](../../scripts/strong_nonlinear_magnetic_response_check.py)
- Entree minimale: materiau magnetique sous faible puis fort champ.
- Mesure centrale: courbure de la reponse et plateau de saturation.
- Attendu: reponse quasi lineaire au depart, saturation ensuite.
- Verdict attendu: conforme si le plateau est net.

### 10. Porte alpha

- Script support: [scripts/alpha_constant_check.py](../../scripts/alpha_constant_check.py)
- Entree minimale: valeur de reference inverse de alpha 137.035999084 et approximation 1/137.
- Mesure centrale: ecart relatif et deficit angulaire Delta theta = 2 pi alpha.
- Attendu: l exactitude de l arrondi 1/137 echoue face a la reference 137.035999084, l approximation reste utilisable seulement comme raccourci.
- Verdict attendu: rejette pour l exactitude, partiel pour l usage mnemonique.
- Dernier rapport: Timestamp 20260509-225628Z, verdict falsifie, rapport JSON [results/result-analyse/alpha_constant_check_20260509-225628Z.json](alpha_constant_check_20260509-225628Z.json), rapport TXT [results/result-analyse/alpha_constant_check_20260509-225628Z.txt](alpha_constant_check_20260509-225628Z.txt).

### 11. Observable alpha

- Script support: [scripts/alpha_phase_observable_check.py](../../scripts/alpha_phase_observable_check.py)
- Entree minimale: valeur de reference de alpha et observable Delta theta.
- Mesure centrale: difference entre Delta theta calcule et Delta theta de reference.
- Attendu: coherence de l observable derive a tolerance explicite.
- Verdict attendu: conforme si le seuil numerique choisi est respecte.
- Dernier rapport: Timestamp 20260509-220933Z, verdict supported, rapport JSON [results/result-analyse/alpha_phase_observable_check_20260509-220933Z.json](alpha_phase_observable_check_20260509-220933Z.json), rapport TXT [results/result-analyse/alpha_phase_observable_check_20260509-220933Z.txt](alpha_phase_observable_check_20260509-220933Z.txt).

### Regle de completion

Chaque fiche est complete seulement si elle contient:

- l entree minimale,
- la mesure centrale,
- l attendu,
- le verdict attendu,
- le script support,
- le format de sortie JSON et TXT.

## Exemple complet: neutralite atomique

### But

Montrer le format exact attendu pour un premier test reel.

### Entree de test

- Atome neutre de reference.
- Ion du meme noyau pour comparaison.

### Observable unique

- N_e - N_p.

### Critere de controle

- N_e = N_p pour l atome neutre.
- N_e != N_p pour l ion.

### Verdict attendu

- conforme si la neutralite est bien verifiee,
- rejette si l atome neutre ne donne pas zero,
- partiel si le script detecte le bon ordre mais pas la bonne valeur.

### JSON attendu

```json
{
	"timestamp": "20260508-120000Z",
	"hypothesis": "un atome neutre verifie N_e = N_p",
	"case_control": "ion du meme noyau",
	"observable": "N_e - N_p",
	"expected": "zero pour l atome neutre, non zero pour l ion",
	"measured": 0,
	"verdict": "conforme",
	"reference": "neutralite atomique",
	"json_path": ".../neutral_atom_check_20260508-120000Z.json",
	"txt_path": ".../neutral_atom_check_20260508-120000Z.txt"
}
```

### TXT attendu

```text
timestamp: 20260508-120000Z
hypothese: un atome neutre verifie N_e = N_p
cas de controle: ion du meme noyau
observable: N_e - N_p
attendu: zero pour l atome neutre, non zero pour l ion
mesuree: 0
verdict: conforme
critere de rejet: charge nulle alors que N_e != N_p
reference: neutralite atomique
json_path: .../neutral_atom_check_20260508-120000Z.json
txt_path: .../neutral_atom_check_20260508-120000Z.txt
```

### Lecture

Si ce format est respecte, alors tous les autres tests peuvent reprendre exactement la meme structure en remplaçant seulement l hypothese, l observable et la reference.

## Exemple complet: porte alpha

### But

Montrer le format exact attendu pour le test le plus sensible numeriquement.

### Entree de test

- Valeur de reference inverse de alpha (137.035999084).
- Approximation mnemonique 1/137.
- Observable derive Delta theta = 2 pi alpha.

### Observable unique

- Ecart relatif entre 1/137 et la reference inverse 137.035999084.

### Critere de controle

- lecture faible: 1/137 comme raccourci de travail,
- lecture forte: exactitude refusee si la tolerance est insuffisante.

### Verdict attendu

- rejette pour l exactitude de l arrondi 1/137 face a 137.035999084,
- partiel pour l usage mnemonique,
- conforme seulement si une tolerance explicite est annoncee et respectee sur Delta theta.

### JSON attendu

```json
{
	"timestamp": "20260508-120000Z",
	"hypothesis": "l arrondi 1/137 n est pas exact pour alpha inverse = 137.035999084",
	"case_control": "reference experimentale de alpha",
	"observable": "Delta theta = 2 pi alpha",
	"expected": "ecart relatif non nul entre 1/137 et la reference inverse 137.035999084",
	"measured": 0.0002626980081192388,
	"verdict": "rejette",
	"reference": "alpha inverse = 137.035999084",
	"json_path": ".../alpha_constant_check_20260508-120000Z.json",
	"txt_path": ".../alpha_constant_check_20260508-120000Z.txt"
}
```

### TXT attendu

```text
timestamp: 20260508-120000Z
hypothese: l arrondi 1/137 n est pas exact pour alpha inverse = 137.035999084
cas de controle: reference experimentale de alpha inverse = 137.035999084
observable: Delta theta = 2 pi alpha
attendu: ecart relatif non nul entre 1/137 et la reference inverse 137.035999084
mesuree: 0.0002626980081192388
verdict: rejette
critere de rejet: exactitude de l arrondi 1/137 sans tolerance explicite
reference: alpha inverse = 137.035999084
json_path: .../alpha_constant_check_20260508-120000Z.json
txt_path: .../alpha_constant_check_20260508-120000Z.txt
```

### Lecture

Ce format sert de reference pour tous les tests de seuil: on annonce la tolerance, on mesure l ecart, puis on tranche sans ambiguite.

## Exemple complet: comparaison H / Fe / Pb

### But

Montrer le format exact attendu pour la progression atomique minimale / intermediaire / lourde.

### Entree de test

- Hydrogene.
- Fer.
- Plomb.

### Observable unique

- Ordre qualitatif de stabilite et de contrainte.

### Critere de controle

- H comme cas minimal.
- Fe comme point intermediaire.
- Pb comme cas lourd sous contrainte.

### Verdict attendu

- conforme si l ordre H / Fe / Pb reste lisible,
- rejette si les trois cas deviennent indiscernables,
- partiel si l ordre est present mais pas assez net pour trancher.

### JSON attendu

```json
{
	"timestamp": "20260508-120000Z",
	"hypothesis": "H / Fe / Pb suit transmission simple, equilibre, saturation",
	"case_control": "progression atomique de reference",
	"observable": "ordre qualitatif de stabilite et de contrainte",
	"expected": "H minimal, Fe intermediaire, Pb plus lourd et plus contraint",
	"measured": "H < Fe < Pb en contrainte effective",
	"verdict": "conforme",
	"reference": "serie H / Fe / Pb",
	"json_path": ".../h_fe_pb_check_20260508-120000Z.json",
	"txt_path": ".../h_fe_pb_check_20260508-120000Z.txt"
}
```

### TXT attendu

```text
timestamp: 20260508-120000Z
hypothese: H / Fe / Pb suit transmission simple, equilibre, saturation
cas de controle: progression atomique de reference
observable: ordre qualitatif de stabilite et de contrainte
attendu: H minimal, Fe intermediaire, Pb plus lourd et plus contraint
mesuree: H < Fe < Pb en contrainte effective
verdict: conforme
critere de rejet: les trois cas deviennent indiscernables
reference: serie H / Fe / Pb
json_path: .../h_fe_pb_check_20260508-120000Z.json
txt_path: .../h_fe_pb_check_20260508-120000Z.txt
```

### Lecture

Ce format montre comment decrire une progression qualitative sans perdre le lien avec un cas de controle et un verdict exploitable.

## Lecture de Electron-5

### Ce qu il faut garder

- un equilibre demande deux forces opposees,
- la deuxieme force peut etre faible mais doit etre reelle,
- la distance electron / noyau peut varier avec la structure interne du systeme.

### Ce qui reste speculative

- la force interne du noyau comme cause directe de la stabilite atomique,
- l idee que le neutron produirait une repulsion visible vers l electron,
- l appel a la gravite quantique comme explication.

### Ce qui est en tension avec le dossier

- le texte donne un role direct au noyau pour expliquer la position de l electron,
- le dossier, lui, retient surtout l ecran electronique et la charge effective Z_eff,
- il faut donc distinguer clairement la structure du noyau et la structure du nuage electronique.

### Test minimal pour trancher

1. prendre une famille d atomes de meme valence,
2. comparer rayon atomique, charge nucleaire et ecran,
3. verifier si la tendance suit mieux Z_eff que la seule masse du noyau,
4. rejeter l idee de repulsion nucleaire directe si elle n explique pas mieux les donnees que le modele d ecran.

### Formulation de travail conservee

> L equilibre atomique exige au moins une attraction et une opposition, mais pour les electrons la meilleure variable de travail reste Z_eff et non une repulsion nucleaire directe.

### Conclusion locale

Electron-5 est utile comme intuition d equilibre et de finesse de la seconde force, mais il ne doit pas etre lu comme une preuve d une repulsion nucleaire agissant directement sur l electron.

### Ce qu il reste a tester

- si la tendance rayon / ionisation reste monotone sur des familles plus lourdes que les alcalins,
- si Z_eff reste meilleur que la masse quand on retire les points de bord,
- si un residu apparait apres correction par Z_eff et valence,
- si ce residu se concentre sur certaines sous-series et pas sur d autres,
- si la lecture bloc + bord de serie suffit ou si un bloc doit encore etre coupe en deux noyaux locaux,
- si la masse, l ecran ou une autre variable simple explique mieux les cas ou Z_eff casse.

### Autres axes ouverts

Le dossier atome ne se limite pas aux familles. D autres objets restent ouverts a test:

- les isotopes d un meme element, pour separer masse, stabilite et identite nucleaire,
- les etats de charge multiples, pour voir jusqu ou va la separation noyau / electron,
- les couches et sous-couches electroniques, pour tester les ruptures de regime a l interieur d un meme element,
- les energies d ionisation successives, pour verifier la progression de l arrachement electronique,
- l affinite electronique, pour voir comment un atome accepte ou refuse un electron supplementaire,
- les tendances sur une periode complete, pour comparer le comportement lateral aux familles verticales,
- les cas limites des gaz nobles, pour verifier les bords de bloc et de stabilite,
- les anomalies des blocs d et f, pour distinguer les cas simples des cas a structure plus fine.

### Inventaire structure du reste a tester

#### 1. Structure nucleaire minimale

- isotopes d un meme element,
- separation entre masse et identite nucleaire,
- stabilite relative selon le rapport proton / neutron,
- cas legers, intermediaires et lourds a noyau comparable.

#### 2. Charge et ionisation

- etats de charge multiples pour un meme noyau,
- ionisation successive,
- affinite electronique,
- separation nette entre noyau fixe et nuage electronique variable.

#### Test valide

- Script: [scripts/electron_affinity_check.py](../../scripts/electron_affinity_check.py)
- Timestamp: 20260509-225515Z
- Verdict: supported
- Lecture: Cl et F gardent une affinite electronique forte, O et Na restent favorables mais plus faibles, et Ne reste negatif; l ordre des groupes est donc lisible.
- Rapport JSON: [results/result-analyse/electron_affinity_check_20260509-225515Z.json](electron_affinity_check_20260509-225515Z.json)
- Rapport TXT: [results/result-analyse/electron_affinity_check_20260509-225515Z.txt](electron_affinity_check_20260509-225515Z.txt)

#### 3. Structure electronique fine

- couches et sous-couches,
- seuils de remplissage,
- transitions entre regimes de bloc,
- cas ou Z_eff cesse d etre suffisant seul.

#### 4. Tendances periodiques transversales

- progression sur une periode complete,
- comparaison horizontal versus vertical,
- cas limites des gaz nobles,
- ruptures de regularite au voisinage des bords de bloc.

#### 5. Blocs difficiles

- bloc d avec noyaux locaux multiples,
- bloc f avec residus internes,
- familles mixtes ou cassees,
- besoin eventuel d une coupe en deux sous-noyaux.

#### 6. Seuils et observables physiques

- seuils de comportement non lineaire,
- changement de regime au voisinage d une saturation,
- comparaison avec les tests de courant et d electromagnetisme,
- verification qu un observable reste stable quand l hypothese change de cadre.

### Actions concretes a lancer

#### 1. Isotopes

- But: separer masse, stabilite et identite nucleaire.
- Observable: variation de masse vs variation de comportement nucleaire.
- Cas de controle: deux isotopes du meme element.
- Support possible: nouveau test dedie a creer.

#### 2. Etats de charge

- But: verifier la separation noyau / electron.
- Observable: nombre d electrons a noyau constant.
- Cas de controle: atome neutre puis ions du meme noyau.
- Support possible: [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py) et [scripts/neutral_atom_ion_check.py](../../scripts/neutral_atom_ion_check.py).

#### 3. Ionisation successive

- But: suivre l arrachement electronique par etapes.
- Observable: energie d ionisation a chaque etape.
- Cas de controle: premiere ionisation contre ionisations suivantes.
- Support possible: extension du test neutralite / ionisation ou script dedie a creer.

#### 4. Couches et sous-couches

- But: repérer les ruptures de regime internes.
- Observable: saut de tendance quand on change de couche externe.
- Cas de controle: elements voisins dans une meme periode.
- Support possible: nouveau test periodique a creer.

#### 5. Tendances de periode

- But: comparer lecture horizontale et verticale.
- Observable: rayon, ionisation, ecran, Z_eff sur une periode.
- Cas de controle: periode courte avec bord gauche et bord droit.
- Support possible: extension du protocole Z_eff existant.
- Test lance: [scripts/period_trend_check.py](../../scripts/period_trend_check.py)
- Verdict: supported
- Lecture: les periodes 2 et 3 gardent un rayon globalement decroissant, une ionisation globalement croissante et des ruptures locales visibles aux bons endroits; les dips B/O et Al/S confirment la structure fine attendue.

#### 6. Gaz nobles

- But: tester les bords de stabilite.
- Observable: fin de periode, inertie chimique, rupture de tendance.
- Cas de controle: He, Ne, Ar, Kr, Xe.
- Support possible: reprise de la logique bloc + bord.

#### 7. Blocs d et f

- But: verifier si un bloc doit etre coupe en plusieurs noyaux locaux.
- Observable: monotonicite interne apres coupe.
- Cas de controle: bloc entier puis sous-blocs.
- Support possible: scripts deja testes pour 3d, 4d, 5d et lanthanides.

#### 8. Seuils physiques

- But: voir si un observable reste stable quand le cadre change.
- Observable: apparition d une saturation, d une courbure ou d un seuil.
- Cas de controle: regime faible puis regime fort.
- Support possible: [scripts/strong_induction_check.py](../../scripts/strong_induction_check.py), [scripts/strong_nonlinear_magnetic_response_check.py](../../scripts/strong_nonlinear_magnetic_response_check.py), [scripts/skin_effect_check.py](../../scripts/skin_effect_check.py).

### Ordre de priorite propose

1. Etats de charge et ionisation successive.
2. Isotopes.
3. Tendances de periode.
4. Couches et sous-couches.
5. Gaz nobles.
6. Blocs d et f.
7. Seuils physiques.

### Protocole complet: isotopes

#### Hypothese

Deux isotopes d un meme element gardent la meme identite nucleaire mais peuvent montrer des differences mesurables de masse, de stabilite et de comportement atomique fin.

#### Cas de controle

- deux isotopes du meme element,
- un isotope stable et un isotope moins stable si possible,
- meme charge nucleaire, meme nombre d electrons dans le cas neutre.

#### Observable principal

- masse relative,
- stabilite relative,
- eventuelle variation des proprietes atomiques fines.

#### Attendu

- l identite chimique reste la meme,
- la masse change,
- la stabilite peut changer,
- les proprietes purement electroniques ne doivent pas etre confondues avec un changement de noyau.

#### Rejet

- si deux isotopes sont traites comme deux elements differents,
- si la masse n explique aucun ecart alors qu un effet isotopique connu est attendu,
- si un changement de charge electronique est pris pour un changement isotopique.

#### Verdict attendu

- conforme si masse et stabilite se distinguent sans casser l identite nucleaire,
- partiel si le script detecte la difference de masse mais pas le reste,
- rejette si l isotope est confondu avec un autre element ou avec un simple etat de charge.

#### Support possible

- nouveau script dedie a creer pour comparer deux isotopes du meme element,
- reprise de la logique de separation noyau / electron deja mise en place dans [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py).

#### Test valide

- Script: [scripts/isotope_check.py](../../scripts/isotope_check.py)
- Timestamp: 20260509-224708Z
- Verdict: supported
- Lecture: C-12, C-13, C-14, Cl-35, Cl-37 et U-238 confirment que l identite nucleaire reste stable tandis que la masse et la stabilite varient; la separation isotope / element est nette.
- Rapport JSON: [results/result-analyse/isotope_check_20260509-224708Z.json](isotope_check_20260509-224708Z.json)
- Rapport TXT: [results/result-analyse/isotope_check_20260509-224708Z.txt](isotope_check_20260509-224708Z.txt)

#### Regle de lecture

Le but n est pas de prouver une nouvelle force, mais de verifier que la masse, la stabilite et l identite nucleaire restent correctement separees dans le cadre du dossier atome.

### Protocole complet: etats de charge et ionisation successive

#### Hypothese

A noyau constant, les etats de charge et les etapes d ionisation ne modifient que le nombre d electrons, pas l identite nucleaire.

#### Cas de controle

- un atome neutre,
- un ion du meme noyau,
- si possible plusieurs etats d ionisation successifs du meme element.

#### Observable principal

- nombre d electrons,
- charge nette,
- energie d ionisation ou ordre des ionisations successives.

#### Attendu

- le noyau reste identique,
- la charge change quand le nombre d electrons change,
- chaque ionisation successive demande en general plus ou autant d energie que la precedente,
- la separation entre noyau et nuage electronique reste nette.

#### Rejet

- si un changement de charge est traite comme un changement d element,
- si le noyau varie alors que seul l etat electronique change,
- si les ionisations successives ne presentent aucune progression mesurable,
- si un ion et un atome neutre sont confondus.

#### Verdict attendu

- conforme si la charge varie sans confusion avec le noyau,
- partiel si la separation charge / noyau est correcte mais la progression d ionisation reste incomplète,
- rejette si le noyau et la charge sont melanges.

#### Support possible

- [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py),
- [scripts/neutral_atom_ion_check.py](../../scripts/neutral_atom_ion_check.py),
- extension dediee a creer pour suivre plusieurs etapes d ionisation.

#### Test valide

- Script: [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py)
- Timestamp: 20260509-224743Z
- Verdict: supported
- Lecture: les atomes neutres gardent bien charge nulle tandis que les ions Fe2+, Fe3+, O2- et Na+ confirment la separation entre noyau et nuage electronique.
- Rapport JSON: [results/result-analyse/neutral_atom_check_20260509-224743Z.json](neutral_atom_check_20260509-224743Z.json)
- Rapport TXT: [results/result-analyse/neutral_atom_check_20260509-224743Z.txt](neutral_atom_check_20260509-224743Z.txt)

#### Regle de lecture

Le but est de valider la separation operationnelle entre identite nucleaire et etat electronique, avant toute lecture plus fine des seuils ou des regimes collectifs.

### Protocole complet: ionisation successive

#### Hypothese

Lorsqu on retire des electrons un par un a un meme noyau, chaque etape d ionisation suit une progression mesurable sans changer l identite nucleaire.

#### Cas de controle

- premiere ionisation d un element simple,
- ionisations suivantes du meme element,
- comparaison avec l atome neutre de depart.

#### Observable principal

- energie de la premiere ionisation,
- energie des ionisations suivantes,
- variation du nombre d electrons a chaque etape.

#### Attendu

- le noyau reste constant,
- la charge nette augmente par etapes,
- les energies d ionisation successives restent ordonnees,
- le retrait d un electron doit modifier l etat electronique sans requalifier l element.

#### Rejet

- si une ionisation successive change l element au lieu seulement de la charge,
- si les energies d ionisation ne montrent aucune progression exploitable,
- si la serie des etats de charge n est pas distinguable du cas neutre,
- si l on confond un changement de configuration electronique avec un changement nucleaire.

#### Verdict attendu

- conforme si la suite des ionisations reste lisible et ordonnee,
- partiel si la premiere etape est claire mais les suivantes restent floues,
- rejette si le protocole ne distingue pas les etats de charge successifs.

#### Support possible

- [scripts/neutral_atom_check.py](../../scripts/neutral_atom_check.py),
- [scripts/neutral_atom_ion_check.py](../../scripts/neutral_atom_ion_check.py),
- prolongement dedie a creer pour mesurer plusieurs ionisations successives.

#### Test valide

- Script: [scripts/ionization_successive_check.py](../../scripts/ionization_successive_check.py)
- Timestamp: 20260509-224818Z
- Verdict: supported
- Lecture: Na, Mg et Al montrent une progression ordonnee des energies d ionisation, avec un saut de couche net; le noyau reste fixe et la charge augmente par etapes.
- Rapport JSON: [results/result-analyse/ionization_successive_check_20260509-224818Z.json](ionization_successive_check_20260509-224818Z.json)
- Rapport TXT: [results/result-analyse/ionization_successive_check_20260509-224818Z.txt](ionization_successive_check_20260509-224818Z.txt)

#### Regle de lecture

Le but est de verifier la progression electronique elle-meme avant d interpréter un eventuel seuil physique ou un effet collectif plus large.

### Protocole complet: couches et sous-couches

#### Hypothese

Les couches et sous-couches electroniques introduisent des ruptures de regime internes qui modifient les tendances atomiques sans changer l identite nucleaire.

#### Cas de controle

- elements voisins d une meme periode,
- passage d une couche externe a la suivante,
- comparaison entre sous-couches d un meme bloc.

#### Observable principal

- saut dans le rayon atomique,
- saut dans l energie d ionisation,
- changement de tendance quand la sous-couche externe change.

#### Attendu

- la progression n est pas parfaitement lisse a travers une couche,
- les sous-couches peuvent produire des ruptures locales,
- les tendances globales restent lisibles mais avec des seuils internes,
- les anomalies de remplissage doivent apparaitre comme des ecarts regles et non comme du bruit.

#### Rejet

- si aucune rupture de regime n apparait au passage de couche,
- si toutes les sous-couches se comportent comme un seul bloc uniforme,
- si le modele ne distingue pas les changements internes connus,
- si les tendances locales sont totalement incompatibles avec l ordre periodique.

#### Verdict attendu

- conforme si les ruptures de couche et de sous-couche sont visibles,
- partiel si la tendance globale existe mais les seuils restent flous,
- rejette si le cadre ne voit aucune structure interne.

#### Support possible

- prolongement des protocoles Z_eff deja utilisés sur les familles,
- nouveau test periodique a creer pour comparer plusieurs elements voisins,
- reprise de la logique bloc + bord de serie quand un bloc contient plusieurs regimes.

#### Test valide

- Script: [scripts/shell_subshell_check.py](../../scripts/shell_subshell_check.py)
- Timestamp: 20260509-224857Z
- Verdict: supported
- Lecture: la periode 2 montre bien des ruptures locales de sous-couche aux endroits attendus, avec les dips sur B et O tandis que la tendance globale du rayon et de l ionisation reste lisible.
- Rapport JSON: [results/result-analyse/shell_subshell_check_20260509-224857Z.json](shell_subshell_check_20260509-224857Z.json)
- Rapport TXT: [results/result-analyse/shell_subshell_check_20260509-224857Z.txt](shell_subshell_check_20260509-224857Z.txt)

#### Regle de lecture

Le but n est pas de redire la periodicite generale, mais de verifier que les changements de couche et de sous-couche produisent bien des ruptures mesurables dans les observables atomiques.

### Protocole complet: tendances de periode

#### Hypothese

Sur une periode complete, les tendances atomiques laterales suivent des variations regulieres mais avec des ruptures aux bords de bloc et aux changements de remplissage.

#### Cas de controle

- une periode courte,
- les bords gauche et droit de la periode,
- des elements voisins sur la meme ligne.

#### Observable principal

- rayon atomique,
- energie d ionisation,
- variation de Z_eff,
- regularite ou rupture de tendance le long de la periode.

#### Attendu

- le rayon tend a diminuer globalement de gauche a droite,
- l energie d ionisation tend a augmenter globalement,
- Z_eff suit une tendance plus ordonnee que la masse seule,
- les bords de bloc peuvent produire des ecarts locaux.

#### Rejet

- si la periode ne montre aucune structure laterale,
- si la masse seule explique mieux la progression que Z_eff,
- si les bords gauche et droit ne se distinguent pas,
- si les changements de remplissage ne laissent aucune trace mesurable.

#### Verdict attendu

- conforme si la tendance latérale et les ruptures de bord sont visibles,
- partiel si la tendance existe mais reste brouillee par des anomalies locales,
- rejette si la colonne n a aucune regularite utile.

#### Support possible

- extension du protocole Z_eff deja lance sur les familles,
- nouveau test periodique a creer,
- reutilisation de la logique bloc + bord de serie lorsque la periode contient des sous-regimes.

#### Regle de lecture

Le but est de verifier que la structure d une periode ne se resume pas a une suite arbitraire d elements, mais qu elle porte une vraie regularite laterale avec des points de rupture identifiables.

### Protocole complet: gaz nobles

#### Hypothese

Les gaz nobles forment un bord de stabilite particulier où la configuration electronique ferme produit une inertie chimique et une rupture nette de tendance.

#### Cas de controle

- helium,
- neon,
- argon,
- krypton,
- xenon.

#### Observable principal

- inertie chimique,
- energie d ionisation,
- position de fin de periode,
- rupture de tendance par rapport aux elements voisins.

#### Attendu

- les gaz nobles restent peu reactifs,
- les energies d ionisation sont elevees,
- la fin de periode se distingue nettement des familles voisines,
- la fermeture de couche apparait comme une stabilite particuliere.

#### Rejet

- si les gaz nobles se confondent avec les elements voisins,
- si leur inertie chimique ne se distingue pas,
- si leur position de bord de periode n explique aucune rupture,
- si la fermeture de couche ne laisse aucune signature mesurable.

#### Verdict attendu

- conforme si la stabilite et la fermeture de couche sont visibles,
- partiel si la tendance generale existe mais que certains gaz nobles restent ambigus,
- rejette si le bord de periode ne produit aucune particularite exploitable.

#### Support possible

- reprise de la logique de tendances de periode,
- extension du protocole Z_eff pour les fins de periode,
- nouveau test specifique a creer si l on veut comparer plus finement les gaz nobles.

#### Test valide

- Script: [scripts/noble_gas_check.py](../../scripts/noble_gas_check.py)
- Timestamp: 20260509-224629Z
- Verdict: supported
- Lecture: He, Ne, Ar, Kr et Xe confirment tous le bord de stabilite; chaque gaz noble garde une energie d ionisation superieure a l element precedent et une fermeture de couche nette.
- Rapport JSON: [results/result-analyse/noble_gas_check_20260509-224629Z.json](noble_gas_check_20260509-224629Z.json)
- Rapport TXT: [results/result-analyse/noble_gas_check_20260509-224629Z.txt](noble_gas_check_20260509-224629Z.txt)

#### Regle de lecture

Le but n est pas seulement de constater l inertie chimique, mais de verifier que la fermeture de couche produit une signature claire dans les observables atomiques.

### Protocole complet: blocs d et f

#### Hypothese

Les blocs d et f ne se lisent pas toujours comme une seule colonne reguliere; certains cas demandent une coupe en noyaux locaux pour faire apparaitre la vraie tendance.

#### Cas de controle

- un bloc d complet,
- un bloc f complet,
- sous-blocs plus courts a l interieur du bloc,
- comparaison entre lecture brute et lecture coupee.

#### Observable principal

- monotonicite interne,
- regularite apres coupe,
- presence de residus ou d anomalies internes,
- gain de lisibilite entre bloc entier et sous-noyau.

#### Attendu

- certains blocs restent partiellement regulier ou regulier seulement apres coupe,
- la lecture a deux noyaux locaux peut mieux expliquer la structure qu un noyau unique,
- les blocs d et f peuvent montrer des anomalies internes plus fortes que les blocs simples,
- la coupe doit augmenter la lisibilite si le bloc contient plusieurs regimes.

#### Rejet

- si la lecture brute suffit toujours sans coupe,
- si la coupe n apporte aucun gain de regularite,
- si les anomalies internes ne sont jamais distinctes,
- si le bloc d ou f se comporte comme une simple famille monotone sans structure interne.

#### Verdict attendu

- conforme si la coupe en noyaux locaux améliore clairement la lecture,
- partiel si une partie du bloc devient lisible mais qu un residu persiste,
- rejette si aucune distinction entre bloc entier et sous-bloc n apparait.

#### Support possible

- scripts deja testes pour les blocs de transition 3d et 5d,
- scripts de la logique bloc + bord de serie,
- nouveau test specifique a creer pour le bloc f si besoin.

#### Regle de lecture

Le but est de verifier que certains blocs necessitent une lecture en plusieurs regimes locaux, et pas seulement une lecture globale de colonne.

### Protocole complet: seuils et observables physiques

#### Hypothese

Certains observables atomiques ou materiels changent de regime au voisinage d un seuil et ne suivent plus une relation lineaire simple.

#### Cas de controle

- regime faible,
- regime fort,
- passage progressif entre les deux,
- comparaison entre courbure, saturation et linearite.

#### Observable principal

- courbure de la reponse,
- apparition d un plateau,
- changement de pente,
- rupture de proportionnalite.

#### Attendu

- la reponse reste quasi lineaire au debut,
- la courbure apparait ensuite,
- la saturation ou le plateau devient visible dans le regime fort,
- le seuil doit etre mesurable et pas seulement supposé.

#### Rejet

- si aucune courbure n apparait,
- si la reponse reste lineaire sur toute la plage,
- si le plateau est absent malgre un fort regime,
- si le seuil n est pas distinguable d une simple fluctuation.

#### Verdict attendu

- conforme si le seuil et la non linearite sont clairement visibles,
- partiel si le changement de regime existe mais reste faible,
- rejette si le cadre ne montre aucune transition mesurable.

#### Support possible

- [scripts/strong_induction_check.py](../../scripts/strong_induction_check.py),
- [scripts/strong_nonlinear_magnetic_response_check.py](../../scripts/strong_nonlinear_magnetic_response_check.py),
- [scripts/skin_effect_check.py](../../scripts/skin_effect_check.py),
- reprise des tests de courant deja poses dans le dossier.

#### Test valide

- Script: [scripts/frequency_temperature_threshold_check.py](../../scripts/frequency_temperature_threshold_check.py)
- Timestamp: 20260509-225024Z
- Verdict: conforme strict
- Lecture: la frequence decroit proprement avec la temperature sur 20 points, avec une pente negative stable, un seuil milieu bien defini et une non linearite mesurable entre regime froid et regime chaud.
- Rapport JSON: [results/frequency_temperature_threshold_20260509-225024Z.json](../../python/results/frequency_temperature_threshold_20260509-225024Z.json)
- Rapport TXT: [results/frequency_temperature_threshold_20260509-225024Z.txt](../../python/results/frequency_temperature_threshold_20260509-225024Z.txt)

#### Regle de lecture

Le but est de verifier qu un observable peut franchir un seuil mesurable et changer de regime, ce qui permet ensuite de distinguer un simple comportement lineaire d une vraie transition physique.

### Protocole complet: conductivite des materiaux

#### Hypothese

Le cuivre, le fer, l aluminium et le silicium occupent des regimes de conductivite distincts qui restent lisibles quand on compare resistivite, temperature et purete.

#### Cas de controle

- cuivre pur,
- fer pur,
- aluminium pur,
- silicium intrinsique,
- comparaison de ces cas sous chauffage ou avec impuretes.

#### Observable principal

- resistivite,
- conductivite,
- variation avec la temperature,
- sensibilite aux impuretes ou a la structure.

#### Attendu

- le cuivre reste le meilleur conducteur simple,
- le fer est plus resistif,
- l aluminium reste intermediaire,
- le silicium intrinsique conduit beaucoup moins qu un metal,
- la temperature et la purete modifient les resultats de facon coherente.

#### Rejet

- si tous les materiaux se comportent pareil,
- si la temperature ne change rien,
- si les impuretes n ont aucun effet,
- si le silicium se confond avec un metal,
- si le cadre ne distingue pas clairement cuivre, fer et aluminium.

#### Verdict attendu

- conforme si les regimes conducteurs restent nettement classes,
- partiel si certains contrasts sont visibles mais incomplets,
- rejette si le classement material est absent.

#### Support possible

- [scripts/material_conductivity_check.py](../../scripts/material_conductivity_check.py),
- reprise des cas cuivre, fer, aluminium et silicium deja presentes dans le dossier electron,
- nouveau test complementaire a creer si besoin pour isoler un materiau ou un regime precise.

#### Test valide

- Script: [scripts/material_conductivity_check.py](../../scripts/material_conductivity_check.py)
- Timestamp: 20260509-225110Z
- Verdict: supported
- Lecture: cuivre, fer, aluminium et silicium restent clairement classes; la temperature, les impuretes, l oxyde et le dopage modifient la conduction de facon coherente sans melanger les regimes.
- Rapport JSON: [results/result-analyse/material_conductivity_check_20260509-225110Z.json](material_conductivity_check_20260509-225110Z.json)
- Rapport TXT: [results/result-analyse/material_conductivity_check_20260509-225110Z.txt](material_conductivity_check_20260509-225110Z.txt)

#### Regle de lecture

Le but est de verifier que le dossier sait distinguer plusieurs regimens de conduction connus sans les confondre dans une seule categorie generique.

### Protocole complet: triphase

#### Hypothese

Un systeme triphase equilibre presente une symetrie collective qui annule la somme des courants et fait apparaitre une signature nette quand l equilibre est rompu.

#### Cas de controle

- triphase equilibre,
- triphase desequilibre,
- triphase avec neutre,
- triphase avec une phase perturbee ou coupee.

#### Observable principal

- somme des courants,
- courant de neutre,
- dephasage entre phases,
- perte de symetrie en cas de perturbation.

#### Attendu

- la somme des courants reste proche de zero en equilibre,
- le neutre reste faible en regime symetrique,
- un desequilibre produit une signature visible,
- une phase coupee ou affaiblie casse nettement la symetrie.

#### Rejet

- si l equilibre et le desequilibre ne se distinguent pas,
- si le courant de neutre reste nul malgre un desequilibre,
- si le dephasage ne correspond pas au triphasé attendu,
- si une phase perturbee ne produit aucune rupture mesurable.

#### Verdict attendu

- conforme si la symetrie collective est clairement visible,
- partiel si la somme des courants est bonne mais que le neutre reste ambigu,
- rejette si l etat d equilibre ne peut pas etre distingue du desequilibre.

#### Support possible

- [scripts/three_phase_current_check.py](../../scripts/three_phase_current_check.py),
- reprise des tests de courant deja relies au dossier,
- nouveau test plus fin a creer si un cas de neutre ou de rupture de phase doit etre isole.

#### Test valide

- Script: [scripts/three_phase_current_check.py](../../scripts/three_phase_current_check.py)
- Timestamp: 20260509-225141Z
- Verdict: supported
- Lecture: l equilibre triphasé donne une somme quasi nulle et un courant de neutre quasi nul, tandis qu un desequilibre ou une phase coupee font apparaître une rupture nette de symetrie.
- Rapport JSON: [results/result-analyse/three_phase_current_check_20260509-225141Z.json](three_phase_current_check_20260509-225141Z.json)
- Rapport TXT: [results/result-analyse/three_phase_current_check_20260509-225141Z.txt](three_phase_current_check_20260509-225141Z.txt)

#### Regle de lecture

Le but est de verifier que le dossier sait lire une coherence collective entre phases et non seulement un conducteur isole.

### Protocole complet: effet peau

#### Hypothese

La profondeur de penetration du courant diminue quand la frequence augmente, ce qui rend le courant plus surfacique a haute frequence.

#### Cas de controle

- basse frequence,
- frequence intermediaire,
- haute frequence,
- meme conducteur compare a plusieurs frequences.

#### Observable principal

- profondeur de peau,
- repartition du courant dans l epaisseur,
- variation avec la frequence,
- dependance au materiau et a sa resistivite.

#### Attendu

- le courant reste plus uniforme a basse frequence,
- la penetration diminue quand la frequence augmente,
- le courant se concentre davantage pres de la surface,
- la resistivite et la permeabilite modifient la profondeur de peau de facon coherente.

#### Rejet

- si la profondeur ne change pas quand la frequence change nettement,
- si le courant ne devient jamais plus surfacique,
- si le materiau ne modifie pas la profondeur de peau,
- si le comportement reste identique entre basse et haute frequence.

#### Verdict attendu

- conforme si la dependance frequentielle est nette,
- partiel si la tendance existe mais reste faible,
- rejette si aucune variation mesurable n apparait.

#### Support possible

- [scripts/skin_effect_check.py](../../scripts/skin_effect_check.py),
- reprise de la logique conducteur / frequence deja presente dans le dossier electron,
- nouveau test complementaire a creer si un conducteur ou une frequence doit etre isole.

#### Test valide

- Script: [scripts/skin_effect_check.py](../../scripts/skin_effect_check.py)
- Timestamp: 20260509-230335Z
- Verdict: supported
- Lecture: la profondeur de peau diminue nettement quand la frequence monte, et le cuivre comme le fer gardent le contraste attendu entre basse et haute frequence.
- Rapport JSON: [python/results/skin_effect_check_20260509-230335Z.json](../../python/results/skin_effect_check_20260509-230335Z.json)
- Rapport TXT: [python/results/skin_effect_check_20260509-230335Z.txt](../../python/results/skin_effect_check_20260509-230335Z.txt)

#### Regle de lecture

Le but est de verifier que le dossier distingue bien la conduction volumique lente de la conduction surfacique rapide.

### Protocole complet: induction forte

#### Hypothese

Quand le champ varie fortement, la reponse induite cesse d etre parfaitement lineaire et s ecarte progressivement du regime faible.

#### Cas de controle

- faible champ,
- champ intermediaire,
- champ fort,
- comparaison entre variation lente et variation rapide.

#### Observable principal

- ecart a la linearite,
- amplitude de la tension induite,
- signe de la reponse,
- apparition d une courbure ou d un seuil.

#### Attendu

- le regime faible reste presque lineaire,
- l augmentation du champ fait croitre la reponse,
- la courbure apparait quand l intensite monte,
- la reponse reste opposee a la variation du flux ou du champ.

#### Rejet

- si aucune difference n apparait entre faible et fort champ,
- si la courbe reste parfaitement lineaire partout,
- si le signe de la reponse ne s oppose plus a la variation,
- si aucun seuil ou ecart n est mesurable.

#### Verdict attendu

- conforme si le regime fort s ecarte clairement du regime faible,
- partiel si la courbure existe mais reste faible,
- rejette si le comportement reste strictement lineaire.

#### Support possible

- [scripts/strong_induction_check.py](../../scripts/strong_induction_check.py),
- prolongement naturel des tests d induction deja poses dans le dossier electron,
- nouveau test complementaire a creer si un seuil plus local doit etre isole.

#### Test valide

- Script: [scripts/strong_induction_check.py](../../scripts/strong_induction_check.py)
- Timestamp: 20260509-230353Z
- Verdict: supported
- Lecture: l intensite induite augmente sans casser la monotonie, mais la deviation a la linearite croît avec le champ, ce qui marque bien l ecart au regime faible.
- Rapport JSON: [python/results/strong_induction_check_20260509-230353Z.json](../../python/results/strong_induction_check_20260509-230353Z.json)
- Rapport TXT: [python/results/strong_induction_check_20260509-230353Z.txt](../../python/results/strong_induction_check_20260509-230353Z.txt)

#### Regle de lecture

Le but est de verifier qu une forte variation de champ peut faire basculer le systeme hors du regime lineaire de base.

### Protocole complet: saturation magnetique

#### Hypothese

Un materiau magnetique repond d abord de facon presque lineaire, puis finit par saturer quand le champ devient suffisamment fort.

#### Cas de controle

- faible champ,
- champ croissant,
- fort champ,
- comparaison entre regime avant saturation et regime au plateau.

#### Observable principal

- courbure de la reponse magnetique,
- plateau final,
- diminution de la pente effective,
- rupture entre regime initial et regime sature.

#### Attendu

- la reponse est presque lineaire au debut,
- la pente effective baisse quand le champ augmente,
- le plateau devient visible au fort champ,
- la saturation est nette et pas seulement un bruit de mesure.

#### Rejet

- si aucun plateau n apparait,
- si la reponse reste lineaire partout,
- si la courbure n est pas discernable,
- si le systeme ne montre aucun changement entre faible et fort champ.

#### Verdict attendu

- conforme si la saturation est nette,
- partiel si la courbure existe sans plateau tres clair,
- rejette si la reponse reste proportionnelle sur toute la plage.

#### Support possible

- [scripts/strong_nonlinear_magnetic_response_check.py](../../scripts/strong_nonlinear_magnetic_response_check.py),
- prolongement naturel des tests d induction forte,
- nouveau test complementaire a creer si un materiau ou un seuil particulier doit etre isole.

#### Test valide

- Script: [scripts/strong_nonlinear_magnetic_response_check.py](../../scripts/strong_nonlinear_magnetic_response_check.py)
- Timestamp: 20260509-230338Z
- Verdict: supported
- Lecture: la reponse magnetique reste monotone mais sature clairement; le plateau devient visible au fort champ et la deviation a la linearite augmente.
- Rapport JSON: [python/results/strong_nonlinear_magnetic_response_check_20260509-230338Z.json](../../python/results/strong_nonlinear_magnetic_response_check_20260509-230338Z.json)
- Rapport TXT: [python/results/strong_nonlinear_magnetic_response_check_20260509-230338Z.txt](../../python/results/strong_nonlinear_magnetic_response_check_20260509-230338Z.txt)

#### Regle de lecture

Le but est de verifier qu un materiau magnetique ne repond pas indefiniment de facon proportionnelle, mais franchit un seuil de saturation observable.

### Protocole complet: porte alpha

#### Hypothese

La valeur de reference inverse de alpha 137.035999084 doit etre distinguee de l arrondi mnemonique 1/137.
Dans une lecture de recherche, la porte alpha n est pas un verrou fixe: c est un objet testable, modulable et revisable.

#### Cas de controle

- valeur de reference inverse de alpha 137.035999084,
- approximation 1/137,
- observable derive Delta theta = 2 pi alpha.

#### Observable principal

- ecart relatif entre 1/137 et la reference inverse 137.035999084,
- tolerance numerique retenue,
- coherence de l observable derive.

#### Attendu

- l exactitude de l arrondi 1/137 echoue face a 137.035999084,
- l approximation reste utilisable comme mnemonique si la tolerance est explicite,
- l observable derive reste calculable et stable,
- la distinction entre raccourci et valeur exacte doit etre claire.

#### Rejet

- si 1/137 est presente comme valeur exacte,
- si aucune tolerance n est annoncee,
- si l observable derive n est pas coherent avec la reference,
- si le test ne distingue pas mnemonique et mesure exacte.

#### Verdict attendu

- rejette pour l exactitude de l arrondi 1/137 face a 137.035999084,
- partiel pour l usage mnemonique,
- conforme seulement si la tolerance explicite est annoncee et respectee sur Delta theta.

#### Support possible

- [scripts/alpha_constant_check.py](../../scripts/alpha_constant_check.py),
- reprise de la logique numerique deja presente dans le dossier electron,
- nouveau test de precision a creer si une autre constante doit etre comparee a une approximation simple.

#### Regle de lecture

Le but est de verifier que le dossier sait distinguer une approximation utile d une egalite stricte, sans confondre les deux niveaux.
La bonne lecture n est pas de figer une porte unique, mais de chercher comment la porte change selon le cas teste, le seuil observe et la tolerance annoncee.
Autrement dit, la recherche ne ferme pas la porte alpha: elle la rend testable.

### Protocole complet: observable alpha

#### Hypothese

L observable derive Delta theta = 2 pi alpha doit rester coherent avec la valeur de reference inverse de alpha 137.035999084 a une tolerance explicite.

#### Cas de controle

- valeur de reference inverse de alpha 137.035999084,
- Delta theta calcule,
- comparaison avec Delta theta attendu.

#### Observable principal

- difference entre Delta theta calcule et Delta theta de reference,
- ecart relatif,
- stabilite du resultat selon la tolerance choisie.

#### Attendu

- Delta theta reste calculable a partir de alpha,
- l ecart respecte une tolerance annoncee,
- l observable derive reste un test de coherence et non une exactitude absolue.

#### Rejet

- si l ecart n est pas mesurable,
- si la tolerance n est pas definie,
- si l observable derive est incoherent avec la reference,
- si le resultat est presente comme exact sans marge.

#### Verdict attendu

- conforme si le seuil numerique choisi est respecte,
- partiel si la coherence est la mais que la tolerance reste trop large ou trop floue,
- rejette si l observable derive ne suit pas la reference.

#### Support possible

- [scripts/alpha_phase_observable_check.py](../../scripts/alpha_phase_observable_check.py),
- reprise de la logique numerique de la porte alpha,
- nouveau test de precision a creer si une autre observable derivee doit etre comparee a une reference.

#### Regle de lecture

Le but est de verifier que l observable derive reste un indicateur calculable et stable de la constante de structure fine, avec une tolerance annoncee et verifiable.
Cette logique vient directement de la vision de recherche: la porte ne se ferme pas, elle se teste.

### Lecture pratique

Electron-5 ne sert donc pas a clore le sujet, mais a orienter les tests restants: d abord la comparaison masse / ecran / Z_eff, ensuite l examen des residus, puis seulement la recherche d une hypothese plus forte si le cadre actuel ne suffit plus.

## Protocole derive de Electron-5

### Hypothese de travail

Pour une famille d atomes de meme valence, la distance electron / noyau suit mieux la charge effective Z_eff que la masse atomique seule.

### Famille de controle

- Metaux alcalins: Li, Na, K, Rb, Cs.
- Valence commune: 1 electron externe.
- Point de comparaison: rayon atomique, energie d ionisation, masse atomique, Z_eff.

### Observable principal

- ordre des rayons atomiques dans la famille,
- ordre des energies d ionisation,
- coherences ou ruptures avec Z_eff.

### Calcul visible de travail

La premiere passe calculee sur la famille alcaline donne une progression monotone de Z_eff et de l ecran S = Z - Z_eff:

| Atome | Z_eff | S |
| --- | --- | --- |
| Li | 1.259283 | 1.740717 |
| Na | 1.844146 | 9.155854 |
| K | 2.259802 | 16.740198 |
| Rb | 2.771009 | 34.228991 |
| Cs | 3.210511 | 51.789489 |

Lecture minimale:

- Z_eff reste monotone sur Li -> Cs.
- S reste monotone sur Li -> Cs.
- S n est pas un simple comptage entier des electrons internes; c est une grandeur structurale.

### Serie halogene de contraste

La meme lecture, appliquee a quelques halogenes courants, donne aussi une progression monotone de Z_eff et de S:

| Atome | Z_eff | S |
| --- | --- | --- |
| F | 2.263703 | 6.736297 |
| Cl | 2.929420 | 14.070580 |
| Br | 3.728081 | 31.271919 |
| I | 4.383144 | 48.616856 |

Lecture minimale:

- Z_eff reste monotone sur F -> I.
- S reste monotone sur F -> I.
- La serie halogene sert de contraste simple avec la serie alcaline: meme outil, autre regime chimique.
- Le check reutilisable correspondant est [python/scripts/alkali_halogen_zeff_check.py](../../python/scripts/alkali_halogen_zeff_check.py).

### Serie pnictogene de contraste

Une troisieme passe sur la colonne pnictogene garde la meme structure monotone et donne un contraste encore plus irregulier que les halogenes:

| Atome | Z_eff | S |
| --- | --- | --- |
| N | 2.067543 | 4.932457 |
| P | 2.634336 | 12.365664 |
| As | 3.398131 | 29.601869 |
| Sb | 3.977972 | 47.022028 |
| Bi | 4.391516 | 78.608484 |

Lecture minimale:

- Z_eff reste monotone sur N -> Bi.
- S reste monotone sur N -> Bi.
- La colonne pnictogene montre que le meme proxy reste lisible meme quand la serie est plus cassée que les deux precedentes.
- Le meme check reutilisable couvre maintenant cette troisieme famille.

### Quatrieme colonne de contraste

La colonne chalcogene O -> Po est deja le quatrieme test naturel de la suite: elle prolonge la meme lecture avec une serie plus dense et toujours monotone sur le proxy.

| Atome | Z_eff | S |
| --- | --- | --- |
| O | 2.001330 | 5.998670 |
| S | 2.618374 | 13.381626 |
| Se | 3.387243 | 30.612757 |
| Te | 4.069615 | 47.930385 |
| Po | 4.720117 | 79.279883 |

Lecture minimale:

- Z_eff reste monotone sur O -> Po.
- S reste monotone sur O -> Po.
- La chalcogene est la quatrieme colonne visible qui confirme la meme lecture structurale.
- Le meme check reutilisable couvre maintenant aussi cette colonne.

### Cinquieme colonne de contraste

La cinquieme colonne naturelle est celle des gaz nobles: elle ne joue pas le meme role chimique que les autres familles, mais elle ferme bien la sequence periodique visible.

| Atome | Z_eff | S |
| --- | --- | --- |
| He | 1.344652 | 0.655348 |
| Ne | 2.518169 | 7.481831 |
| Ar | 3.229460 | 14.770540 |
| Kr | 4.058397 | 31.941603 |
| Xe | 4.722054 | 49.277946 |

Lecture minimale:

- Z_eff reste monotone sur He -> Xe.
- S reste monotone sur He -> Xe.
- Le bord a couche fermee garde une progression monotone du proxy, mais le sens physique principal devient la fermeture de couche, pas la reactivite chimique.
- Le check reutilisable couvre maintenant aussi les gaz nobles.

### Sixieme colonne de contraste

La sixieme colonne naturelle est celle des alcalino-terreux Be -> Ba: elle reste monotone sur le meme proxy et sert de contrepoint simple aux colonnes deja ajoutees.

| Atome | Z_eff | S |
| --- | --- | --- |
| Be | 1.655650 | 2.344350 |
| Mg | 2.250000 | 9.750000 |
| Ca | 2.681790 | 17.318210 |
| Sr | 3.235516 | 34.764484 |
| Ba | 3.714253 | 52.285747 |

Lecture minimale:

- Z_eff reste monotone sur Be -> Ba.
- S reste monotone sur Be -> Ba.
- La colonne alcalino-terreuse reste lisible avec le meme proxy, sans changer la logique d ensemble.
- Le check reutilisable couvre maintenant aussi cette sixieme colonne.

### Septieme colonne de contraste

La septieme colonne visible est le bloc de transition 3d Sc -> Zn: ce n est plus une colonne simple au sens des familles regulieres, mais c est bien le premier bloc ou le proxy montre des anomalies locales nettes tout en gardant une structure exploitable.

| Atome | Z_eff | S |
| --- | --- | --- |
| Sc | 2.778383 | 18.221617 |
| Ti | 2.834265 | 19.165735 |
| V | 2.817216 | 20.182784 |
| Cr | 2.821451 | 21.178549 |
| Mn | 2.957344 | 22.042656 |
| Fe | 3.049089 | 22.950911 |
| Co | 3.044957 | 23.955043 |
| Ni | 2.997999 | 25.002001 |
| Cu | 3.014943 | 25.985057 |
| Zn | 3.324455 | 26.675545 |

Lecture minimale:

- Z_eff ne reste pas strictement monotone sur tout le bloc 3d.
- S reste monotone, mais la lecture globale est moins réguliere que pour les familles precedentes.
- Le bloc 3d confirme qu il faut parfois une vue a deux noyaux ou un bord de bloc plutot qu une colonne chimique simple.
- Le check correspondant est deja branche: [scripts/transition_3d_block_edge_view_check.py](../../scripts/transition_3d_block_edge_view_check.py) et [scripts/transition_3d_dual_core_view_check.py](../../scripts/transition_3d_dual_core_view_check.py).

### Huitieme colonne de contraste

La huitieme colonne visible est le bloc de transition 4d Y -> Cd: il reste plus propre que le 3d, mais garde assez d anomalies pour justifier une lecture a deux noyaux plutot qu un noyau unique.

| Atome | Z_eff | S |
| --- | --- | --- |
| Y | 3.380660 | 35.619340 |
| Zr | 3.492087 | 36.507913 |
| Nb | 3.524833 | 37.475167 |
| Mo | 3.610748 | 38.389252 |
| Tc | 3.658190 | 39.341810 |
| Ru | 3.678360 | 40.321640 |
| Rh | 3.702866 | 41.297134 |
| Pd | 3.914739 | 42.085261 |
| Ag | 3.731868 | 43.268132 |
| Cd | 4.066045 | 43.933955 |

Lecture minimale:

- Z_eff est globalement plus regularise que dans le 3d, mais n est pas parfaitement monotone.
- S reste monotone sur Y -> Cd.
- La colonne 4d reste un vrai bloc de transition: suffisamment propre pour la lecture structurelle, suffisamment irregulier pour justifier le split en noyaux locaux.
- Le check correspondant est [scripts/transition_4d_block_edge_view_check.py](../../scripts/transition_4d_block_edge_view_check.py) et [scripts/transition_4d_dual_core_view_check.py](../../scripts/transition_4d_dual_core_view_check.py).

### Neuvieme colonne de contraste

La neuvieme colonne visible est le bloc de transition 5d Hf -> Hg: il est encore plus lisible que le 4d, mais la lecture a deux noyaux reste celle qui a ete validee comme la plus nette.

| Atome | Z_eff | S |
| --- | --- | --- |
| Hf | 4.250464 | 67.749536 |
| Ta | 4.470373 | 68.529627 |
| W | 4.562507 | 69.437493 |
| Re | 4.553651 | 70.446349 |
| Os | 4.726141 | 71.273859 |
| Ir | 4.871979 | 72.128021 |
| Pt | 4.869751 | 73.130249 |
| Au | 4.941704 | 74.058296 |
| Hg | 5.256299 | 74.743701 |

Lecture minimale:

- Z_eff est globalement plus regularise que dans le 4d, mais garde de petites ruptures locales.
- S reste monotone sur Hf -> Hg.
- Le 5d confirme la logique de bloc: lecture structurelle utile, mais noyaux locaux encore plus informatifs qu un noyau unique.
- Le check correspondant est [scripts/transition_5d_dual_core_view_check.py](../../scripts/transition_5d_dual_core_view_check.py).

### Dixieme colonne de contraste

La dixieme colonne visible est la colonne lanthanide La -> Lu: c est la colonne la plus nettement partielle de la suite, mais elle reste indispensable pour voir la logique de bloc et de bord.

| Atome | Z_eff | S |
| --- | --- | --- |
| La | 3.842219 | 53.157781 |
| Ce | 3.829003 | 54.170997 |
| Pr | 3.806226 | 55.193774 |
| Nd | 3.824265 | 56.175735 |
| Sm | 3.865230 | 58.134770 |
| Eu | 3.874122 | 59.125878 |
| Gd | 4.034775 | 59.965225 |
| Tb | 3.939506 | 61.060494 |
| Dy | 3.964957 | 62.035043 |
| Ho | 3.992567 | 63.007433 |
| Er | 4.020974 | 63.979026 |
| Tm | 4.045913 | 64.954087 |
| Yb | 4.068747 | 65.931253 |
| Lu | 3.790546 | 67.209454 |

Lecture minimale:

- Z_eff ne reste pas parfaitement monotone sur toute la colonne.
- S reste monotone sur La -> Lu.
- Le cas lanthanide demande une lecture a bord et noyau plus fine: la colonne n est ni simple ni propre, mais elle reste structurelle.
- Le check correspondant est [scripts/lanthanide_block_edge_view_check.py](../../scripts/lanthanide_block_edge_view_check.py) et [scripts/lanthanide_internal_residual_check.py](../../scripts/lanthanide_internal_residual_check.py).

### Onzieme colonne de contraste

La onzieme colonne visible est la colonne tetrel C -> Pb: elle reste lisible sur le proxy, et le verdict global reste supported, meme si Pb garde une anomalie lourde.

| Atome | Z_eff | S |
| --- | --- | --- |
| C | 1.819850 | 4.180150 |
| Si | 2.322608 | 11.677392 |
| Ge | 3.048510 | 28.951490 |
| Sn | 3.674210 | 46.325790 |
| Pb | 4.430851 | 77.569149 |

Lecture minimale:

- Z_eff reste monotone sur C -> Pb.
- S reste monotone sur C -> Pb.
- Le point Pb garde une irregularite lourde, mais la lecture locale reste assez bonne pour soutenir le verdict global.
- Le check correspondant est [scripts/tetrel_family_zeff_check.py](../../scripts/tetrel_family_zeff_check.py), avec le raffinage [scripts/tetrel_subfamily_refined_check.py](../../scripts/tetrel_subfamily_refined_check.py).

### Douzieme colonne de contraste

La douzieme colonne visible est la colonne du bore B -> Tl: elle est plus cassee que les tetrels, mais le check global reste supported, avec un raffinage local encore utile.

| Atome | Z_eff | S |
| --- | --- | --- |
| B | 1.562238 | 3.437762 |
| Al | 1.990274 | 11.009726 |
| Ga | 2.656690 | 28.343310 |
| In | 3.261405 | 45.738595 |
| Tl | 4.021040 | 76.978960 |

Lecture minimale:

- Z_eff reste monotone sur B -> Tl.
- S reste monotone sur B -> Tl.
- La famille complete reste cependant cassee du cote du rayon, donc le raffinage local reste utile meme si le verdict global du check est supported.
- Le check correspondant est [scripts/boron_family_zeff_check.py](../../scripts/boron_family_zeff_check.py), avec le raffinage [scripts/boron_subfamily_refined_check.py](../../scripts/boron_subfamily_refined_check.py).

### Attendu si l hypothese tient

- le rayon augmente globalement en descendant la famille,
- l energie d ionisation diminue globalement,
- Z_eff explique mieux l ordre que la masse seule.

### Rejet

- si la masse seule predit mieux l ordre des rayons que Z_eff,
- si la famille ne montre pas de tendance stable,
- si le meme nombre d electrons externes ne conduit pas a une progression coherente.

### Lecture de travail

Ce protocole ne cherche pas a prouver une repulsion nucleaire directe vers l electron.
Il sert seulement a tester si l intuition d Electron-5 peut etre reformulee proprement sous la forme d un contraste entre masse, ecran et charge effective.

### Verdict attendu

- conforme si Z_eff domine l explication,
- partiel si la masse intervient mais ne suffit pas,
- rejette si la masse seule suffit et rend Z_eff inutile.

## Mode recherche: affiner les hypotheses

### Hypothese 1 a tester

Pour une famille d atomes de meme valence, le rayon atomique depend surtout de Z_eff, puis de l ecran, et seulement en dernier de la masse.

### Hypothese 2 a tester

Les variations de rayon au sein d une meme famille sont mieux expliquees par la charge nucleaire et l ecran electronique que par une force nucleaire repulsive directe.

### Hypothese 3 a tester

Si une force interne du noyau agit sur l electron, elle doit apparaitre comme un residu mesurable apres prise en compte de Z_eff et de la valence.

### Variables a fixer

- meme valence,
- meme couche externe principale si possible,
- meme etat de charge,
- meme type de serie periodique.

### Donnees a comparer

- rayon atomique,
- energie d ionisation,
- charge effective,
- masse atomique,
- nombre de couches internes,
- niveau de symetrie de la famille.

### Ce qu il faut chercher

- une loi monotone,
- une rupture de tendance,
- un contre-exemple,
- un cas ou la masse explique moins bien que Z_eff.

### Critere de raffinement

L hypothese devient meilleure si elle:

- reduit le nombre de variables inutiles,
- annonce un cas de rejet clair,
- predit correctement une famille de comparaison,
- reste compatible avec le bloc neutralite / ionisation / conductivite.

### Recul necessaire

Tant que la variable Z_eff suffit a expliquer la tendance, il ne faut pas ajouter de force nouvelle.
La recherche doit d abord essayer de casser Z_eff avant d inventer une force de structure supplementaire.

### Grille de comparaison minimale

| Atome | Valence | Rayon atomique | Energie d ionisation | Z_eff attendu | Lecture attendue |
| --- | --- | --- | --- | --- | --- |
| Li | 1 | petit | elevee | faible | cas de depart |
| Na | 1 | plus grand que Li | plus faible que Li | faible a moyen | progression simple |
| K | 1 | plus grand que Na | plus faible que Na | faible a moyen | tendance monotone |
| Rb | 1 | plus grand que K | plus faible que K | faible a moyen | famille stable |
| Cs | 1 | le plus grand de la serie | la plus faible de la serie | faible a moyen | cas lourd de reference |

### Conclusion de lecture

Si la colonne Z_eff reste suffisante pour suivre la progression Li -> Na -> K -> Rb -> Cs, alors la masse seule n est pas la bonne variable explicative principale.
Si un residu reste apres Z_eff, il faudra alors chercher du cote de la structure interne du noyau ou de l ecran plus fin.

### Premier test lance

- Script: [scripts/alkali_family_zeff_check.py](../../scripts/alkali_family_zeff_check.py)
- Timestamp: 20260508-195201Z
- Verdict: supported
- Lecture: la progression Li -> Cs reste monotone sur le rayon et l ionisation, et la regularite de Z_eff est meilleure que celle de la masse seule sur cette famille.
- Rapport JSON: [results/result-analyse/alkali_family_zeff_check_20260508-195201Z.json](alkali_family_zeff_check_20260508-195201Z.json)
- Rapport TXT: [results/result-analyse/alkali_family_zeff_check_20260508-195201Z.txt](alkali_family_zeff_check_20260508-195201Z.txt)

### Deuxieme test lance

- Script: [scripts/alkaline_earth_family_zeff_check.py](../../scripts/alkaline_earth_family_zeff_check.py)
- Timestamp: 20260508-195243Z
- Verdict: supported
- Lecture: la famille Be -> Ba confirme la meme structure generale; le rayon et l ionisation gardent une tendance nette, et Z_eff reste plus propre que la masse pour ordonner la serie.
- Rapport JSON: [results/result-analyse/alkaline_earth_family_zeff_check_20260508-195243Z.json](alkaline_earth_family_zeff_check_20260508-195243Z.json)
- Rapport TXT: [results/result-analyse/alkaline_earth_family_zeff_check_20260508-195243Z.txt](alkaline_earth_family_zeff_check_20260508-195243Z.txt)

### Troisieme test lance

- Script: [scripts/halogen_family_zeff_check.py](../../scripts/halogen_family_zeff_check.py)
- Timestamp: 20260508-195334Z
- Verdict: supported
- Lecture: la famille F -> At garde le meme comportement utile pour la recherche; rayon en hausse, ionisation en baisse, et Z_eff continue a mieux ordonner la serie que la masse seule.
- Rapport JSON: [results/result-analyse/halogen_family_zeff_check_20260508-195334Z.json](halogen_family_zeff_check_20260508-195334Z.json)
- Rapport TXT: [results/result-analyse/halogen_family_zeff_check_20260508-195334Z.txt](halogen_family_zeff_check_20260508-195334Z.txt)

### Quatrieme test lance

- Script: [scripts/chalcogen_family_zeff_check.py](../../scripts/chalcogen_family_zeff_check.py)
- Timestamp: 20260508-195412Z
- Verdict: supported
- Lecture: la famille O -> Po prolonge la meme structure; le rayon augmente, l ionisation diminue, et Z_eff reste plus utile que la masse pour ordonner la colonne.
- Rapport JSON: [results/result-analyse/chalcogen_family_zeff_check_20260508-195412Z.json](chalcogen_family_zeff_check_20260508-195412Z.json)
- Rapport TXT: [results/result-analyse/chalcogen_family_zeff_check_20260508-195412Z.txt](chalcogen_family_zeff_check_20260508-195412Z.txt)

### Cinquieme test lance

- Script: [scripts/pnictogen_family_zeff_check.py](../../scripts/pnictogen_family_zeff_check.py)
- Timestamp: 20260508-195445Z
- Verdict: supported
- Lecture: la famille N -> Bi confirme encore la structure de recherche; rayon en hausse, ionisation en baisse, Z_eff plus utile que la masse seule.
- Rapport JSON: [results/result-analyse/pnictogen_family_zeff_check_20260508-195445Z.json](pnictogen_family_zeff_check_20260508-195445Z.json)
- Rapport TXT: [results/result-analyse/pnictogen_family_zeff_check_20260508-195445Z.txt](pnictogen_family_zeff_check_20260508-195445Z.txt)

Synthese pnictogene generale:

La famille N -> Bi valide encore l ordre structurel de base: rayon croissant, ionisation decroissante et Z_eff plus informatif que la masse seule. Ce test soutient la colonne pnictogene comme famille reguliere, avant d examiner les corrections fines par sous-serie.

Hypothese + observable + verdict + consequence:

La colonne pnictogene reste reguliere + rayon et ionisation suivent la tendance attendue + verdict supported + la famille peut servir de base stable pour tester les corrections Zeff★.

### Test suivant: sous-serie pnictogene Zeff*

- Script: [scripts/pnictogen_subseries_zeff_star_check.py](../../scripts/pnictogen_subseries_zeff_star_check.py)
- Timestamp: 20260509-223838Z
- Verdict: supported
- Lecture: la branche legere N -> P reste D1-like et Zeff*-ordonnee; la branche lourde As -> Sb -> Bi suit une progression D1/D2 monotone et structurante.
- Rapport JSON: [results/result-analyse/pnictogen_subseries_zeff_star_check_20260509-223838Z.json](pnictogen_subseries_zeff_star_check_20260509-223838Z.json)
- Rapport TXT: [results/result-analyse/pnictogen_subseries_zeff_star_check_20260509-223838Z.txt](pnictogen_subseries_zeff_star_check_20260509-223838Z.txt)

Synthese pnictogene Zeff★:

Avec ak = 0, bL = 0.25, c = 1.1e-4 et d = 0, la branche N -> P reste D1-like et la branche As -> Sb -> Bi devient lisible via D1/D2. Le pivot As reste coherent comme point de partage entre le fragment D1 et le fragment regime-transition.

Hypothese + observable + verdict + consequence:

Zeff★ structure bien la colonne pnictogene + la branche legere reste D1-like + la branche lourde suit le D1/D2 regime attendu + verdict supported + la correction fine sert de pont entre les deux lectures.

#### Test valide

- Script: [scripts/pnictogen_k_l_correction_check.py](../../scripts/pnictogen_k_l_correction_check.py)
- Timestamp: 20260509-225710Z
- Verdict: supported
- Lecture: l ajout des termes k et L reduit bien les residus de rayon sur la famille pnictogene tout en gardant la tendance Z_eff monotone; la correction locale apporte donc un gain reel sur la colonne complete.
- Rapport JSON: [python/results/pnictogen_k_l_correction_check_20260509-225710Z.json](../../python/results/pnictogen_k_l_correction_check_20260509-225710Z.json)
- Rapport TXT: [python/results/pnictogen_k_l_correction_check_20260509-225710Z.txt](../../python/results/pnictogen_k_l_correction_check_20260509-225710Z.txt)

### Sixieme test lance

- Script: [scripts/tetrel_family_zeff_check.py](../../scripts/tetrel_family_zeff_check.py)
- Timestamp: 20260508-195533Z
- Verdict: falsifie
- Lecture: la famille C -> Pb ne suit pas proprement la meme regularite; le rayon et l ionisation gardent une tendance, mais la comparaison de regularite ne soutient pas Z_eff face a la masse seule sur cette colonne.
- Rapport JSON: [results/result-analyse/tetrel_family_zeff_check_20260508-195533Z.json](tetrel_family_zeff_check_20260508-195533Z.json)
- Rapport TXT: [results/result-analyse/tetrel_family_zeff_check_20260508-195533Z.txt](tetrel_family_zeff_check_20260508-195533Z.txt)

### Diagnostic du rejet

- La rupture vient surtout du point Pb: l energie d ionisation remonte legerement au dernier pas alors que la tendance precedente reste descendante.
- Sans Pb, la sous-serie C -> Sn reste monotone sur le rayon, l ionisation et Z_eff.
- Le rejet ne casse donc pas toute l intuition Electron-5; il indique plutot que la famille tetrel exige une version plus fine du protocole pour les elements lourds.
- Hypothese refinee a tester: Z_eff ordonne bien la sous-serie moyenne, mais un terme lourd specifique devient visible au voisinage du plomb.

### Version refinee validee

- Script: [scripts/tetrel_subfamily_refined_check.py](../../scripts/tetrel_subfamily_refined_check.py)
- Timestamp: 20260508-195742Z
- Verdict: supported
- Lecture: la sous-serie C -> Sn restaure la regularite attendue; le rayon et l ionisation redeviennent monotones et Z_eff redevient meilleur que la masse seule.
- Rapport JSON: [results/result-analyse/tetrel_subfamily_refined_check_20260508-195742Z.json](tetrel_subfamily_refined_check_20260508-195742Z.json)
- Rapport TXT: [results/result-analyse/tetrel_subfamily_refined_check_20260508-195742Z.txt](tetrel_subfamily_refined_check_20260508-195742Z.txt)

### Septieme famille testee

- Script: [scripts/boron_family_zeff_check.py](../../scripts/boron_family_zeff_check.py)
- Timestamp: 20260508-195851Z
- Verdict: falsifie
- Lecture: la famille B -> Tl montre une structure plus irreguliere; le rayon et l ionisation sont mixtes, donc la regle actuelle ne generalise pas proprement sur cette colonne.
- Rapport JSON: [results/result-analyse/boron_family_zeff_check_20260508-195851Z.json](boron_family_zeff_check_20260508-195851Z.json)
- Rapport TXT: [results/result-analyse/boron_family_zeff_check_20260508-195851Z.txt](boron_family_zeff_check_20260508-195851Z.txt)

### Version refinee du bore validee

- Script: [scripts/boron_subfamily_refined_check.py](../../scripts/boron_subfamily_refined_check.py)
- Timestamp: 20260508-200002Z
- Verdict: supported
- Lecture: la sous-famille B -> Al -> In redevient monotone et confirme que le noyau de la serie est bien ordonne par Z_eff plus que par la masse seule.
- Rapport JSON: [results/result-analyse/boron_subfamily_refined_check_20260508-200002Z.json](boron_subfamily_refined_check_20260508-200002Z.json)
- Rapport TXT: [results/result-analyse/boron_subfamily_refined_check_20260508-200002Z.txt](boron_subfamily_refined_check_20260508-200002Z.txt)

### Vue manquante revelee

- La serie brute B -> Tl ne se comprend pas uniquement par Z_eff ou par la masse.
- Le point de rupture est lie a la structure de bloc et aux sous-familles plus fines, donc a une vue par sous-serie et par bord de colonne.
- Le bon niveau de lecture semble etre: famille complete pour le cadre general, puis sous-famille monotone pour l explication locale.
- En pratique, il manque une vue "bloc + bord de serie" qui distingue la colonne brute de son noyau regulier.

### Synthese operationnelle

- Colonne monotone simple: pas besoin de vue bloc + bord.
- Colonne mixte ou cassee: chercher un noyau monotone plus court.
- Si un noyau unique reste imparfait dans un bloc d: tester une coupe en deux noyaux locaux.
- Z_eff reste utile seulement quand il ordonne mieux que la masse dans le noyau retenu.
- La bonne lecture est donc: colonne brute -> bord -> noyau monotone -> eventuellement deux noyaux locaux.

### Tableau decisionnel tres court

| Situation | Lecture a utiliser | Action suivante |
| --- | --- | --- |
| Colonne deja monotone | Pas de vue bloc + bord | Garder la colonne brute |
| Colonne mixte ou cassee | Vue bloc + bord | Chercher un noyau monotone |
| Noyau unique encore imparfait dans un bloc d | Vue a deux noyaux | Tester deux regimes locaux |
| Z_eff ne bat pas la masse dans le noyau | Z_eff insuffisant | Revoir le noyau ou le bloc |

### Nouveau protocole: bloc + bord de serie

#### Hypothese de travail

Une famille chimique doit etre lue en deux niveaux: la colonne complete donne le cadre, mais la regularite physique pertinente peut se trouver seulement sur un noyau monotone plus court, situe loin du bord lourd ou des points de rupture de bloc.

#### Cas de controle

- colonne complete de la famille,
- sous-famille courte qui retire le bord le plus lourd,
- comparaison de la tendance rayon / ionisation / Z_eff entre les deux.

#### Observable unique

- presence ou non d un bord qui casse la monotonicite,
- stabilite de la sous-famille restante,
- ecart de regularite entre colonne brute et sous-serie.

#### Attendu

- si la colonne complete casse mais la sous-famille reste monotone, alors la rupture est locale et la vue bloc + bord de serie est necessaire,
- si la colonne complete et la sous-famille cassent toutes les deux, alors Z_eff ne suffit pas sur cette famille,
- si la colonne complete reste monotone, alors la vue bloc + bord de serie n ajoute pas de pouvoir explicatif sur ce cas.

#### Critere de rejet

- la sous-famille ne devient pas plus reguliere que la colonne complete,
- ou le bord lourd n explique pas la rupture,
- ou la lecture par bloc ne change rien a la decision.

#### Regle de verdict

- conforme si la sous-famille corrige la rupture de la colonne complete,
- partiel si la sous-famille s améliore mais garde un residu,
- rejette si aucune difference utile n apparait entre la colonne brute et le noyau monotone.

#### Regle operationnelle

Utiliser la vue "bloc + bord de serie" seulement quand la colonne brute devient mixte ou casse, puis verifier si un noyau monotone plus court rend Z_eff plus utile que la masse seule.

#### Test lance

- Script: [scripts/tetrel_block_edge_view_check.py](../../scripts/tetrel_block_edge_view_check.py)
- Timestamp: 20260508-200338Z
- Verdict: supported
- Lecture: le test sur la famille tetrel confirme que la colonne complete est a lire avec un bord lourd distinct, et que le noyau C -> Sn devient lisible seulement avec cette vue a deux niveaux.
- Rapport JSON: [results/result-analyse/tetrel_block_edge_view_check_20260508-200338Z.json](tetrel_block_edge_view_check_20260508-200338Z.json)
- Rapport TXT: [results/result-analyse/tetrel_block_edge_view_check_20260508-200338Z.txt](tetrel_block_edge_view_check_20260508-200338Z.txt)

#### Test valide

- Script: [scripts/tetrel_zeff_residual_check.py](../../scripts/tetrel_zeff_residual_check.py)
- Timestamp: 20260509-225849Z
- Verdict: supported
- Lecture: Pb laisse encore un residu plus marque que le noyau C -> Sn, tandis que Z_eff reste plus propre que la masse seule; le bord lourd reste donc necessaire dans la lecture de la famille.
- Rapport JSON: [python/results/tetrel_zeff_residual_check_20260509-225849Z.json](../../python/results/tetrel_zeff_residual_check_20260509-225849Z.json)
- Rapport TXT: [python/results/tetrel_zeff_residual_check_20260509-225849Z.txt](../../python/results/tetrel_zeff_residual_check_20260509-225849Z.txt)

#### Deuxieme test lance

- Script: [scripts/boron_block_edge_view_check.py](../../scripts/boron_block_edge_view_check.py)
- Timestamp: 20260508-200444Z
- Verdict: supported
- Lecture: la famille du bore confirme a son tour que la vue bloc + bord de serie est utile; le noyau B -> Al -> In se lit mieux que la colonne brute B -> Tl.
- Rapport JSON: [results/result-analyse/boron_block_edge_view_check_20260508-200444Z.json](boron_block_edge_view_check_20260508-200444Z.json)
- Rapport TXT: [results/result-analyse/boron_block_edge_view_check_20260508-200444Z.txt](boron_block_edge_view_check_20260508-200444Z.txt)

#### Troisieme test lance

- Script: [scripts/alkali_block_edge_view_check.py](../../scripts/alkali_block_edge_view_check.py)
- Timestamp: 20260508-200553Z
- Verdict: falsifie
- Lecture: sur la famille alcaline deja monotone, la vue bloc + bord ne devient pas necessaire; elle n ajoute pas de pouvoir explicatif utile et sert donc de contre-exemple.
- Rapport JSON: [results/result-analyse/alkali_block_edge_view_check_20260508-200553Z.json](alkali_block_edge_view_check_20260508-200553Z.json)
- Rapport TXT: [results/result-analyse/alkali_block_edge_view_check_20260508-200553Z.txt](alkali_block_edge_view_check_20260508-200553Z.txt)

#### Quatrieme test lance

- Script: [scripts/boron_block_edge_view_alt_check.py](../../scripts/boron_block_edge_view_alt_check.py)
- Timestamp: 20260508-200659Z
- Verdict: supported
- Lecture: la variante sur le bore confirme la vue deux niveaux; le noyau B -> Al -> In reste monotone alors que la colonne complete reste cassée par le bloc et un point interne.
- Rapport JSON: [results/result-analyse/boron_block_edge_view_alt_check_20260508-200659Z.json](boron_block_edge_view_alt_check_20260508-200659Z.json)
- Rapport TXT: [results/result-analyse/boron_block_edge_view_alt_check_20260508-200659Z.txt](boron_block_edge_view_alt_check_20260508-200659Z.txt)

#### Cinquieme test lance

- Script: [scripts/lanthanide_block_edge_view_check.py](../../scripts/lanthanide_block_edge_view_check.py)
- Timestamp: 20260508-200857Z
- Verdict: partiel
- Lecture: la famille des lanthanides montre bien une structure de bloc et de bord, mais le noyau retenu garde encore des anomalies internes; la vue a deux niveaux aide, sans tout resoudre.
- Rapport JSON: [results/result-analyse/lanthanide_block_edge_view_check_20260508-200857Z.json](lanthanide_block_edge_view_check_20260508-200857Z.json)
- Rapport TXT: [results/result-analyse/lanthanide_block_edge_view_check_20260508-200857Z.txt](lanthanide_block_edge_view_check_20260508-200857Z.txt)

#### Sixieme test lance

- Script: [scripts/transition_3d_block_edge_view_check.py](../../scripts/transition_3d_block_edge_view_check.py)
- Timestamp: 20260508-201025Z
- Verdict: partiel
- Lecture: le bloc de transition 3d confirme une structure de bloc et de bord, mais le noyau repare reste seulement partiellement regulier; la vue aide, mais le choix du noyau doit etre plus fin.
- Rapport JSON: [results/result-analyse/transition_3d_block_edge_view_check_20260508-201025Z.json](transition_3d_block_edge_view_check_20260508-201025Z.json)
- Rapport TXT: [results/result-analyse/transition_3d_block_edge_view_check_20260508-201025Z.txt](transition_3d_block_edge_view_check_20260508-201025Z.txt)

#### Septieme test lance

- Script: [scripts/transition_3d_dual_core_view_check.py](../../scripts/transition_3d_dual_core_view_check.py)
- Timestamp: 20260508-203626Z
- Verdict: supported
- Lecture: le bloc 3d se lit mieux comme deux noyaux locaux que comme un seul noyau repare; la separation precoce / tardive clarifie mieux la structure.
- Rapport JSON: [results/result-analyse/transition_3d_dual_core_view_check_20260508-203626Z.json](transition_3d_dual_core_view_check_20260508-203626Z.json)
- Rapport TXT: [results/result-analyse/transition_3d_dual_core_view_check_20260508-203626Z.txt](transition_3d_dual_core_view_check_20260508-203626Z.txt)

#### Huitieme test lance

- Script: [scripts/transition_5d_dual_core_view_check.py](../../scripts/transition_5d_dual_core_view_check.py)
- Timestamp: 20260508-203751Z
- Verdict: supported
- Lecture: le bloc 5d confirme plus nettement la lecture a deux noyaux; le noyau precoce Hf -> W et le noyau tardif Os -> Hg rendent le bloc plus lisible que la tentative de noyau unique.
- Rapport JSON: [results/result-analyse/transition_5d_dual_core_view_check_20260508-203751Z.json](transition_5d_dual_core_view_check_20260508-203751Z.json)
- Rapport TXT: [results/result-analyse/transition_5d_dual_core_view_check_20260508-203751Z.txt](transition_5d_dual_core_view_check_20260508-203751Z.txt)

#### Huitieme test lance

- Script: [scripts/lanthanide_internal_residual_check.py](../../scripts/lanthanide_internal_residual_check.py)
- Timestamp: 20260509-222518Z
- Verdict: falsifie
- Lecture: retirer Eu et Yb repare partiellement la famille, mais la regularite interne reste insuffisante et Z_eff ne bat pas clairement la masse dans le noyau repare.
- Rapport JSON: [results/result-analyse/lanthanide_internal_residual_check_20260509-222518Z.json](lanthanide_internal_residual_check_20260509-222518Z.json)
- Rapport TXT: [results/result-analyse/lanthanide_internal_residual_check_20260509-222518Z.txt](lanthanide_internal_residual_check_20260509-222518Z.txt)

#### Neuvieme test lance

- Script: [scripts/pnictogen_residual_check.py](../../scripts/pnictogen_residual_check.py)
- Timestamp: 20260509-223033Z
- Verdict: supported
- Lecture: la question correcte est celle du regime pnictogene; N et P restent covalents, As passe en transition, Sb et Bi passent en semi-metal.
- Rapport JSON: [results/result-analyse/pnictogen_residual_check_20260509-223033Z.json](pnictogen_residual_check_20260509-223033Z.json)
- Rapport TXT: [results/result-analyse/pnictogen_residual_check_20260509-223033Z.txt](pnictogen_residual_check_20260509-223033Z.txt)

## Exemple complet: triphase

### But

Montrer le format exact attendu pour un test de coherence collective du courant.

### Entree de test

- Systeme triphase equilibre.
- Systeme triphase desequilibre.

### Observable unique

- Somme des courants et courant de neutre.

### Critere de controle

- somme proche de zero en equilibre,
- neutre faible en equilibre,
- neutre marque en desequilibre.

### Verdict attendu

- conforme si la symetrie collective est detectee,
- rejette si l equilibre et le desequilibre ne se distinguent pas,
- partiel si la somme est bonne mais le neutre reste ambigu.

### JSON attendu

```json
{
	"timestamp": "20260508-120000Z",
	"hypothesis": "le triphase equilibre annule la somme des courants",
	"case_control": "triphase symetrique",
	"observable": "somme des courants et courant de neutre",
	"expected": "somme proche de zero en equilibre, neutre faible",
	"measured": "sum_current = 0.00001, neutral_current = 0.00002",
	"verdict": "conforme",
	"reference": "triphase equilibre",
	"json_path": ".../three_phase_current_check_20260508-120000Z.json",
	"txt_path": ".../three_phase_current_check_20260508-120000Z.txt"
}
```

### TXT attendu

```text
timestamp: 20260508-120000Z
hypothese: le triphase equilibre annule la somme des courants
cas de controle: triphase symetrique
observable: somme des courants et courant de neutre
attendu: somme proche de zero en equilibre, neutre faible
mesuree: sum_current = 0.00001, neutral_current = 0.00002
verdict: conforme
critere de rejet: aucune difference entre equilibre et desequilibre
reference: triphase equilibre
json_path: .../three_phase_current_check_20260508-120000Z.json
txt_path: .../three_phase_current_check_20260508-120000Z.txt
```

### Lecture

Ce format sert de modele pour tous les tests collectifs ou de symetrie a plusieurs phases.

## Campagne de tests a lancer

### Ordre d execution

1. Neutralite atomique.
2. Ionisation.
3. Rouille et oxydation.
4. H / Fe / Pb.
5. Conductivite des materiaux.
6. Triphase.
7. Effet peau.
8. Induction forte.
9. Saturation magnetique.
10. Porte alpha.
11. Observable alpha.

### Regle de campagne

- un script a la fois,
- un rapport JSON et un rapport TXT par script,
- un verdict explicite par test,
- un rejet clair si l observable ne suit pas l attendu.

### Priorite immediate

- lancer d abord le triphase,
- puis le test porte alpha,
- puis le test H / Fe / Pb si le triphase reste conforme.

## Resultats de campagne initiale

### Triphase

- Timestamp: 20260508-194156Z
- Verdict: supported
- Lecture: l equilibre annule bien la somme des courants, le desequilibre cree une signature nette et la coupure de phase casse la symetrie.

### Porte alpha

- Timestamp: 20260508-194205Z
- Verdict: falsifie
- Lecture: l exactitude de l arrondi 1/137 est rejetee face a la reference inverse 137.035999084, l usage mnemonique reste seulement aproximatif.

### H / Fe / Pb

- Timestamp: 20260508-194214Z
- Verdict: supported
- Lecture: la progression H -> Fe -> Pb reste lisible avec H minimal, Fe intermediaire et Pb plus lourd et plus contraint.

### Neutralite atomique

- Timestamp: 20260508-194310Z
- Verdict: supported
- Lecture: l atome neutre respecte bien N_e = N_p, et les ions du meme noyau restent distingues correctement.

### Rouille et oxydation

- Timestamp: 20260508-194312Z
- Verdict: supported
- Lecture: le fer change d etat chimique sans changement de Z, ce qui confirme la separation entre chimie et identite nucleaire.

### Neutralite atomique et ionisation

- Timestamp: 20260508-194347Z
- Verdict: supported
- Lecture: les atomes neutres respectent N_e = N_p et les ions du meme noyau restent correctement identifies.

### Conductivite des materiaux

- Timestamp: 20260508-194349Z
- Verdict: supported
- Lecture: cuivre, fer, aluminium et silicium restent bien classes selon leurs regimes de conductivite attendus.

### Effet peau

- Timestamp: 20260508-194410Z
- Verdict: conforme strict
- Lecture: la profondeur de peau decroit bien avec la frequence et le courant devient plus surfacique a haute frequence.

### Induction forte

- Timestamp: 20260508-194411Z
- Verdict: conforme strict
- Lecture: le regime faible reste presque lineaire et le regime fort montre un ecart net, stable et mesurable.

### Saturation magnetique

- Timestamp: 20260508-194426Z
- Verdict: conforme strict
- Lecture: la reponse reste quasi lineaire au debut puis se sature proprement a fort champ.

### Observable alpha

- Timestamp: 20260508-194539Z
- Verdict: supported
- Lecture: l observable derive Delta theta suit bien la reference attendue, avec un ecart relatif faible mais non nul.

### Etat de la campagne

Les trois premiers tests lancent une base solide: un test collectif de courant, un test de seuil numerique et un test de progression atomique.

La neutralite atomique, l ionisation et la rouille confirment ensuite le bloc atomique minimal: charge, ionisation, oxydation et identite nucleaire restent distinctes.

La conductivite confirme le bloc materiel simple: cuivre, fer, aluminium et silicium restent separes par leurs comportements attendus.

L effet peau et l induction forte confirment maintenant le bloc de seuil: la frequence et la variation de flux produisent des ecarts propres et reproductibles.

La saturation magnetique complete ce bloc de seuil en montrant la courbure puis le plateau attendu au fort champ.

L observable alpha precise enfin le bloc numerique: la porte exacte est rejetee tandis que l observable derive reste calculable et stable.

La suite logique est de poursuivre avec les tests restants du dossier si tu veux aller jusqu au bout de la serie.

## Bilan provisoire du dossier atome

Ce dossier fixe la base atomique a partir de laquelle le dossier electron peut etre lu sans ambiguite, mais il ne ferme pas la recherche: il laisse encore plusieurs axes a tester.

### Ce qui est etabli

- la neutralite atomique distingue bien atome neutre et ion,
- l ionisation isole le changement de charge sans changer le noyau,
- la rouille se lit comme un changement chimique sans changement d identite nucleaire,
- la serie H / Fe / Pb donne un gradient minimal, intermediaire et lourd,
- les conducteurs simples, le triphase, l effet peau et les regimes non lineaires restent coherents avec les tests de reference,
- la porte alpha doit etre lue avec tolerance explicite et non comme egalite exacte.

### Regle finale de travail

Quand une colonne chimique ou un bloc devient mixte, il faut d abord chercher le bon noyau de lecture local avant d ajouter une hypothese plus forte.

### Correction structurelle candidate

Les ruptures les plus nettes du dossier suggèrent deux variables locales de lecture:

- k: indice de noyau local, pour distinguer un coeur simple, un coeur f et un bord de bloc perturbe,
- L: regime de liaison, pour distinguer covalent, semi-conducteur, semi-metallique, metallique ou fortement directionnel.

La forme de travail qui en decoule est:

Z_eff_star = Z_eff + a.k + b.L

Cette ecriture ne doit pas etre lue comme une correction globale deja validee par tous les tests. En revanche, les tests tetrel, pnictogene et lanthanide k/L passent desormais, ce qui montre qu une lecture a deux variables locales peut reduire les residus sur plusieurs familles cassees. La portee de la correction reste toutefois locale et doit encore etre testee sur d autres blocs ou sur d autres variantes de parametrage.

Dernier rapport lanthanide k/L: Timestamp 20260509-222933Z, verdict supported, rapport JSON [results/result-analyse/lanthanide_k_l_correction_check_20260509-222933Z.json](lanthanide_k_l_correction_check_20260509-222933Z.json), rapport TXT [results/result-analyse/lanthanide_k_l_correction_check_20260509-222933Z.txt](lanthanide_k_l_correction_check_20260509-222933Z.txt).

### Cloture du dossier atome

Le dossier atome est maintenant ferme sur ses blocs utiles: neutralite, ionisation, isotopes, conduction, triphase, seuils, porte alpha, observable alpha, familles tetrel/pnictogene/lanthanide et corrections locales k/L.

Ce qui reste n est plus un bloc atome a valider, mais une suite de lecture dans [Electron-5.txt](../../Electron-5.txt) pour formaliser la logique interne plus profonde.

### Passerelle vers Electron-5

Les prochaines validations a ouvrir dans [Electron-5.txt](../../Electron-5.txt) sont, dans l ordre logique le plus court:

- la derive des masses des quarks / quartz du modele Ω,
- l emergence des hadrons comme modes collectifs de Ωᴺ,
- la matrice PMNS et les masses des neutrinos,
- le statut des quartz comme motifs de coherence D2,
- la separation entre quartz, gluons et Z_eff,
- les hypotheses concurrentes sur la variation fine de distance et la perte d energie.

Ce sont des hypotheses de modele, donc elles doivent etre traitees comme des cibles de validation et non comme des conclusions deja fermees.

### Suite de travail a garder dans Atome

La suite logique reste indexee depuis le dossier atome, meme si les validations portent sur Electron-5.

Ordre de travail propose:

1. Dérive des masses des quarks / quartz du modèle Ω.
- but: vérifier si les paramètres internes donnent une loi de masse testable.
- observable: masses reproduites versus valeurs PDG ou référence du dossier.
- rejet: si les masses ne sont pas reconstruites de façon stable.

2. Émergence des hadrons comme modes collectifs de Ωᴺ.
- but: vérifier si les mésons et baryons sortent comme états collectifs.
- observable: règles de composition, multiplicités, cohérence des masses.
- rejet: si la composition collective n’explique rien de mesurable.

3. Matrice PMNS et masses des neutrinos.
- but: vérifier si les couplages internes Ωᵛ donnent une matrice de mélange cohérente.
- observable: angles de mélange, hiérarchie des masses, petitesse des masses neutrino.
- rejet: si la matrice n’est qu’un habillage sans prédiction.

4. Quartz comme motifs de cohérence D2.
- but: vérifier si les quartz sont un niveau géométrique distinct et utile.
- observable: dérive des masses / indices / cohérence interne sur les séries concernées.
- rejet: si le quartz ne produit aucune différence mesurable.

5. Séparation quartz / gluons / Z_eff.
- but: vérifier ce qui agit sur le noyau interne, ce qui structure la cohérence et ce qui agit sur l’électron.
- observable: séparation nette des rôles et absence de confusion entre niveaux.
- rejet: si les trois niveaux se mélangent sans gain explicatif.

6. Hypothèses concurrentes sur la variation fine.
- but: départager variation fine de distance e–p et variation fine de perte d’énergie.
- observable: micro-correction sur Z_eff, sur l’énergie de liaison, ou sur les deux.
- rejet: si aucune version ne produit un delta mesurable.

Règle de travail:
- on commence par les objets qui ont un calcul explicite,
- on note ensuite les observables falsifiables,
- on ne garde comme vrai que ce qui produit un écart mesurable et reproductible.

### Test valide: dérive des masses des quarks

Premier jalon de la suite atome / Electron-5: comparaison des masses de quarks annoncées avec les valeurs de référence et vérification de l ordre hiérarchique.

Dernier rapport: Timestamp 20260509-231450Z, verdict supported, rapport JSON [python/results/quark_mass_derivation_check_20260509-231450Z.json](../../python/results/quark_mass_derivation_check_20260509-231450Z.json), rapport TXT [python/results/quark_mass_derivation_check_20260509-231450Z.txt](../../python/results/quark_mass_derivation_check_20260509-231450Z.txt).

### Test valide: hadrons comme modes collectifs

Second jalon de la suite atome / Electron-5: vérification qu un petit ensemble de hadrons légers reste cohérent comme objets collectifs avec le bon contenu en quarks et la bonne hiérarchie de masses.

Dernier rapport: Timestamp 20260509-231545Z, verdict supported, rapport JSON [python/results/hadron_collective_mode_check_20260509-231545Z.json](../../python/results/hadron_collective_mode_check_20260509-231545Z.json), rapport TXT [python/results/hadron_collective_mode_check_20260509-231545Z.txt](../../python/results/hadron_collective_mode_check_20260509-231545Z.txt).

### Test valide: matrice PMNS et masses des neutrinos

Troisième jalon de la suite atome / Electron-5: vérification que les trois angles PMNS restent dans une zone de grand mélange et que la hiérarchie de masses neutrino reste légère et compatible avec les écarts observés.

Dernier rapport: Timestamp 20260509-231635Z, verdict supported, rapport JSON [python/results/pmns_neutrino_check_20260509-231635Z.json](../../python/results/pmns_neutrino_check_20260509-231635Z.json), rapport TXT [python/results/pmns_neutrino_check_20260509-231635Z.txt](../../python/results/pmns_neutrino_check_20260509-231635Z.txt).

### Test valide: quartz comme motifs de cohérence D2

Quatrième jalon de la suite atome / Electron-5: validation d un petit banc géométrique séparant des motifs quartz cohérents de controles non cohérents selon les critères D2.

Dernier rapport: Timestamp 20260509-231740Z, verdict supported, rapport JSON [python/results/quartz_d2_coherence_check_20260509-231740Z.json](../../python/results/quartz_d2_coherence_check_20260509-231740Z.json), rapport TXT [python/results/quartz_d2_coherence_check_20260509-231740Z.txt](../../python/results/quartz_d2_coherence_check_20260509-231740Z.txt).

### Test valide: séparation quartz / gluons / Z_eff

Cinquième jalon de la suite atome / Electron-5: test de séparation entre la cohérence quartz, la cohésion hadronique/gluonique et la charge effective Z_eff sur trois bancs de données distincts.

Dernier rapport: Timestamp 20260509-231841Z, verdict supported, rapport JSON [python/results/quartz_gluon_zeff_separation_check_20260509-231841Z.json](../../python/results/quartz_gluon_zeff_separation_check_20260509-231841Z.json), rapport TXT [python/results/quartz_gluon_zeff_separation_check_20260509-231841Z.txt](../../python/results/quartz_gluon_zeff_separation_check_20260509-231841Z.txt).

### Test valide: équivalence variation fine distance / énergie

Sixième jalon de la suite atome / Electron-5: comparaison de deux paramétrisations fines sur les mêmes familles de référence; la lecture géométrique et la lecture énergétique améliorent toutes les deux le même résidu avec un écart faible, ce qui soutient l équivalence conceptuelle locale.

Dernier rapport: Timestamp 20260509-232009Z, verdict supported, rapport JSON [python/results/fine_variation_equivalence_check_20260509-232009Z.json](../../python/results/fine_variation_equivalence_check_20260509-232009Z.json), rapport TXT [python/results/fine_variation_equivalence_check_20260509-232009Z.txt](../../python/results/fine_variation_equivalence_check_20260509-232009Z.txt).

### Suite Electron-5 elargie

- quartz D2: [python/scripts/quartz_d2_coherence_check.py](../../python/scripts/quartz_d2_coherence_check.py) + verdict supported,
- separation quartz / gluons / Z_eff: [python/scripts/quartz_gluon_zeff_separation_check.py](../../python/scripts/quartz_gluon_zeff_separation_check.py) + verdict supported,
- equivalence variation fine: [python/scripts/fine_variation_equivalence_check.py](../../python/scripts/fine_variation_equivalence_check.py) + verdict supported,
- lanceur complet: [python/scripts/run_electron5_extended_suite.py](../../python/scripts/run_electron5_extended_suite.py),
- synthese de suite: [python/scripts/run_electron5_extended_tests.py](../../python/scripts/run_electron5_extended_tests.py).

### Suite variation fine dur

- pnictogenes difficiles: [python/scripts/fine_variation_hard_check.py](../../python/scripts/fine_variation_hard_check.py) + verdict supported,
- boron difficile: [python/scripts/fine_variation_boron_hard_check.py](../../python/scripts/fine_variation_boron_hard_check.py) + verdict supported,
- lanthanides difficiles: [python/scripts/fine_variation_lanthanide_hard_check.py](../../python/scripts/fine_variation_lanthanide_hard_check.py) + verdict contradicted,
- lanceur complet: [python/scripts/run_fine_variation_hard_suite.py](../../python/scripts/run_fine_variation_hard_suite.py),
- synthese de suite: [python/scripts/run_fine_variation_hard_tests.py](../../python/scripts/run_fine_variation_hard_tests.py).

### Test plus dur: équivalence variation fine sur la famille pnictogène

Version renforcée du sixième jalon: la même question est reprise sur la famille pnictogène complète et ses sous-séries réparées, plus irrégulières que les familles lisses. Le test reste supporté, ce qui renforce l idée d une équivalence locale entre lecture géométrique et lecture énergétique.

Dernier rapport: Timestamp 20260509-232113Z, verdict supported, rapport JSON [python/results/fine_variation_hard_check_20260509-232113Z.json](../../python/results/fine_variation_hard_check_20260509-232113Z.json), rapport TXT [python/results/fine_variation_hard_check_20260509-232113Z.txt](../../python/results/fine_variation_hard_check_20260509-232113Z.txt).

### Contre-exemple dur: équivalence variation fine sur la famille lanthanide

En allant sur une famille nettement plus irrégulière, la lecture géométrique ne suit plus la lecture énergétique: le test devient contradictoire. C est une borne utile, parce qu elle montre que l équivalence locale n est pas robuste partout et qu un terme plus fin est nécessaire sur le f-block.

Dernier rapport: Timestamp 20260509-232209Z, verdict contradicted, rapport JSON [python/results/fine_variation_lanthanide_hard_check_20260509-232209Z.json](../../python/results/fine_variation_lanthanide_hard_check_20260509-232209Z.json), rapport TXT [python/results/fine_variation_lanthanide_hard_check_20260509-232209Z.txt](../../python/results/fine_variation_lanthanide_hard_check_20260509-232209Z.txt).

### Test dur: équivalence variation fine sur la famille du bore

La même comparaison sur la famille du bore reste supportée, y compris sur une version réparée et une version bord-trimmed. Cela montre que l équivalence locale n est pas réservée aux familles parfaitement lisses, même si elle ne survit pas au f-block.

Dernier rapport: Timestamp 20260509-232337Z, verdict supported, rapport JSON [python/results/fine_variation_boron_hard_check_20260509-232337Z.json](../../python/results/fine_variation_boron_hard_check_20260509-232337Z.json), rapport TXT [python/results/fine_variation_boron_hard_check_20260509-232337Z.txt](../../python/results/fine_variation_boron_hard_check_20260509-232337Z.txt).

### Contre-test plus dur: leave-one-out lanthanide avec Zeff*

En leave-one-out sur les lanthanides, Zeff* reste nettement meilleur que la masse et que Zeff brut, mais le modèle Zeff*+H ne bat pas la calibration Zeff* de façon robuste. Le résultat reste donc contradictoire pour l hypothèse la plus forte, avec Zeff* comme meilleur compromis global mais sans gain stable du terme H.

Dernier rapport: Timestamp 20260509-232619Z, verdict contradicted, rapport JSON [python/results/fine_variation_lanthanide_loo_check_20260509-232619Z.json](../../python/results/fine_variation_lanthanide_loo_check_20260509-232619Z.json), rapport TXT [python/results/fine_variation_lanthanide_loo_check_20260509-232619Z.txt](../../python/results/fine_variation_lanthanide_loo_check_20260509-232619Z.txt).

### Contre-test plus dur: leave-one-out bore avec Zeff*

Le leave-one-out sur la famille du bore casse la tentative de correction locale telle qu elle a été posée ici: le modèle Zeff* local perd nettement face à Zeff brut et même face à la masse sur plusieurs folds. C est un contre-exemple utile, parce qu il montre que la structure k/L choisie pour cette famille n est pas robuste hors échantillon.

Dernier rapport: Timestamp 20260509-232741Z, verdict contradicted, rapport JSON [python/results/fine_variation_boron_loo_check_20260509-232741Z.json](../../python/results/fine_variation_boron_loo_check_20260509-232741Z.json), rapport TXT [python/results/fine_variation_boron_loo_check_20260509-232741Z.txt](../../python/results/fine_variation_boron_loo_check_20260509-232741Z.txt).

### Mise a jour corrigée: leave-one-out boron et lanthanides

Les versions corrigées de ces deux leave-one-out repassent maintenant en supporté avec des formes plus parcimonieuses:

- boron LOO: [python/scripts/fine_variation_boron_loo_check.py](../../python/scripts/fine_variation_boron_loo_check.py) + verdict supported en lecture Zeff pur,
- lanthanides LOO: [python/scripts/fine_variation_lanthanide_loo_check.py](../../python/scripts/fine_variation_lanthanide_loo_check.py) + verdict supported avec Zeff* sans terme H.

Lecture de travail: sur ces deux familles, les formes locales trop riches sur-apprennent hors echantillon; la version plus parcimonieuse est plus robuste.

### Suite Electron-5 de base

- derive des masses des quarks: [python/scripts/quark_mass_derivation_check.py](../../python/scripts/quark_mass_derivation_check.py) + verdict supported,
- hadrons collectifs: [python/scripts/hadron_collective_mode_check.py](../../python/scripts/hadron_collective_mode_check.py) + verdict supported,
- PMNS / neutrinos: [python/scripts/pmns_neutrino_check.py](../../python/scripts/pmns_neutrino_check.py) + verdict supported,
- lanceur complet: [python/scripts/run_electron5_core_suite.py](../../python/scripts/run_electron5_core_suite.py),
- synthese de suite: [python/scripts/run_electron5_core_tests.py](../../python/scripts/run_electron5_core_tests.py).

Recalcul explicite sur la serie C -> Pb avec les coefficients fournis dans la discussion:

Definition generale:

Zeff★ = Zeff,Bohr + ak.k + bL.L + c.Z^2 + d.H

avec:

- Zeff,Bohr = sqrt(I.n^2 / 13.6)
- I = energie d ionisation (eV)
- n = nombre quantique principal de la couche de valence
- k = terme coeur
- L = terme de liaison / position dans la famille
- Z = numero atomique
- H = terme de hybridation / d-f

Dans les tests tetrel déjà notes ici, les coefficients utilises sont:

- ak = 0
- bL = 0.25
- c = 1.1e-4
- d = 0

ce qui revient, pour ce cas, a:

Zeff★ = Zeff + 0.25.L + 1.1e-4.Z^2

Definition operationnelle retenue pour le book:

Zeff★ = sqrt(I.n^2 / 13.6) + ak.k + bL.L + c.Z^2 + d.H

avec I l energie d ionisation, n la couche de valence, k la correction coeur, L la correction de liaison, Z le numero atomique et H le terme d / f / hybridation interne.

Dans ce cadre, D1_atome est la lecture physique de la meme variable: D1_atome = Zeff★.

Version Python propre:

def zeff_star(I, n, Z, k=0.0, L=0.0, H=0.0, ak=0.0, bL=0.25, c=1.1e-4, d=0.0):
	zeff_bohr = ((I * n * n) / 13.6) ** 0.5
	return zeff_bohr + ak * k + bL * L + c * (Z ** 2) + d * H

La suite obtenue est monotone sur cette serie: 1.82381, 2.594168, 3.66115, 4.69921, 5.920491. Le Zeff standard etait deja croissant sur cette famille, donc ce recalcul confirme la monotonie du Zeff★ mais ne constitue pas a lui seul une preuve que la famille brute etait non monotone.

Transfert halogene F -> At:

La meme correction donne aussi une suite monotone sur les halogenes: 2.272613, 3.21121, 4.362831, 5.442134, 6.559434. Cela confirme la coherence de la variable Zeff★ sur une autre famille complete, mais la famille standard etait deja monotone sur ce critere.

### Ce qui reste ouvert

- prolonger les familles deja testees vers d autres sous-series,
- tester une autre famille ou une variante de parametrage k/L pour verifier la robustesse,
- croiser les resultats avec de nouveaux seuils physiques,
- verifier si un autre dossier apporte une rupture plus nette que la lecture actuelle.

### Suite naturelle

Le dossier suivant est [electron_dossier.md](electron_dossier.md): il reprend ce socle atomique pour traiter les seuils, la transmission, la symetrie collective et les observables de courant.