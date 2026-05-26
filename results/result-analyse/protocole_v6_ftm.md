# Protocole V6 - Loi derivee Frequence-Torsion-Masse (FTM)

## But

V6 ne cherche pas a valider la FTM comme loi fondamentale.
V6 cherche a determiner le statut physique reel que la FTM peut raisonnablement avoir:

- invariant structurel,
- loi effective conditionnelle,
- ou parametrage heuristique non robuste.

Aucune promotion automatique vers une loi physique fondamentale.

## Lois et hypotheses autorisees

Les definitions ci-dessous sont figees et ne doivent pas etre modifiees:

- Loi du tube: omega_tube(m) = K * sqrt(m)
- Loi multi-phase maximale: N_phases,max = 1 + n_torsions
- Loi derivee FTM:

  N_phases,eff(m, omega) = [1 + n_torsions * F(omega / Omega_torsion)] * G(omega_tube(m) / Omega_torsion)

- F(x) = x^2 / (1 + x^2)
- G(y) = y / (1 + y)

Aucun autre terme n est autorise.

## Hypotheses V6-H

- H6-1: la dependance en masse proposee par G(y) a une signification physique robuste, non purement ordinale.
- H6-2: le facteur de torsion F(omega / Omega) decrit une activation reelle, pas un simple seuil arbitraire.
- H6-3: la combinaison F x G introduit une structure predictive stable, pas seulement une hierarchie qualitative.
- H6-4: la loi FTM n est pas equivalente a une reecriture triviale de V2 (portance conductrice).

## Serie de tests V6

### TEST V6-1 - Test d equivalence structurelle

Question:

La loi FTM apporte-t-elle une structure nouvelle par rapport a l espace invariant V3 ?

Test:

- Calculer N_phases,eff pour Cu, Al, Fe et Ag.
- Comparer l ordre FTM (via N_phases,eff) et l ordre V3 sur l axe V2 (sigma / sigma_Cu).

Critere de rejet:

- si FTM est equivalente a une projection monotone de V2, la loi est redondante et donc non physique.

Critere de soutien:

- si FTM introduit une separation differente ou enrichie, la loi reste potentiellement informative.

### TEST V6-2 - Robustesse par leave-one-material-out

Question:

La dependance en masse est-elle stable, ou seulement ajustee a un petit ensemble ?

Test:

- retirer un materiau;
- recalculer les classements FTM;
- verifier la coherence des positions relatives.

Critere:

- soutien si l ordre et les ecarts relatifs restent stables;
- rejet si la permutation devient instable.

### TEST V6-3 - Nature du facteur de torsion

Question:

Le facteur F(omega / Omega) decrit-il un changement de regime reel ?

Tests:

- analyser les transitions bf_proxy -> hf_classic -> hf_advanced_proxy;
- comparer les activations prevues par F a celles deja observees dans V1.

Critere:

- soutien si F est correle a l activation geometrique HF (V1);
- rejet si F introduit une dynamique etrangere.

### TEST V6-4 - Limite haute regime sature

Question:

La limite omega >> Omega_torsion est-elle physiquement coherente ?

Tests:

- comparer N_phases,eff quand omega tend vers l infini;
- verifier si cette saturation respecte les ecarts V3;
- verifier qu elle ne cree pas de plateau universel artificiel.

Critere:

- soutien si la saturation reste differenciee par materiau;
- rejet si un plateau commun non observe apparait.

### TEST V6-5 - Test falsifiant dur

Question:

Peut-on expliquer toutes les separations FTM sans invoquer la torsion ?

Test:

- fixer n_torsions = 0;
- reduire N_phases,eff a G(y);
- comparer avec V3.

Verdict:

- soutien si la torsion change reellement la structure;
- rejet si la torsion n est qu un artifice narratif.

## Sorties attendues

Le protocole doit produire un rapport qui tranche sans ambiguite:

- ce que FTM apporte reellement;
- ce qu elle n apporte pas;
- son statut epistemique correct parmi loi effective conditionnelle, outil descriptif heuristique, ou formalisme non robuste.

## Regle de cloture

Quelle que soit l issue de V6:

- echec de FTM ne signifie pas echec de tube;
- echec de FTM ne signifie pas remise en cause de V3 a V5;
- FTM reste une branche exploratoire independante.

## Lecture strategique

Apres V3 a V5, attaquer FTM est pertinent, mais seulement sous cette forme exploratoire.
V6 doit suffire pour decider si la loi derivee merite d aller plus loin.