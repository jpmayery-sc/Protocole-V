# Dossier Validation Transport

## Objectif

Suivre la validation numerique du protocole de transport V2 de facon claire, tracee et falsifiable.

Ce document regroupe le protocole, les tests a realiser, l etat des donnees et les resultats disponibles avant toute generalisation.

## Tableau de synthese

| Colonne | Etage / test | Verdict | Script principal |
| --- | --- | --- | --- |
| 1 | H1 - modele local seul | supported | [python/scripts/run_protocol_v2_validation.py](../../python/scripts/run_protocol_v2_validation.py) |
| 2 | H2 - correction globale alpha prime | contradicted | [python/scripts/run_protocol_v2_validation.py](../../python/scripts/run_protocol_v2_validation.py) |
| 3 | H3 - terme quadratique beta prime | contradicted | [python/scripts/run_protocol_v2_validation.py](../../python/scripts/run_protocol_v2_validation.py) |
| 4 | H4 - comparaison FTM ponderee masse | contradicted | [python/scripts/run_protocol_v2_validation.py](../../python/scripts/run_protocol_v2_validation.py) |

## Protocole de travail

- Un seul modele local de depart Kloc(omega).
- Un seul ajustement global de alpha prime, puis alpha prime fige.
- Un terme beta prime active seulement pour les materiaux non lineaires.
- Une comparaison inter-materiaux via FTM(omega) ponderee par sigma racine(m).
- Juger avec RMSE, erreur relative moyenne, chi2 reduit, AIC et BIC.
- Invalider toute generalisation si le gain reste local ou disparaît hors du jeu d ajustement.

## Hypotheses du protocole

- H1: la partie locale seule ne suffit pas a expliquer les donnees HF reelles.
- H2: une correction globale unique doit reduire l erreur hors echantillon si un proxy de conductivite capture vraiment la variance inter-materiaux.
- H3: un terme quadratique ne doit etre retenu que s il ameliore de facon robuste la prediction hors echantillon au-dela du terme lineaire.
- H4: un repondage masse n est justifie que s il rend la statistique inter-materiaux plus stable apres normalisation physique, pas seulement plus petite sur ce jeu.

## Pourquoi H2, H3 et H4 echouent

- H2 echoue parce qu un seul proxy de conductivite n explique pas toute la dispersion entre Cu, Al, Ag et Fe: les ecarts restants sont encore domines par les differences de regime et de transport effectif, pas par une correction globale unique.
- H3 echoue parce que le terme quadratique apporte surtout de la flexibilite d ajustement sur un echantillon minuscule; en validation croisee, cette flexibilite ne se transforme pas en gain hors echantillon.
- H4 echoue parce que la ponderation par racine(m) est heuristique et non derivee de l observable mesure; elle amplifie la separation entre materiaux au lieu de la compresser sur ce jeu normalise.
- En bref, les trois echecs pointent vers le meme probleme: les corrections ajoutees sont plus proches d un parametrage phenomenologique que d une invariance physique verifiee.

## Formulation plus robuste

- H2 robuste: une correction globale fondee sur un invariant physique doit reduire l erreur hors echantillon sur chaque materiau laisse de cote, avec un seuil de gain defini a l avance.
- H3 robuste: un terme non lineaire ne doit etre accepte que s il ameliore la prediction leave-one-material-out sur tous les materiaux, et pas seulement sur le materiau non lineaire suppose.
- H4 robuste: toute ponderation supplementaire doit etre justifiee par une diminution du coefficient de variation apres re-normalisation dimensionnelle, et rester stable lorsque l on retire un materiau a la fois.
- Si l objectif est une loi physique, la bonne question n est pas "est-ce que le score baisse" mais "quelle structure reste invariante quand on change de materiau, de regime et de source publiee".

## Jeux de donnees a suivre

- Cuivre: [python/data/hf_transport/cu.json](../../python/data/hf_transport/cu.json)
- Aluminium: [python/data/hf_transport/al.json](../../python/data/hf_transport/al.json)
- Argent: [python/data/hf_transport/ag.json](../../python/data/hf_transport/ag.json)
- Fer: [python/data/hf_transport/fe.json](../../python/data/hf_transport/fe.json)

## Etat des donnees

- Le manifeste de travail est present: [python/data/hf_transport_manifest.json](../../python/data/hf_transport_manifest.json).
- Le manifeste est maintenant au statut ready.
- Les fichiers HF ont ete normalises en JSON reels avec provenance explicite.
- Le dossier de schema explique la forme attendue: [python/data/hf_transport/README.md](../../python/data/hf_transport/README.md).

## Sources publiees identifiees

- Cuivre et aluminium: article Springer sur la mesure de la dependance en frequence de la resistance active de conducteurs circulaires en cuivre et aluminium, plage 20 Hz a 2 MHz.
- Argent: article ResearchGate / Materials Today Proceedings sur la profondeur de peau de l argent, du cuivre et de l or, avec equation explicite et figures.
- Fer: article sur le skin effect ferromagnetique et comparaison des effets de peau dans des materiaux ferromagnetiques et non ferromagnetiques.
- Point commun: ces sources sont reelles et publiees, et elles ont maintenant ete converties en jeux HF normalises pour le protocole V2.

## Ordre d execution

1. Verifier la presence et la lisibilite du manifeste.
2. Verifier la presence des quatre jeux HF.
3. Marquer le manifeste comme ready seulement quand les jeux sont reels.
4. Executer la suite V2.
5. Relever le verdict H1 a H4.
6. Comparer les scores avant / apres.
7. Rejeter toute conclusion si le gain reste non robuste.

## Scripts de validation

- [python/scripts/run_protocol_v2_suite.py](../../python/scripts/run_protocol_v2_suite.py): suite de readiness et rapport global.
- [results/result-analyse/protocole_v2.md](protocole_v2.md): rapport lisible de la suite V2.

## Etat actuel apres reprise

- Le runner V2 de readiness existe toujours et distingue maintenant un manifeste ready d une source exploitable.
- Le manifeste HF transport est passe au statut ready.
- Les quatre fichiers HF sont des jeux normalises et non plus des gabarits.
- Les sources publiees candidates ont ete transformees en datasets JSON reels et harmonises.
- Une validation numerique dediee a ete ajoutee dans [python/scripts/run_protocol_v2_validation.py](../../python/scripts/run_protocol_v2_validation.py).
- H1 est maintenant supporte, tandis que H2, H3 et H4 sont contradits par les donnees HF normalisees.
- Etape 3 valide: le manifeste n est marque ready que parce que les quatre jeux HF Cu, Al, Ag et Fe sont bien presentes sous forme de jeux reels normalises.

## Resultats de validation

### Suite V2

- Verdict global: partiel.
- Statut des donnees: ready.
- Jeux attendus: Cu, Al, Ag, Fe.
- Manifeste detecte: [python/data/hf_transport_manifest.json](../../python/data/hf_transport_manifest.json).
- Jeux detectes: [python/data/hf_transport/cu.json](../../python/data/hf_transport/cu.json), [python/data/hf_transport/al.json](../../python/data/hf_transport/al.json), [python/data/hf_transport/ag.json](../../python/data/hf_transport/ag.json), [python/data/hf_transport/fe.json](../../python/data/hf_transport/fe.json).
- Rapport exact: [results/result-analyse/protocol_v2_validation_summary_20260512-121626Z.json](protocol_v2_validation_summary_20260512-121626Z.json) et [results/result-analyse/protocole_v2_validation.md](protocole_v2_validation.md).
- Etages H1 a H4: H1 supported, H2 contradicted, H3 contradicted, H4 contradicted.

### Lecture courte

- Les suites adjacentes restent valides et servent de support de contexte.
- Le protocole transport est maintenant trace dans un dossier unique.
- La validation numerique H1-H4 est desormais calculee explicitement par un script dedie; le resultat est partiel, avec un seul etage supporte.

## Suites adjacentes deja valides

- Conductivite des materiaux: supported.
- Regime courant: supported.
- Induction: supported.
- Effet peau: conforme strict.
- Saturation magnetique: conforme strict.
