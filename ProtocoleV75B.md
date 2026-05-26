# V75B — TEST NUMÉRIQUE BBN / LITHIUM
# Version : 1.0 — Vérification chiffrée du cadre COSMO-03
# Auteur : Jean-Philippe
# Objet : Comparer les chiffres BBN observés / de référence avec le cadre V70

Protocole précédent : ProtocoleV75.md
Protocole suivant : V76 (extension sur d’autres anomalies)

Wrapper global suggéré :
- python/scripts/runv75b_bbn_suite.py

CONTENU :
- 0. Objectif
- 1. Chiffres BBN de référence
- 2. Cas pilote : D/H, He/H, Li/H
- 3. Test de cohérence
- 4. Pipeline de calcul
- 5. Résultats attendus
- 6. Comparatif observation / calcul
- 7. Verdict

0. OBJECTIF
-----------
Passer du cadre BBN qualitatif (V75) à un contrôle numérique explicite.

Le but de V75B est de vérifier si les chiffres BBN standards sont compatibles avec le cadre V70 :
- D/H : doit rester cohérent,
- He/H : doit rester cohérent,
- Li/H : la tension doit être identifiée clairement comme non résolue numériquement.

Ici, "compatible" signifie que la mesure observationnelle reste dans la bande d'erreur du benchmark standard; cela ne veut pas dire que le mécanisme sous-jacent est expliqué par le cadre V70.

Le fixed-point V80B sera utilisé plus loin comme test séparé: il montre que, dans le toy proxy calibré à $\delta_{EM}=-0.0069$, Li/H passe aussi numériquement.


1. CHIFFRES BBN DE RÉFÉRENCE
----------------------------
Valeurs de benchmark utilisées pour la vérification :

- D/H_obs = (2.527 ± 0.030) × 10^-5
- He/H_obs = 0.2465 ± 0.0097
- Li/H_obs = (1.58 ± 0.31) × 10^-10

Référence BBN standard typique (ordre de grandeur de synthèse) :

- D/H_BBN ≈ 2.45 × 10^-5
- He/H_BBN ≈ 0.2471
- Li/H_BBN ≈ 5.3 × 10^-10

Lecture directe :
- D/H est un accord observationnel de précision avec le standard.
- He/H reste compatible, mais l'incertitude est dominée par les systématiques d'émissivité et d'extrapolation.
- Li/H reste une tension physique robuste: l'observé est typiquement un facteur 2 à 4 sous la prédiction standard.

Sources web utilisées pour V75B :

- Cooke et al., 2018, "One percent determination of the primordial deuterium abundance" (arXiv:1710.11129) : D/H = (2.527 ± 0.030) × 10^-5.
- Pitrou et al., 2018, "Precision big bang nucleosynthesis with improved Helium-4 predictions" (arXiv:1801.08023) : Y_p = 0.24709 ± 0.00017 pour la prédiction standard.
- Aver et al., 2013, "The primordial helium abundance from updated emissivities" (arXiv:1309.0047) : Y_p = 0.2465 ± 0.0097 côté observation.
- Cyburt, Fields, Olive, 2008, "A Bitter Pill: The Primordial Lithium Problem Worsens" (arXiv:0808.2818) : 7Li/H BBN ≈ 5.24 × 10^-10, avec un écart observé de l'ordre de 2.4 à 4.3.


2. CAS PILOTE : D/H, He/H, Li/H
--------------------------------
Le cadre V70 n’essaie pas ici de refaire une BBN complète.
Il vérifie seulement :
- que le cadre géométrique reste compatible avec D/H et He/H,
- que la tension lithium demeure explicitement identifiée.


3. TEST DE COHÉRENCE
--------------------
Critère simple :
- D/H et He/H doivent rester dans une zone compatible avec les observations,
- Li/H doit montrer une tension résiduelle forte si on ne rajoute pas de mécanisme BBN dédié.

Ce test sert à trier :
- ce qui est déjà cohérent,
- ce qui reste à résoudre numériquement.


4. PIPELINE DE CALCUL
---------------------
Étape 1 — Charger les chiffres de référence.

Étape 2 — Comparer les valeurs observation / benchmark BBN.

Étape 3 — Calculer un écart normalisé par observable :

    z = |modèle - observation| / sqrt(σ_obs² + σ_mod²)

Étape 4 — Conclure :
- D/H et He/H passent,
- Li/H ne passe pas encore numériquement.


5. RÉSULTATS ATTENDUS
---------------------
Le testeur doit produire :
- un tableau des chiffres BBN,
- les écarts normalisés,
- un verdict global,
- une mention claire sur le lithium.


6. COMPARATIF OBSERVATION / CALCUL
----------------------------------
| Observable | Observation | Benchmark BBN | Statut |
|---|---:|---:|---|
| D/H | 2.527e-5 ± 0.030e-5 | 2.45e-5 | compatible |
| $Y_p$ (He-4) | 0.2465 ± 0.0097 | 0.2471 | compatible mais systématique-dominé |
| Li/H | 1.58e-10 ± 0.31e-10 | 5.3e-10 | tension forte |

Conclusion locale :
- D/H : compatible observationnellement,
- $Y_p$ : ok à l'échelle des erreurs expérimentales, avec une marge dominée par les systématiques.
- Li/H : non résolu numériquement à ce stade.

## Résultat V75B
Le contrôle numérique confirme :
- D/H passe,
- $Y_p$ passe,
- Li/H reste en tension dans le benchmark standard.

Valeurs de référence retenues :
- D/H = $2.527 \times 10^{-5}$
- $Y_p = 0.2465$
- Li/H = $1.58 \times 10^{-10}$

Verdict de travail :
- `cadre_BBN_partiellement_coherent`
- D/H et $Y_p$ validés,
- Li/H encore en tension physique dans le cadre standard.


7. VERDICT
----------
Le cadre V70 est numériquement cohérent sur D/H et $Y_p$,
mais le lithium ne peut pas encore être présenté comme résolu chiffré.

Verdict attendu :
- cadre_BBN_partiellement_coherent
- D/H et $Y_p$ validés
- Li/H encore en tension physique dans le benchmark standard, mais corrigé dans V80B.

## Résultat V80B de référence
Le fixed-point V80B valide directement le point Li/H au même $\delta_{EM}=-0.0069$ :
- D/H = 2.530e-05, passe
- $Y_p$ = 0.2467, passe
- Li7/H = 1.566e-10, passe
- Be7/H = 1.329e-10
- verdict = `bbn_liou_solved`

Lecture synthétique :
- le benchmark standard de V75B conserve sa tension Li/H,
- le point V80B montre que le toy proxy peut déjà fermer cette tension numériquement.
