# V77D — AUTOPSIE A=7 AVEC COMPENSATION ÉLECTRONIQUE
# Version : 1.0 — Mode recherche, niveau triplet e–p–n
# Auteur : Jean-Philippe
# Objet : tester si une compensation électronique peut réduire Li_total dans le proxy A=7

Protocole précédent : ProtocoleV77C.md
Protocole suivant : V78R (si un levier réel est identifié)

Wrapper global suggéré :
- python/scripts/runv77d_triplet_epn.py

CONTENU :
- 0. Objectif
- 1. Hypothèses
- 2. Nouveaux paramètres
- 3. Questions de recherche
- 4. Pipeline V77D
- 5. Sorties attendues
- 6. Transition

0. OBJECTIF
-----------
Étendre l’autopsie A=7 en intégrant le rôle de l’électron dans le triplet e–p–n.

V77D cherche à :
- tester si une compensation électronique peut réduire Li_total,
- explorer l’effet de l’écrantage coulombien,
- explorer l’effet sur la capture électronique Be-7 → Li-7,
- comprendre si l’électron peut fournir le canal compensateur manquant.

V77D n’est pas un pipeline de calibration mais un test de physique fondamentale.


1. HYPOTHÈSES
-------------
- On garde les paramètres globaux :
  - $\varepsilon_{best} = -0.0069$
  - $\delta_{EM} = -0.0069$
  - $k_G$, $k_T$, $k_n$ = V83
- On ne modifie pas :
  - $\alpha_{Be}$ (fixé à 1.0)
  - les taux Li / Be (fixés)
- On ajoute un nouveau degré de liberté :
  - $\beta_e$ = paramètre de compensation électronique.


2. NOUVEAUX PARAMÈTRES (ÉLECTRON)
---------------------------------
$\beta_e$ représente l’effet électronique effectif dans le triplet e–p–n.

Il agit sur deux zones :

1) Écrantage coulombien (BBN précoce)
   - modifie la barrière EM effective dans les réactions A=7
   - modélisé comme un facteur multiplicatif sur les termes EM :
     $\delta_{EM}^{eff} = \delta_{EM} \cdot \beta_e$

2) Capture électronique tardive Be-7 + e– → Li-7
   - modifie la vitesse de conversion Be-7 → Li-7
   - modélisé comme un facteur sur la branche Be-7 :
     $Be7_{eff} = Be7 \cdot f(\beta_e)$

Plage de test :
- $\beta_e \in [0.8, 1.2]$


3. QUESTIONS DE RECHERCHE
-------------------------
V77D doit répondre à :

1) L’électron peut-il fournir un canal compensateur A=7 ?
   - via l’écrantage (BBN précoce)
   - via la capture e– (post-BBN)

2) $\beta_e$ modifie-t-il réellement Li_total ?
   - Li-7/H
   - Be-7/H
   - Li_total = Li7 + Be7

3) $\beta_e$ peut-il casser la rigidité de la branche Be-7 ?
   - si oui → direction physique
   - si non → verrou structurel confirmé


4. PIPELINE V77D
----------------

4.1 Grille de test
------------------
- $\delta_{EM}$ fixé à $-0.0069$
- $\alpha_{Be}$ fixé à 1.0
- $\beta_e \in [0.8, 1.2]$ avec 5 points

Pour chaque $\beta_e$ :
- calculer Li-7/H
- calculer Be-7/H
- calculer Li_total
- enregistrer les variations relatives.


4.2 Modèle électronique
-----------------------
Implémenter :

1) Écrantage :
   $\delta_{EM}^{eff} = \delta_{EM} \cdot \beta_e$

2) Capture électronique :
   $Be7_{eff} = Be7 \cdot (1 - 0.3 \cdot (\beta_e - 1))$

3) Li_total = Li7 + Be7_eff


4.3 Analyse
-----------
Pour chaque $\beta_e$ :
- comparer Li_total($\beta_e$) à Li_total($\beta_e = 1$)
- tracer Li7($\beta_e$)
- tracer Be7($\beta_e$)
- tracer Li_total($\beta_e$)

Identifier :
- $\beta_e$ qui minimise Li_total
- amplitude de la variation
- stabilité de D/H et $Y_p$ (doivent rester quasi fixes)


4.4 Critère de direction
------------------------
Une direction physique existe si :
- Li_total($\beta_e$) descend significativement (>10%)
- sans casser D/H et $Y_p$
- et sans rendre Li-7/H non physique


5. SORTIES ATTENDUES
--------------------
- V77D_ELECTRON_SCAN.txt
- courbes Li7 vs $\beta_e$
- courbes Be7 vs $\beta_e$
- courbes Li_total vs $\beta_e$
- un tableau des variations relatives
- une phrase claire :
  > "$\beta_e$ ouvre / n’ouvre pas une direction physique pour compenser A=7."


## Résultat V77D
Le scan électronique confirme une direction physique ouverte :
- verdict : `direction_physique_ouverte`
- beta_e de base : $1.0$
- meilleur beta_e : $1.2$
- Li_total/H de base : $2.895706\times 10^{-10}$
- Li_total/H au meilleur point : $2.225\times 10^{-10}$
- baisse relative de Li_total : $23.15\%$

Statut de passage au meilleur point :
- D/H : passe
- $Y_p$ : passe
- Li-7/H : passe
- Li_total/H : ne passe pas encore la fenêtre observationnelle

Meilleur point :
- D/H = $2.546\times 10^{-5}$
- $Y_p = 0.246676$
- Li-7/H = $1.230\times 10^{-10}$
- Be-7/H = $9.950\times 10^{-11}$

Lecture :
- D/H et $Y_p$ restent acceptables,
- Li_total baisse de plus de 10%,
- l’électron fournit donc un levier compensateur réel dans ce proxy jouet.


6. TRANSITION
-------------
- Si $\beta_e$ ouvre une direction :
  → V78R = intégration d’un canal électronique réel (écrantage + capture e–)
- Si $\beta_e$ ne change rien :
  → le verrou est purement nucléaire, pas électronique
  → V78R devra réviser la structure A=7 elle-même.

V77D est un test de physique fondamentale, pas un ajustement.
Il doit dire si l’électron peut jouer un rôle compensateur réel.