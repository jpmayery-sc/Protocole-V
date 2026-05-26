# Tests a realiser

Cette checklist rassemble les tests a executer pour la nouvelle physique de travail. Elle sert de point de depart pour formaliser les validations par regime sans dupliquer le reste du dossier.

## Validation recente

- lanceur racine [python/scripts/run_regime_tests.py](../../python/scripts/run_regime_tests.py): ok, tous les regimes passent.
- suite pytest [python/tests](../../python/tests): ok, 8 tests passes.
- marqueurs pytest atomique, metal, lanthanide et dense: ok, 2 tests passes par regime et 6 deselectionnes a chaque fois.

## 1. Regime atomique

- [x] verifier que D1 domine clairement D4.
- [x] verifier que D4 reste negligeable sur la grille atomique.
- [x] verifier que le ratio D4 / D1 reste sous 5e-4.
- [x] verifier que la loi de pression brute suit n_e^(5/3).

## 2. Regime metallique

- [x] verifier que D1 reste dominant face a D4.
- [x] verifier que D4 reste dans une bande few-eV.
- [x] verifier que le lanceur route bien vers D1 + D2 + D4.
- [x] verifier que plusieurs cas representatifs restent dans la bande cible.

## 3. Regime des lanthanides

- [x] verifier que D3 est obligatoire.
- [x] verifier qu il n existe pas de reduction D1-only.
- [x] verifier que Ce, Sm, Nd, Gd et Yb sont tous routés vers D1 + D3.
- [x] verifier que la branche lanthanide reste stable dans la suite pytest.

## 4. Regime dense

- [x] verifier le croisement local D1 ~= D4.
- [x] verifier que la balance est continue quand la densite varie.
- [x] verifier que la pression brute suit la loi n_e^(5/3).
- [x] verifier que la grille dense couvre les deux cotes du point d equilibre.

## 5. Lanceurs de test

- [x] verifier [python/scripts/run_regime_tests.py](../../python/scripts/run_regime_tests.py) sur les sous-commandes atomique, metal, lanthanide, dense et all.
- [x] verifier [python/scripts/run_regime_physics_pytest.py](../../python/scripts/run_regime_physics_pytest.py) avec un marqueur unique.
- [x] verifier les sorties pytest pour chaque marqueur.

## 6. Critere de cloture

- [x] considerer la liste comme valide si chaque regime passe et si les lanceurs racine et marqueur restent stables.