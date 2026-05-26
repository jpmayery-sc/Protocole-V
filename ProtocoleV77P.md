# V77P — PROJECTION BBN A=7 AVEC BLOC EM EFFECTIF
# Version : 1.0 — Mode test, ajout d’un bloc EM minimal sur la bande lithium
# Auteur : Jean-Philippe
# Objet : tester si un bloc EM effectif raisonnable peut desserrer la rigidité
#         observée sur le secteur A=7 dans V77N / V77O.

Protocole précédent : V77O (géométrie temporelle A=7)
Protocole suivant : V77Q (test jouet de survie A=7)

Wrapper suggéré :
- python/scripts/runv77p_em_block.py

CONTENU :
- 0. Objectif
- 1. Rappel du blocage A=7
- 2. Ajout du bloc EM effectif
- 3. Projection EM sur la grille A=7
- 4. Analyse de structure EM vs no-EM
- 5. Sorties attendues
- 6. Critères de succès
- 7. Transition vers V79P

0. OBJECTIF
-----------
V77P teste une question très précise :

> “Si l’on ajoute un bloc EM effectif minimal au secteur A=7,
>  la bande lithium se desserre-t-elle, ou la rigidité structurelle reste-t-elle
>  essentiellement inchangée ?”

L’idée n’est pas de remplacer la physique, mais de projeter un mode EM effectif
sur la grille A=7 pour voir si la direction la plus raide devient plus souple.


1. RAPPEL DU BLOCAGE A=7
------------------------
Les protocoles V77N et V77O ont montré que :

- le pincement lithium reste présent,
- la bande acceptable est étroite,
- le diagnostic dominant reste Li_total/H,
- changer le temps d’observation ne suffit pas à ouvrir la bande.

V77P part donc du point V77O et ajoute une nouvelle hypothèse :

- un bloc EM effectif peut modifier la réponse du secteur A=7,
- en introduisant une anisotropie douce dans le transport/stockage du lithium,
- sans casser le reste de la structure.


2. AJOUT DU BLOC EM EFFECTIF
----------------------------
On introduit deux paramètres effectifs :

- B_eff : intensité magnétique effective adimensionnée
- E_ind : terme électrique induit effectif adimensionné

Dans ce cadre jouet, EM agit principalement comme une correction de projection :

- Li7/H est légèrement modulé,
- Be7/H est légèrement modulé,
- Li_total/H = Li7/H + Be7/H est la quantité de contrôle principale,
- D/H et Y_p restent proches du point de départ mais peuvent bouger faiblement.

Le but est de tester si le bloc EM crée une direction plus souple,
pas d’affirmer une microphysique réaliste.


3. PROJECTION EM SUR LA GRILLE A=7
----------------------------------
Pour une grille autour du meilleur point A=7 de V77O/V79BIS, on compare trois surfaces :

- S_EM_OFF : B_eff = 0, E_ind = 0
- S_EM_SOFT : B_eff modéré, E_ind modéré
- S_EM_STRONG : B_eff plus fort, E_ind plus fort

Pour chaque point de la grille :

- on calcule D/H, Y_p, Li7/H, Be7/H, Li_total/H,
- on applique ensuite la projection EM,
- on recalcule les chi-scores,
- on suit la largeur de la bande acceptée et la meilleure valeur de chi_sum.

Le point important n’est pas seulement le nombre de points acceptés,
mais aussi si le minimum de chi_sum descend et si la surface devient plus plate.


4. ANALYSE DE STRUCTURE EM VS NO-EM
-----------------------------------
V77P compare :

- la bande no-EM,
- la bande EM soft,
- la bande EM strong.

Signaux recherchés :

- amélioration du meilleur chi_sum,
- élargissement de la fenêtre Li_total/H,
- réduction de la sensibilité au couplage drain/exchange,
- apparition d’un comportement plus mou sans instabilité.

Critère conceptuel :

- si EM ne change rien, le pincement reste structurel,
- si EM abaisse nettement le chi_sum et élargit la bande, alors le bloc EM
  fournit une direction manquante.


5. SORTIES ATTENDUES
--------------------
- v77p_results_S_EM_OFF.csv
- v77p_results_S_EM_SOFT.csv
- v77p_results_S_EM_STRONG.csv
- v77p_Li_total_vs_beta_e_phys.png
- v77p_Li_surface_gamma_phys.png
- V77P_EM_BLOCK_REPORT.txt


RÉSULTAT CHIFFRÉ — EXÉCUTION V77P
---------------------------------
Statut du run : réussi.

Grille utilisée :
- beta_e_phys ∈ [0.96, 1.04] avec 9 points
- gamma_exch_phys ∈ [1.03, 1.15] avec 7 points
- gamma_drain_phys ∈ [0.56, 0.72] avec 9 points
- taille totale de la grille : 567 points

Point le plus favorable (sur la surface no-EM) :
- beta_e_phys = 1.0
- gamma_exch_phys = 1.09
- gamma_drain_phys = 0.64

Verdict global :
- verdict = mixed_em_response
- best_surface = S_EM_OFF
- dominant_surface = S_EM_OFF

Balayage fin autour de zéro EM :
- meilleur réglage trouvé : B_eff = 0.0, E_ind = 0.0
- best_tuning_chi_sum = 0.0033936651583709823
- conclusion : aucun voisin EM plus favorable n’a dépassé le cas sans EM

Synthèse par surface :
- S_EM_OFF : accepted = 567, components = 9, best_chi_sum = 0.0033936651583709823, softness = 1.0
  - beta_span = (0.96, 1.04)
  - gamma_exch_span = (1.03, 1.15)
  - gamma_drain_span = (0.56, 0.72)
- S_EM_SOFT : accepted = 567, components = 9, best_chi_sum = 0.15575746367443422, softness = 0.7142857142857142
  - beta_span = (0.96, 1.04)
  - gamma_exch_span = (1.03, 1.15)
  - gamma_drain_span = (0.56, 0.72)
- S_EM_STRONG : accepted = 541, components = 9, best_chi_sum = 0.37683198814037383, softness = 0.5555555555555556
  - beta_span = (0.96, 1.04)
  - gamma_exch_span = (1.03, 1.15)
  - gamma_drain_span = (0.56, 0.72)

Lecture physique :
- le bloc EM effectif modifie bien la réponse locale, mais il ne fournit pas
  une ouverture nette de la bande acceptable;
- la surface EM strong réduit même légèrement le nombre de points acceptés;
- le meilleur minimum reste sur la surface no-EM, donc le système ne gagne pas
  une direction moue robuste grâce à ce bloc EM minimal;
- la rigidité A=7 reste donc principalement structurelle.

Fichiers produits :
- v77p_results_S_EM_OFF.csv
- v77p_results_S_EM_SOFT.csv
- v77p_results_S_EM_STRONG.csv
- v77p_em_tuning_scan.csv
- v77p_Li_total_vs_beta_e_phys.png
- v77p_Li_surface_gamma_phys.png
- v77p_em_tuning_scan_heatmap.png
- V77P_EM_BLOCK_REPORT.txt


6. CRITÈRES DE SUCCÈS
---------------------
V77P est réussi si le bloc EM :

- ouvre un mode plus mou,
- ou améliore clairement le meilleur chi_sum,
- ou élargit la bande Li_total/H,
- sans déstabiliser D/H et Y_p.

S’il ne change pas le diagnostic, V77P conclut que le bloc EM minimal n’est
pas le bon levier pour casser le pincement.


7. TRANSITION VERS V79P
-----------------------
Deux cas :

1) EM aide :
   - V79P devient l’étape de contrôle fine pour voir si le pincement Li reste
     compatible avec le bloc EM.

2) EM n’aide pas :
   - V79P sert à confirmer que le pincement est structurel malgré le bloc EM.

V77P est donc le test de projection : on ajoute le secteur EM minimal et on
mesure s’il desserre réellement la bande A=7.