# Protocole V10

## Vue d'ensemble

V10 est la version ou le modele atomique devient dynamique. Il relie l'atome individuel, les etats excites, l'ionisation et les regimes critiques.

Il se compose de trois modules:

- V10-ION: ionisation et etats critiques.
- V10-SPECTRE: series spectrales et corrections torsionnelles.
- V10-RYDBERG: etats de Rydberg et geometrie D2.

Le wrapper global est `v10atomdynamics_suite`.

## Fichiers ajoutes

- python/scripts/v10ion_check.py
- python/scripts/v10spectre_check.py
- python/scripts/v10rydberg_check.py
- python/scripts/run_v10atomdynamics_suite.py
- python/tests/test_v10ion_check.py
- python/tests/test_v10spectre_check.py
- python/tests/test_v10rydberg_check.py
- python/tests/test_v10atomdynamics_suite.py

## V10-ION

Hypothese testee: le seuil d'ionisation effective depend du champ alpha, de la torsion D2, de la reponse electronique et de la stabilite atomique.

Forme operationnelle:

- E_ion_eff(Z) = E_ion_ref(Z) - DeltaE_torsion(Z) + DeltaE_coupling(Z)
- E_ion_ref(Z) = proxy lisse centre sur Fe
- DeltaE_torsion(Z) = module V8-LEVEL
- DeltaE_coupling(Z) = correction de zone stable centre sur Fe

Resultats runtime:

- peak_z = 26
- peak_value = 29.695288756463523 eV
- Z_ion_crit = 30

Cas testes:

- H
- He
- Fe
- Pb
- U

Verdict: conforme.

Lecture:

- l'ionisation effective atteint son maximum autour de Fe.
- la courbe decroit ensuite vers la queue lourde.
- Z_ion_crit tombe dans la bande attendue 30-40.

## V10-SPECTRE

Hypothese testee: la torsion D2 et la porte alpha modifient legerement les niveaux atomiques et leurs series spectrales.

Forme operationnelle:

- E_n = -RZ / n^2
- Delta E_n^torsion = Delta_phi(Z) * tau(r_n)
- tau(r_n) = alpha / r_n
- r_n = n^2 a0

Resultats runtime:

- H: n=2 -> 9.924973653912901e-06 eV, n=6 -> 1.1027748504347668e-06 eV
- He: n=2 -> 1.9849947307825803e-05 eV, n=6 -> 2.2055497008695336e-06 eV
- Fe: n=2 -> 2.5804931500173544e-04 eV, n=6 -> 2.867214611130394e-05 eV
- Pb: n=2 -> 8.13847839620858e-04 eV, n=6 -> 9.04275377356509e-05 eV
- U: n=2 -> 9.13097576159987e-04 eV, n=6 -> 1.0145528623999856e-04 eV

Verdict: conforme.

Lecture:

- les corrections diminuent en 1/n^2.
- toutes les amplitudes restent dans la bande 10^-6 a 10^-3 eV.
- la sensibilite croît avec Z.

## V10-RYDBERG

Hypothese testee: les etats tres excites amplifient les effets geometriques D2 sans divergence.

Forme operationnelle:

- r_n = n^2 a0
- delta r_n = r_n(alpha_ref) - r_n(alpha_approx)
- alpha_approx = alpha_ref - gap(n)
- gap(n) croît doucement avec n

Resultats runtime:

- n=2: delta r_n = 3.893766662840026e-03, deviation relative = 1.839538879637638e-03
- n=4: delta r_n = 2.280290096007498e-02, deviation relative = 2.6932034272175213e-03
- n=8: delta r_n = 1.2460053321087372e-01, deviation relative = 3.6790777592750666e-03
- n=16: delta r_n = 6.437787728054616e-01, deviation relative = 4.752211134027621e-03
- n=32: delta r_n = 3.187079015797849e+00, deviation relative = 5.8815516384217136e-03
- n=64: delta r_n = 1.5282813115213685e+01, deviation relative = 7.050864919878351e-03

Verdict: conforme.

Lecture:

- delta r_n croît avec n.
- la deviation relative reste largement sous 1%.
- la signature geometrique reste controlee et cohérente avec V7-GEO.

## Suite v10atomdynamics_suite

Resultat attendu:

- suite = v10atomdynamics_suite
- total = 3
- supported_count = 3
- overall_verdict = supported

Resultat runtime:

- overall_verdict = supported
- supported_count = 3
- total = 3

## Integration dans point_atome_master

V10 remonte dans la pile atomique de master comme un niveau supplementaire visible.

Resultat attendu apres integration:

- point_atome_master total = 8
- point_atome_master supported_count = 8
- overall_verdict = supported

## Resultats de test

- test_v10ion_check.py: passe
- test_v10spectre_check.py: passe
- test_v10rydberg_check.py: passe
- test_v10atomdynamics_suite.py: passe
- test_point_atome_master_suite.py: passe

## Compte rendu de tests

### Tests unitaires V10

Validation focale lancee sur les cinq fichiers de test suivants:

- `python/tests/test_v10ion_check.py`
- `python/tests/test_v10spectre_check.py`
- `python/tests/test_v10rydberg_check.py`
- `python/tests/test_v10atomdynamics_suite.py`
- `python/tests/test_point_atome_master_suite.py`

Resultat runtime: 10 tests passes.

### Bilan

- V10-ION fixe un Z_ion_crit dans la bande 30-40 avec maximum autour de Fe.
- V10-SPECTRE conserve des corrections faibles et ordonnees.
- V10-RYDBERG amplifie les deviations geometriques sans divergence.
- `v10atomdynamics_suite` est supported sur 3/3.
- `point_atome_master` reste supported apres integration de V10.