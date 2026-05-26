# V73 — DÉMONSTRATION CALCULÉE DE L’ANOMALIE H₀ / H(z)
# Version : 1.0 — Preuve-modèle par pipeline numérique
# Auteur : Jean-Philippe
# Objet : Résolution quantitative du second cas pilote à partir de V70

Protocole précédent : ProtocoleV71.md
Protocole suivant : V74 (extension sur d'autres anomalies)

Wrapper global suggéré :
- python/scripts/runv73_resolution_suite.py

CONTENU :
- 0. Objectif
- 1. Cas pilote choisi : H₀ / H(z)
- 2. Système d’équations
- 3. Pipeline de calcul
- 4. Définition du χ²_H
- 5. Comparatif avec / sans interaction
- 6. Critère de succès
- 7. Extension à d’autres anomalies
- 8. Résultats attendus
- 9. Format de sortie pour le testeur

0. OBJECTIF
-----------
Passer de la démonstration pilote S8 / fσ8 à la démonstration pilote H₀ / H(z), en gardant exactement la même logique calculée.

Le cas COSMO-01 est retenu parce qu’il est déjà consolidé dans V70 et parce qu’il valide directement le fond d’expansion.

Le principe est :
- résoudre le système effectif issu de V70,
- calculer H(z),
- comparer le scénario avec interaction dérivative et le scénario sans interaction,
- montrer que la courbe d’expansion reste cohérente avec les six points consolidés.


1. CAS PILOTE CHOISI : H₀ / H(z)
---------------------------------
Cas retenu :
- tension de Hubble locale / CMB
- observables : H(z), H₀
- données consolidées dans V70 (Table 1)

Résultats de référence :
- χ²_H = 2.11
- 6 points sur z ∈ [0.1, 2.0]
- covariance diagonale dans la synthèse

Interprétation :
Le couplage dérivatif d’interaction corrige doucement Y(z), ce qui ajuste la pente de H(z) sans casser les autres secteurs.


2. SYSTÈME D’ÉQUATIONS
----------------------
On part du système effectif de V70, écrit en fonction du paramètre d’évolution λ :

    A_Y Y'' + γ* (Y - Y∞) + χ₂ T' = 0
    A_T T'' + 2α_T T + α_KT K - χ₂ Y' = 0
    A_K K'' + 2α_K K + α_KT T = 0

Le couplage d’interaction est :

    L_ent = χ₂ T (dY/dλ)

Le potentiel conservatif associé est :

    V_total^(eff) = V_KT + V_Y + V_D

avec :

    V_KT = α_K K² + α_T T² + α_KT K T
    V_Y = (γ*/2)(Y - Y∞)²
    V_D = β₁ Y_D1² + β₂ Y_D2² + β₁₂ Y_D1 Y_D2


3. PIPELINE DE CALCUL (V60–V61)
-------------------------------
Étape 1 — Résoudre le système complet sur z ∈ [0, 2.4].

Étape 2 — Construire H(z) à partir de K(z), T(z), Y(z).

Étape 3 — Calculer le χ² :

    χ²_H = Σ_i (H_mod(z_i) − H_obs(z_i))² / σ_H(z_i)²

Étape 4 — Comparer deux runs :
- avec intrication (χ₂ ≠ 0)
- sans intrication (χ₂ = 0)


4. DÉFINITION DU χ²_H
---------------------
Pour H(z) :

    χ²_H = Σ_i [ (H_mod(z_i) - H_obs(z_i))² / σ_H(z_i)² ]

Version générale matricielle :

    χ² = (d - m)^T C^{-1} (d - m)

avec :
- d : données observées
- m : prédictions du modèle
- C : covariance


5. COMPARATIF AVEC / SANS INTERACTION
-------------------------------------
Scénario avec interaction :
- χ²_H = 2.11
- H(z) cohérent avec les 6 points consolidés
- H₀ émerge naturellement de la dynamique Y(z)
- V_total convexe et stable

Scénario sans interaction :
- non cohérent dans la synthèse consolidée
- tension résiduelle sur la pente de H(z)


6. CRITÈRE DE SUCCÈS
--------------------
La démonstration est considérée comme réussie si :
- χ²_H est raisonnable
- H(z) suit les données consolidées
- le scénario sans interaction reste moins cohérent
- les secteurs matière / photon / RG restent intacts

Ici, le cas H₀ / H(z) satisfait les critères consolidés.


7. EXTENSION À D’AUTRES ANOMALIES
----------------------------------
Même méthode pour :
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
- H(z)
- χ²_H
- verdict final sur le cas pilote


9. FORMAT DE SORTIE POUR LE TESTEUR
------------------------------------
- JSON : résultats numériques du run
- TXT : résumé lisible
- Figures : comparatif H(z), V_total
- Verdict : preuve_modèle_confirmée
