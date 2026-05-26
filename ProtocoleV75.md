# V75 — DÉMONSTRATION CALCULÉE DU CADRE BBN / LITHIUM
# Version : 1.0 — Preuve-cadre par pipeline numérique
# Auteur : Jean-Philippe
# Objet : Relecture quantitative du troisième cas pilote à partir de V70

Protocole précédent : ProtocoleV74.md
Protocole suivant : V76 (extension sur d'autres anomalies)

Wrapper global suggéré :
- python/scripts/runv75_resolution_suite.py

CONTENU :
- 0. Objectif
- 1. Cas pilote choisi : BBN / lithium
- 2. Observables
- 3. Système et hypothèses
- 4. Pipeline de calcul
- 5. Critères de cohérence
- 6. Comparatif observation / calcul
- 7. Extension à d’autres anomalies
- 8. Résultats attendus
- 9. Format de sortie pour le testeur

0. OBJECTIF
-----------
Passer du statut “cadre qualitatif” au statut “cadre calculé” pour COSMO-03.

Le point de départ est simple : le modèle K/T/Y + D1/D2 + V_ent ne modifie pas la physique nucléaire elle-même, mais peut reparamétrer les conditions initiales géométriques au régime BBN.

L’objectif est donc double :
- préserver la cohérence de D/H et He/H,
- relire la tension du lithium comme une branche géométrique potentiellement différente.


1. CAS PILOTE CHOISI : BBN / LITHIUM
-------------------------------------
Cas retenu :
- abondances primordiales D/H, He/H, Li/H
- tension principale : lithium-7
- cadre de validation : COSMO-03 dans V70

Position du modèle :
- D et He restent cohérents avec ΛCDM + BBN standard,
- Li peut être relu comme un effet de branche / condition initiale,
- aucune nouvelle particule n’est introduite dans ce cadre.


2. OBSERVABLES
--------------
On considère :
- (D/H)_obs
- (He/H)_obs
- (Li/H)_obs

Le test n’est pas une BBN complète refaite de zéro ; il s’agit d’un test de cohérence du cadre géométrique sur le régime BBN.


3. SYSTÈME ET HYPOTHÈSES
------------------------
Le système effectif de V70 est utilisé en régime BBN :

    A_Y Y'' + γ* (Y - Y∞) + χ₂ T' = 0
    A_T T'' + 2α_T T + α_KT K - χ₂ Y' = 0
    A_K K'' + 2α_K K + α_KT T = 0

Hypothèses de travail :
- régime z_BBN >> 1
- régime quasi-stationnaire ou lent pour K/T/Y
- conditions initiales géométriques légèrement différentes possibles
- pas de modification directe des réactions nucléaires

Le couplage d’interaction est :

    L_ent = χ₂ T (dY/dλ)

Le potentiel conservatif associé reste :

    V_total^(eff) = V_KT + V_Y + V_D

avec :

    V_KT = α_K K² + α_T T² + α_KT K T
    V_Y = (γ*/2)(Y - Y∞)²
    V_D = β₁ Y_D1² + β₂ Y_D2² + β₁₂ Y_D1 Y_D2


4. PIPELINE DE CALCUL
---------------------
Étape 1 — Fixer le régime BBN :
- z_BBN très élevé
- dynamique lente ou quasi-stationnaire

Étape 2 — Résoudre le système K/T/Y :
- imposer des conditions initiales adaptées au régime BBN
- explorer plusieurs branches (K₀, T₀, Y₀, Y∞)

Étape 3 — En déduire les paramètres effectifs BBN :
- H_BBN
- densités effectives pertinentes

Étape 4 — Vérifier la cohérence :
- D/H compatible
- He/H compatible
- Li/H peut varier selon la branche géométrique


5. CRITÈRES DE COHÉRENCE
------------------------
Le cadre est jugé cohérent si :
- D/H reste dans la bande observée,
- $Y_p$ (He-4) reste dans la bande observée,
- H_BBN reste compatible avec le régime standard,
- le lithium peut être déplacé par branche sans casser D/He,
- les autres secteurs physiques restent intacts.


6. COMPARATIF OBSERVATION / CALCUL
----------------------------------
Comparatif de principe :

| Observable | Observation | Calcul avec cadre V70 | Lecture sans cadre géométrique | Écart principal |
|---|---:|---:|---:|---:|
| D/H | cohérent | cohérent | cohérent | pas de dégradation |
| $Y_p$ (He-4) | cohérent | cohérent | cohérent | pas de dégradation |
| Li/H | tension persistante | branche géométrique possible | tension persistante | relecture du lithium |

Lecture :
- le cadre géométrique ne casse pas D/H et $Y_p$,
- le lithium peut être relu comme un effet de branche géométrique,
- l’absence de nouvelle particule est conservée.

## Résultat V75
Le cadre est cohérent sur le couple BBN de base :
- D/H : compatible observationnellement,
- $Y_p$ : compatible à l'échelle des incertitudes,
- Li/H : tension dans le benchmark standard, mais corrigée numériquement au fixed-point V80B.

Verdict de travail :
- `cadre_BBN_coherent_sur_DH_et_Yp`
- `Li/H` est traité séparément par V80B.


7. EXTENSION À D’AUTRES ANOMALIES
----------------------------------
Même logique pour :
- COSMO-01 : H₀ / H(z)
- COSMO-02 : S₈ / fσ₈
- JWST-01 : Little Red Dots
- UHECR-01 : anisotropie dipolaire

Pour chaque cas :
- définir l’observable,
- écrire la prédiction du modèle,
- comparer le comportement avec et sans branche géométrique,
- vérifier la cohérence multi-secteur.


8. RÉSULTATS ATTENDUS
---------------------
Le testeur doit produire :
- un résumé du régime BBN
- les valeurs K, T, Y au voisinage de z_BBN
- H_BBN
- un verdict de cohérence pour D/H et He/H
- une relecture du lithium par branche


9. FORMAT DE SORTIE POUR LE TESTEUR
------------------------------------
- JSON : résultats de cohérence
- TXT : résumé lisible
- Tableau : D/H, He/H, Li/H
- Verdict : cadre_BBN_coherent
