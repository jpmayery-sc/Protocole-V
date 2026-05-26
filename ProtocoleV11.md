# Protocole V11

## Vue d'ensemble

V11 est la version ou le modele atomique est confronte au redshift comme observable globale.

Il se compose de quatre modules:

- V11-GEO: redshift geometrique D2.
- V11-ATOM: redshift atomique interne.
- V11-CANAL: redshift du canal electronique.
- V11-TOTAL: synthese et preparation a la falsification.

Le wrapper global est `v11redshift_suite`.

## Fichiers ajoutes

- python/scripts/v11geo_check.py
- python/scripts/v11atom_check.py
- python/scripts/v11canal_check.py
- python/scripts/v11total_check.py
- python/scripts/runv11redshiftsuite.py
- python/tests/test_v11geo_check.py
- python/tests/test_v11atom_check.py
- python/tests/test_v11canal_check.py
- python/tests/test_v11total_check.py
- python/tests/test_v11redshift_suite.py

## V11-GEO

Hypothese testee: la torsion D2 induit un redshift geometrique petit mais non nul.

Forme operationnelle:

- phase de reference = base_delta_phi * (1 + 0.01 Z)
- phase environnement = phase_ref + 1.9e-6 * geo_scale * torsion_scale * (1 + Z/120)
- z_geo = (phase_env - phase_ref) / 2pi

Cas testes:

- H_alpha
- Fe_alpha
- Pb_alpha
- U_alpha

Resultats runtime:

- H_alpha: nominal z_geo = 2.4393147611216526e-07
- Fe_alpha: nominal z_geo = 3.679131767807885e-07
- Pb_alpha: nominal z_geo = 6.362881995694561e-07
- U_alpha: nominal z_geo = 7.479221292365444e-07

Verdict: conforme.

Lecture:

- le signe est coherent.
- l'amplitude reste tres faible.
- l'effet croît avec la torsion.

## V11-ATOM

Hypothese testee: les corrections de niveaux internes produisent un redshift atomique petit mais mesurable.

Forme operationnelle:

- DeltaE_ref(Z) = base_delta_phi * Z * alpha_ref / r_eff
- DeltaE_env(Z) = DeltaE_ref(Z) * (1 + 0.025 * atom_scale)
- z_int = (DeltaE_env - DeltaE_ref) / E_transition

Cas testes:

- H
- He
- Fe
- Pb
- U

Resultats runtime:

- H: nominal z_int = 3.9354070719206714e-07
- He: nominal z_int = 5.747095007535248e-07
- Fe: nominal z_int = 3.3521805572804293e-06
- Pb: nominal z_int = 5.854048846888991e-06
- U: nominal z_int = 6.115808664454451e-06

Verdict: conforme.

Lecture:

- l'amplitude reste dans une zone tres faible.
- Fe, Pb et U montent au-dessus de H et He.
- le comportement suit Z sans rupture.

## V11-CANAL

Hypothese testee: la variation relative de κ(n) se lit comme un redshift effectif du canal electronique.

Forme operationnelle:

- z_canal approx (delta kappa / kappa) * 1e-6 * channel_scale * exp(Z/60)

Cas testes:

- H
- Fe
- Pb
- U

Resultats runtime:

- H: nominal z_canal = 8.98645350096726e-07
- Fe: nominal z_canal = 1.1040267160788616e-06
- Pb: nominal z_canal = 2.0923048556515816e-06
- U: nominal z_canal = 2.4717661281133484e-06

Verdict: conforme.

Lecture:

- la suite reste monotone.
- aucune divergence n'apparait.
- l'effet est plus visible dans les regimes lourds.

## V11-TOTAL

Hypothese testee: le redshift total est la somme coherente des trois contributions internes.

Forme operationnelle:

- z_mod = z_geo + z_int + z_canal

Cas testes:

- H
- Fe
- Pb
- U

Resultats runtime:

- H: nominal z_mod = 1.5361175334009585e-06
- Fe: nominal z_mod = 2.0466493936131747e-06
- Pb: nominal z_mod = 6.080773612501467e-06
- U: nominal z_mod = 9.073737104238884e-06

Verdict: conforme.

Lecture:

- le signal total reste petit.
- la structure est ordonnee et testable.
- les cas lourds se detachent clairement.

## V11-FALSIFIER

Hypothese testee: les blocs V11 doivent rester dans des bornes conservatrices pour ne pas etre rejetes par un test de plausibilite.

Bornes de travail:

- V11-GEO: 10^-7 a 2 x 10^-6
- V11-ATOM: 10^-7 a 10^-5
- V11-CANAL: 5 x 10^-7 a 5 x 10^-6
- V11-TOTAL: 10^-6 a 10^-5

Verdict attendu:

- conforme si les quatre blocs restent dans les bornes et gardent une progression monotone
- partiel si la structure est conservee mais qu'un bloc s'ecarte
- falsifie si un bloc sort franchement de la fenetre

Resultat runtime: conforme.

Lecture:

- V11 passe le filtre de plausibilite dans les bornes conservatrices.
- aucune serie nominale ne sort de la fenetre cible.
- ce bloc sert de point de depart avant une future estimation MCMC.

## Suite v11redshift_suite

Resultat attendu:

- suite = v11redshift_suite
- total = 4
- supported_count = 4
- overall_verdict = supported

Resultat runtime:

- overall_verdict = supported
- supported_count = 4
- total = 4

## Integration dans point_atome_master

V11 remonte dans la pile atomique de master comme un nouveau niveau visible.

Resultat attendu apres integration:

- point_atome_master total = 9
- point_atome_master supported_count = 9
- overall_verdict = supported

## Resultats de test

- test_v11geo_check.py: passe
- test_v11atom_check.py: passe
- test_v11canal_check.py: passe
- test_v11total_check.py: passe
- test_v11falsifier_check.py: passe
- test_v11redshift_suite.py: passe
- test_point_atome_master_suite.py: passe

## Compte rendu de tests

### Tests unitaires V11

Validation focale lancee sur les six fichiers de test suivants:

- `python/tests/test_v11geo_check.py`
- `python/tests/test_v11atom_check.py`
- `python/tests/test_v11canal_check.py`
- `python/tests/test_v11total_check.py`
- `python/tests/test_v11falsifier_check.py`
- `python/tests/test_v11redshift_suite.py`
- `python/tests/test_point_atome_master_suite.py`

Resultat runtime: 14 tests passes.

### Bilan

- V11-GEO fournit un redshift geometrique petit et coherent.
- V11-ATOM garde une amplitude faible mais ordonnee.
- V11-CANAL reste monotone et sans divergence.
- V11-FALSIFIER laisse V11 dans les bornes conservatrices.
- `v11redshift_suite` est supported sur 4/4.
- `point_atome_master` reste supported apres integration de V11.