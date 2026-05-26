# Protocole V2 - Validation numerique

## But
Valider les etages H1 a H4 sur les jeux HF reels normalises.

## Verdict
- Verdict global: partiel
- Statut des donnees: ready
- Jeux utilises: CU, AL, AG, FE

## Etages
- H1: supported - Local model only
  - A single amplitude term does not transfer cleanly across Cu, Al, Ag, and Fe.
- H2: contradicted - Global alpha' correction
  - The alpha' correction does not improve transfer enough.
- H3: contradicted - Quadratic beta' term
  - The quadratic term is not justified by the held-out error.
- H4: contradicted - Mass-weighted FTM comparison
  - The mass-weighted transform increases the spread across materials.

## Materiaux
- CU: rho=1.724e-08 mu_r=1.0 amplitude=0.066100
- AL: rho=2.820e-08 mu_r=1.0 amplitude=0.084456
- AG: rho=1.590e-08 mu_r=1.0 amplitude=0.063404
- FE: rho=9.710e-08 mu_r=1000.0 amplitude=0.004960

## Metriques
- H1 RMSE: 0.004025
- H1 erreur relative moyenne: 3.563785
- H2 RMSE: 0.006726
- H2 erreur relative moyenne: 6.547333
- H3 RMSE: 0.007132
- H3 erreur relative moyenne: 7.135963
- H4 CV brut: 0.629879
- H4 CV pondere: 0.813523

## Lecture courte
Le validateur teste un modele d'amplitude commune A = delta * sqrt(f), puis des corrections globales sur le proxy de conductivite et une ponderation masse sigma * sqrt(m).

Les fichiers sources utilises sont les jeux HF normalises du manifeste de travail.
