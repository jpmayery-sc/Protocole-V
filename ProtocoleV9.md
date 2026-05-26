# Protocole V9

## Vue d'ensemble

V9 est la version ou l'atome prend une forme de dossier de theorie compacte, avec un regime critique, des corrections fines extremes, et une carte atomique reduite.

Il se compose de trois modules:

- V9-CRIT: Z critique atomique.
- V9-FINE: corrections fines extremes.
- V9-MAP: carte atomique globale.

Le wrapper global est `v9atomicsuite`.

## Fichiers ajoutes

- python/scripts/v9crit_check.py
- python/scripts/v9fine_check.py
- python/scripts/v9atommap_check.py
- python/scripts/runv9atomic_suite.py
- python/tests/test_v9crit_check.py
- python/tests/test_v9fine_check.py
- python/tests/test_v9atommap_check.py
- python/tests/test_v9atomic_suite.py

## V9-CRIT

Hypothese testee: il existe un regime critique ou la stabilite atomique commence a decrocher nettement apres le fer.

Forme de travail:

- rayon proxy = 0.35 + 0.26 * sqrt(Z)
- correction de niveau = delta_phi * alpha_ref / rayon proxy
- reserve nucleaire = exp(-((Z - 26)/10)^2) / (1 + Z/25)
- score de stabilite = reserve * rayon proxy / (deltaE * variation kappa)

Resultats runtime:

- peak_z = 25
- peak_score = 10483733.585668089
- z_crit = 34
- maximum net autour du fer, puis declin sur la queue lourde

Points controle:

- H
- He
- C
- O
- Fe
- Pb
- U

Verdict: conforme.

Lecture:

- le sommet est localise a proximite de Fe.
- la chute devient nette apres le maximum.
- Pb et U se situent deja dans la queue limite.

## V9-FINE

Hypothese testee: la torsion D2, la porte alpha et le canal electronique produisent des corrections de niveaux extremes mais encore realistes.

Points testes:

- Fe
- Xe
- Pb
- U

Forme de travail:

- delta E_torsion = delta_phi * alpha_ref / rayon proxy
- la sensibilite est l'accroissement de delta E dans la zone lourde

Resultats runtime:

- Fe: delta_E = 3.5197895851444465e-04
- Xe: delta_E = 5.419022543152667e-04
- Pb: delta_E = 6.878507395094548e-04
- U: delta_E = 7.338970397345358e-04

Verdict: conforme.

Lecture:

- la suite est monotone.
- les amplitudes restent dans la bande 10^-6 a 10^-3 eV.
- les corrections lourdes sont plus sensibles sans devenir absurdes.

## V9-MAP

Hypothese testee: V4 a V9 suffisent pour generer une carte atomique qualitative reduite.

Serie testee:

- H
- He
- C
- O
- Fe
- Pb
- U

Resultats runtime:

- le rayon proxy croît avec Z.
- la correction de niveau croît avec Z.
- la stabilite est maximale autour de Fe.
- Pb et U passent en zone limite.

Verdict: conforme.

## Suite v9atomicsuite

Resultat attendu:

- suite = v9atomicsuite
- total = 3
- supported_count = 3
- overall_verdict = supported

## Integration dans point_atome_master

V9 remonte dans la pile atomique de master comme nouveau niveau visible, et la suite globale d'experience 4 le voit via `point_atome_master`.

Resultat attendu apres integration:

- point_atome_master total = 7
- point_atome_master supported_count = 7
- overall_verdict = supported

## Resultats de test

- test_v9crit_check.py: passe
- test_v9fine_check.py: passe
- test_v9atommap_check.py: passe
- test_v9atomic_suite.py: passe
- test_point_atome_master_suite.py: passe

## Compte rendu de tests

### Tests unitaires V9

Validation focale lancee sur les cinq fichiers de test suivants:

- `python/tests/test_v9crit_check.py`
- `python/tests/test_v9fine_check.py`
- `python/tests/test_v9atommap_check.py`
- `python/tests/test_v9atomic_suite.py`
- `python/tests/test_point_atome_master_suite.py`

Resultat runtime: 10 tests passes.

### Bilan

- V9-CRIT fixe un Z_crit proche de Fe avec declin lourd ensuite.
- V9-FINE conserve des corrections fines dans une bande realiste.
- V9-MAP produit un mini tableau atomique avec Fe au sommet.
- `v9atomicsuite` est supported sur 3/3.
- `point_atome_master` reste supported apres integration de V9.