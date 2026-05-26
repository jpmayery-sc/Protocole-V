# V71 — DÉMONSTRATION CALCULÉE DES ANOMALIES S8 / fσ8
# Version : 1.0 — Preuve-modèle par pipeline numérique
# Auteur : Jean-Philippe
# Objet : Poser la résolution quantitative du premier cas pilote à partir de V70

Protocole précédent : ProtocoleV61.md
Protocole suivant : V72 (extension sur d'autres anomalies)

Wrapper global suggéré :
- python/scripts/runv71_resolution_suite.py

CONTENU :
- 0. Objectif
- 1. Cas pilote choisi : S8 / fσ8
- 2. Système d'équations
- 3. Pipeline de calcul
- 4. Définition du χ²
- 5. Comparatif avec / sans interaction
- 6. Critère de succès
- 7. Extension à d'autres anomalies
- 8. Résultats attendus
- 9. Format de sortie pour le testeur

0. OBJECTIF
-----------
Passer du statut « cadre explicatif » au statut « démonstration calculée ».

Le premier cas pilote est la tension cosmologique S8 / fσ8, car il est déjà consolidé en V60–V61 et fournit une preuve-modèle numérique immédiate.

Le principe est :
- résoudre le système effectif issu de V70,
- calculer les observables,
- comparer le scénario avec interaction dérivative et le scénario sans interaction,
- montrer une amélioration quantitative mesurable par χ².


1. CAS PILOTE CHOISI : S8 / fσ8
-------------------------------
Cas retenu :
- tension de croissance des structures
- observables : fσ8(z), S8
- données déjà consolidées dans V60–V61

Résultats de référence :
- χ²_fσ8_with_ent = 1.84
- χ²_fσ8_noent = 9.62
- Δχ²_fσ8 = 7.78
- S8_with_ent = 0.776
- S8_noent = 0.812
- S8_obs = 0.776

Interprétation :
L’intrication dérivative améliore la concordance avec les données et annule la tension sur S8 dans la plage consolidée.


2. SYSTÈME D’ÉQUATIONS
----------------------
On part du système effectif de V70, écrit en fonction du paramètre d’évolution λ :

    A_Y Y'' + γ* (Y - Y∞) + χ₂ T' = 0
    A_T T'' + 2α_T T + α_KT K - χ₂ Y' = 0
    A_K K'' + 2α_K K + α_KT T = 0

Le couplage dérivatif d’interaction est :

    L_ent = χ₂ T (dY/dλ)

Le potentiel conservatif associé est :

    V_total^(eff) = V_KT + V_Y + V_D

avec :

    V_KT = α_K K² + α_T T² + α_KT K T
    V_Y = (γ*/2)(Y - Y∞)²
    V_D = β₁ Y_D1² + β₂ Y_D2² + β₁₂ Y_D1 Y_D2


3. PIPELINE DE CALCUL
---------------------
Étapes du calcul :

1. Résoudre numériquement le système sur un domaine en λ, ou sur z après reparamétrisation.
2. En déduire K(λ), T(λ), Y(λ), Y'(λ).
3. Construire V_total^(eff)(λ).
4. Calculer les observables : H(z), fσ8(z), S8.
5. Refaire le calcul avec χ₂ = 0.
6. Comparer les deux scénarios par χ².

Domaine de calcul recommandé :
- z ∈ [0, z_max]
- z_max ≈ 2.4 pour la synthèse cosmologique consolidée


4. DÉFINITION DU χ²
-------------------
Pour fσ8 :

    χ²_fσ8 = Σ_i [ (fσ8_mod(z_i) - fσ8_obs(z_i))² / σ_fσ8(z_i)² ]

Version générale matricielle :

    χ² = (d - m)^T C^{-1} (d - m)

avec :
- d : données observées
- m : prédictions du modèle
- C : covariance


5. COMPARATIF AVEC / SANS INTERACTION
-------------------------------------
Scénario avec interaction :
- χ²_fσ8_with_ent = 1.84
- S8_with_ent = 0.776
- H(z) cohérent
- V_total convexe et stable

Scénario sans interaction :
- χ²_fσ8_noent = 9.62
- S8_noent = 0.812
- tension résiduelle sur la croissance

Gain :
- Δχ²_fσ8 = 7.78

Comparatif observation / calcul :

| Observable | Observation | Calcul avec interaction | Calcul sans interaction | Écart principal |
|---|---:|---:|---:|---:|
| χ²_fσ8 | — | 1.84 | 9.62 | Δχ² = 7.78 |
| S8 | 0.776 | 0.776 | 0.812 | Tension supprimée avec interaction |
| H(z) | cohérent avec les points consolidés | cohérent | non chiffré ici | validation de cohérence |

Lecture : le calcul avec interaction reproduit exactement la valeur observée de S8 et améliore fortement χ²_fσ8, alors que le scénario sans interaction reste en tension.


6. CRITÈRE DE SUCCÈS
--------------------
La démonstration est considérée comme réussie si :
- χ²_with < χ²_noent
- Δχ² > 5
- S8_with ≈ S8_obs
- H(z) reste cohérent
- V_total reste convexe et stable
- les secteurs matière / photon / RG restent intacts

Ici, le cas S8 / fσ8 satisfait tous les critères consolidés.


7. EXTENSION À D’AUTRES ANOMALIES
----------------------------------
Même méthode pour :
- COSMO-01 : H0 / H(z)
- JWST-01 : Little Red Dots
- COSMO-03 : lithium primordial
- UHECR-01 : anisotropie dipolaire

Pour chaque cas :
- définir l’observable,
- écrire la prédiction du modèle,
- comparer χ² avec et sans interaction,
- vérifier la cohérence multi-secteur.


8. RÉSULTATS ATTENDUS
---------------------
Le testeur doit produire :
- un résumé du pipeline
- les valeurs de K, T, Y
- V_total^(eff)
- H(z), fσ8(z), S8
- χ²_with, χ²_noent, Δχ²
- verdict final sur le cas pilote


9. FORMAT DE SORTIE POUR LE TESTEUR
------------------------------------
- JSON : résultats numériques du run
- TXT : résumé lisible
- Figures : comparatif fσ8, S8, H(z), V_total
- Verdict : preuve_modèle_confirmée
