# Rapport V5 - Nature du couplage geometrie / portance

## Finalite de V5

Identifier si le couplage V1-V2 est:

- purement materiel,
- geometrique,
- ou un effet de changement de regime.

V5 ne cherche aucune nouvelle loi.

## Hypothese V5-H

Le couplage residuel entre V1 et V2 est un effet de saturation geometrique contrainte par la conductivite, et non une dependance directe.

## Definition inchangee depuis V3

On repart exactement de l espace V3:

- V1 = log10(A / A_ref)
- V2 = sigma / sigma_Cu
- A = delta * sqrt(f)

Aucune nouvelle transformation n est autorisee.

## Donnees de depart

Le calcul est effectue sur les quatre materiaux V3:

- Cu
- Al
- Ag
- Fe

Les bandes disponibles restent bf_proxy, hf_classic et hf_advanced_proxy.

## Grille de lecture V5

Les tests ci-dessous reprennent la lecture demandee:

- V5-1: plafond materiel;
- V5-2: analyse locale de pente;
- V5-3: saturation en HF avancee;
- V5-4: test falsifiant dur.

## TEST V5-1 - Lecture plafond materiel

Hypothese:

Le couplage vient du fait que V1 ne peut pas croitre librement quand V2 est faible.

Test:

Normaliser V1 par materiau, puis comparer les trajectoires reduites.

Resultat numerique:

- Cu: max(V1) = 0.0, normalisation degenerée, trajectoire reduite a [0, 0, 0, 0, 0]
- Al: max(V1) = 0.00022472195415797715, trajectoire reduite non monotone
- Ag: max(V1) = 0.0007598797885931705, trajectoire reduite non monotone
- Fe: max(V1) = 0.00045310842808314253, trajectoire reduite non monotone

Comparaison des trajectoires normalisees:

- Cu~Ag: rmse = 0.5650151472376929
- Cu~Fe: rmse = 0.6343538230052922
- Al~Ag: rmse = 1.538422730317096
- Al~Fe: rmse = 1.8882901125675686
- Ag~Fe: rmse = 0.7206675173505389

Lecture attendue:

- un rapprochement partiel des trajectoires serait compatible avec un couplage par plafond;
- un recollage fort et uniforme serait attendu si le plafond materiel dominait completement.

Lecture observee:

- les trajectoires ne se recollent que partiellement;
- la normalisation conditionnelle ne produit pas une fusion nette des profils;
- le cas Cu est degeneré car son maximum de V1 est nul, ce qui rend ce test intrinsèquement fragile pour lui.

Verdict TEST V5-1: partiellement soutenu, mais non concluant comme preuve d un simple effet de plafond.

## TEST V5-2 - Analyse locale de pente

Hypothese:

La portance modifie la vitesse d activation de la geometrie.

Test:

Calculer dV1/df pour chaque materiau et corréler la pente a V2.

Resultat numerique:

- Cu: mean_slope = -8.683992987059573e-08, abs_mean_slope = 1.0148277648601254e-07
- Al: mean_slope = -1.330552957288026e-07, abs_mean_slope = 1.7956350326588354e-07
- Ag: mean_slope = -8.002276232746094e-08, abs_mean_slope = 8.61716486538847e-08
- Fe: mean_slope = 1.050233823172029e-07, abs_mean_slope = 1.284764755520134e-07

Dependance sur V2:

- correlation(mean_slope, V2) = -0.7352210194966962
- correlation(abs_mean_slope, V2) = -0.5589414923801089

Lecture attendue:

- une pente plus faible pour V2 faible serait compatible avec une portance limitante;
- une pente independante de V2 indiquerait des mecanismes réellement separés.

Lecture observee:

- il existe bien une dependance residuelle entre pente locale et portance;
- cette dependance n est pas monotone proprement dite sur les quatre materiaux;
- le signe des pentes varie selon le materiau, donc on n observe pas un mecanisme separable parfaitement propre.

Verdict TEST V5-2: soutient l idee d une contrainte de portance sur l activation, mais pas une separation nette et stable.

## TEST V5-3 - Recherche de saturation en HF avancee

Hypothese:

Le couplage correspond a une saturation geometrique contrainte.

Test:

Vérifier si V1 atteint un plateau, puis comparer la valeur du plateau selon V2.

Resultat numerique:

- Cu: plateau_like = true, relative_gap = 0.14971945378351093
- Al: plateau_like = false, relative_gap = 0.4143581359806043
- Ag: plateau_like = false, relative_gap = 1.0
- Fe: plateau_like = false, relative_gap = 0.9224633512215888

Lecture attendue:

- un plateau commun serait compatible avec une geometrie dominante;
- un plateau decale par materiau indiquerait une limite de portance sur la geometrie.

Lecture observee:

- il n y a pas de plateau commun clairement partage;
- le dernier point HF avancee ne se stabilise pas au meme niveau entre materiaux;
- la saturation geometrique est donc deplacee par le materiau, ce qui est compatible avec une contrainte conductive mais pas avec un plafond universel unique.

Verdict TEST V5-3: soutient un plateau decale par materiau, pas un plateau commun.

## TEST V5-4 - Test falsifiant dur

Question:

Peut-on expliquer la geometrie V3 sans V2 ?

Test:

Projetion en 1D sur V1 et observation de la perte de structure inter-materiaux.

Resultat numerique:

- centroids V1 only:
  - Cu: -0.00014803235388901665
  - Al: -5.6050605660328056e-05
  - Ag: -5.115207748554385e-05
  - Fe: 0.000195296374851966
- spread des centroides V1 only = 0.00034332872874098266
- ordre V1 only: cu -> al -> ag -> fe

Lecture attendue:

- si la structure casse, V2 est fondamental, pas decoratif.

Lecture observee:

- V1 seul conserve un ordre grossier, mais la separation inter-materiaux devient tres faible;
- la structure forte de V3, en particulier la separation entre materiaux, depend encore de V2;
- V2 n est donc pas accessoire si l on veut conserver la structure geometrique lisible.

Verdict TEST V5-4: non, V1 seul ne suffit pas pour expliquer la geometrie V3.

## Synthese physique

Le couplage V1-V2 n apparait ni purement materiel ni purement geometrique.

Ce que montrent les tests:

- V1 porte bien une saturation geometrique HF;
- V2 fixe le niveau de portance conductrice;
- la deformation residuelle de V1 depend de V2, mais de maniere deplacee et regime-dependante;
- V1 seul perd trop de structure pour etre fondamental a lui seul.

## Verdict global

V5 est partiellement soutenu.

Interpretation la plus robuste:

- le couplage est un effet de changement de regime avec saturation geometrique contrainte par la conductivite;
- il ne ressemble pas a une dependance directe simple;
- il n est pas non plus purement materiel, car V1 conserve une dynamique propre.

## Conclusion finale

La bonne lecture de V5 est:

- geometrie et portance sont distinctes;
- leur couplage residuel vient surtout de la saturation geometrique sous contrainte conductive;
- V2 reste fondamental pour garder la structure V3 lisible.
