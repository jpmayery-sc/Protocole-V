# V77N — STABILITÉ + TEST LITHIUM CIBLÉ
# Version : 1.1 — Mode synthèse, focus sur le blocage Li
# Auteur : Jean-Philippe
# Objet : tester la robustesse de la zone acceptable en mettant
#         le lithium (Li7/H, Li_total/H) au centre de l’analyse.

Protocole précédent : V77M (re-validation + readout)
Protocole suivant : V77O (géométrie temporelle A=7)

Wrapper suggéré :
- python/scripts/runv77n_stability_and_lithium_focus.py

CONTENU :
- 0. Objectif
- 1. Rappels des contraintes lithium
- 2. Module A — Stabilité de la zone acceptable
- 3. Module B — Tests lithium ciblés
- 4. Pipeline V77N
- 5. Sorties attendues
- 6. Critères de décision (V80 ou pas)
- 7. Transition

0. OBJECTIF
-----------
V77N vise à répondre à une question précise :

> “Est-ce qu’il existe une zone de paramètres physiques
>  où Li7/H et Li_total/H sont dans la fenêtre,
>  sans casser D/H et Y_p, et cette zone est-elle robuste ?”

On reprend le moteur physique V77L + la validation V77M,
et on ajoute des tests centrés sur le lithium, là où le modèle est historiquement coincé.


1. RAPPELS DES CONTRAINTES LITHIUM
----------------------------------
On fixe explicitement les fenêtres (à adapter selon la compilation choisie) :

- D/H_obs ± sigma_D
- Y_p_obs ± sigma_Y
- Li7/H_obs ± sigma_Li7
- Li_total/H_obs (si tu veux une fenêtre explicite sur la somme)

Exemple jouet (à remplacer par tes vraies valeurs) :
- D/H_obs ≈ 2.5×10^-5
- Y_p_obs ≈ 0.245–0.247
- Li7/H_obs ≈ (1–2)×10^-10
- Li_total/H_obs ≈ (1–3)×10^-10

V77N doit toujours distinguer :
- Li7/H seul,
- Li_total/H = Li7/H + Be7/H.


2. MODULE A — STABILITÉ DE LA ZONE ACCEPTABLE
---------------------------------------------
On reprend la zone trouvée dans V77M :

- beta_e_phys ≈ 1.1
- gamma_exch_phys ≈ 0.5
- gamma_drain_phys ≈ 0.25

2.1 Raffinement local
---------------------
Grille fine autour du meilleur point :

- beta_e_phys ∈ [1.05, 1.15] pas 0.01
- gamma_exch_phys ∈ [0.4, 0.6] pas 0.02
- gamma_drain_phys ∈ [0.15, 0.35] pas 0.02

Pour chaque point :
- lancer le backend (ou l’adapter V77L),
- récupérer D/H, Y_p, Li7/H, Be7/H, Li_total/H,
- calculer chi_D, chi_Y, chi_Li7 (et éventuellement chi_Litot),
- marquer ACCEPTÉ si :
  - |chi_D| ≤ chi_max_D,
  - |chi_Y| ≤ chi_max_Y,
  - Li7/H et Li_total/H dans leurs fenêtres.

Objectif :
- voir si la zone ACCEPTÉE est connectée ou fragmentée.

2.2 Élargissement de grille
---------------------------
Grille plus large :

- beta_e_phys ∈ [0.7, 1.3]
- gamma_exch_phys ∈ [0, 1.2]
- gamma_drain_phys ∈ [0, 0.7]

Même logique de filtrage.

Objectif :
- voir si la zone Li-acceptable est un îlot isolé ou une bande.


3. MODULE B — TESTS LITHIUM CIBLÉS
----------------------------------
Ici, on met le focus explicitement sur Li.

3.1 Cartographie Li7/H seule
----------------------------
Pour chaque point de la grille :

- tracer Li7/H(beta_e_phys) pour quelques couples (gamma_exch_phys, gamma_drain_phys) fixés,
- tracer Li7/H(gamma_exch_phys, gamma_drain_phys) pour un beta_e_phys fixé.

On produit :
- des courbes Li7/H vs beta_e_phys,
- des cartes Li7/H(gamma_exch_phys, gamma_drain_phys).

Objectif :
- voir si Li7/H peut descendre dans la fenêtre sans tomber dans des valeurs non physiques.

3.2 Cartographie Li_total/H
---------------------------
Même chose pour Li_total/H :

- courbes Li_total/H(beta_e_phys),
- cartes Li_total/H(gamma_exch_phys, gamma_drain_phys).

Objectif :
- vérifier que la somme Li7+Be7 est dans la fenêtre,
- et que la réduction ne vient pas d’un artefact (ex : Be7 négatif).

3.3 Test de “bascule A=7”
-------------------------
On définit un critère de renversement A=7 :

- Be7/H < f_threshold × Li7/H
  (par ex. f_threshold = 0.2)

On marque les points où :
- Li_total/H dans la fenêtre,
- D/H et Y_p OK,
- Be7/H suffisamment vidé.

Objectif :
- voir si le renversement A=7 (Be7 vidé, Li7 acceptable) existe vraiment
  dans une zone non ultra-fine.

3.4 Profil “Lithium only”
-------------------------
On construit un profil 1D :

- on suit une ligne dans l’espace (beta_e_phys, gamma_exch_phys, gamma_drain_phys)
  qui traverse la zone acceptable,
- on trace :
  - D/H,
  - Y_p,
  - Li7/H,
  - Li_total/H
  le long de cette ligne.

Objectif :
- voir si le “fix lithium” est un effet local ou une transition douce.


4. PIPELINE V77N
----------------
4.1 Exécution
-------------
- Charger la config V77L (leviers physiques actifs),
- Charger la grille V77M (pour point de départ),
- Construire les grilles raffinée et élargie,
- Lancer tous les runs (backend réel ou adapter V77L),
- Stocker les résultats dans des DataFrame.

4.2 Analyse
-----------
- Appliquer le filtrage observationnel,
- Identifier :
  - nombre de points ACCEPTÉS,
  - largeur de la zone Li-acceptable,
  - existence d’un renversement A=7 (Be7 vidé, Li7 OK),
- Reconstruire :
  - courbes Li7/H et Li_total/H,
  - cartes Li7/H et Li_total/H.

4.3 Lecture
-----------
- Générer un rapport texte :
  - V77N_STABILITY_AND_LITHIUM_REPORT.txt
  contenant :
  - résumé chiffré,
  - lecture qualitative,
  - verdict sur le lithium :
    - “Li fixé de façon robuste / moyenne / ultra-fine / non fixé”,
  - recommandation V80 ou pas.


5. SORTIES ATTENDUES
--------------------
- v77n_results_refined.csv
- v77n_results_extended.csv
- v77n_results_lithium_flags.csv
  (avec colonnes : Li7_OK, Li_total_OK, A7_flipped, ACCEPTED)

- Figures :
  - v77n_Li7_vs_beta_e_phys.png
  - v77n_Litot_vs_beta_e_phys.png
  - v77n_Li7_surface_gamma_phys.png
  - v77n_Litot_surface_gamma_phys.png
  - v77n_A7_flip_map.png

- Rapport :
  - V77N_STABILITY_AND_LITHIUM_REPORT.txt
- Décision :
  - V77N_DECISION.json


6. CRITÈRES DE DÉCISION (V80 OU PAS)
------------------------------------
V80 est recommandé si :

- il existe une zone connectée où :
  - D/H et Y_p sont dans leurs fenêtres,
  - Li7/H est dans la fenêtre,
  - Li_total/H est dans la fenêtre,
  - Be7/H est suffisamment vidé (renversement A=7),
- cette zone n’est pas ultra-fine (plusieurs points voisins),
- les valeurs de beta_e_phys, gamma_exch_phys, gamma_drain_phys restent plausibles.

Sinon :
- V80 non recommandé,
- retour en V79BIS pour affiner le moteur ou conclure à une rigidité forte.


7. TRANSITION
-------------
- Si V77N conclut :
  - “Li fixé de façon robuste / moyenne” → V80 peut généraliser.
  - “Li fixé seulement de façon ultra-fine” → V80 à manier avec prudence.
  - “Li non fixé” → V79BIS pour revoir les hypothèses.

V77N est le test de vérité lithium :
c’est là que tu vois si ton renversement A=7 tient vraiment,
ou si le lithium reste le verrou dur de la BBN.

RÉSULTAT CHIFFRÉ — ZOOM RESSERRÉ AUTOUR DU MEILLEUR POINT
---------------------------------------------------------
Date du run : 20260521-154314Z
Mode : dry-run adapter via V77L, zoom local autour du meilleur point V77N

Synthèse numérique :

- best_fit_beta_e_phys : 1.0
- best_fit_gamma_exch_phys : 1.09
- best_fit_gamma_drain_phys : 0.64
- best_fit_chi_sum : 3.3936651583709823e-03
- accepted_count : 605
- accepted_components : 5
- dominant_bottleneck : bande acceptable encore trop fine
- dominant_metric : Li_total/H
- beta_span : (0.98, 1.02)
- gamma_exch_span : (1.05, 1.15)
- gamma_drain_span : (0.6, 0.7)

Lecture physique plus directe :

- le zoom resserré confirme que le point de meilleur compromis est stable,
  mais que la géométrie reste un ruban très fin autour de Li_total/H.
- gamma_drain_phys est l’axe le plus contraignant: c’est lui qui pince la zone
  acceptable le plus vite, donc la physique du blocage est d’abord un problème
  de vidage A=7 insuffisamment large.
- beta_e_phys reste aussi resserré dans le zoom, ce qui veut dire que le levier
  électronique n’est pas totalement décoratif: il participe au réglage fin.
- gamma_exch_phys élargit légèrement la bande, mais ne suffit pas à lui seul à
  transformer le ruban en bande robuste.
- en clair: le défaut n’est plus l’absence d’un point acceptable, mais le fait
  que Li_total/H accepte seulement un voisinage étroit du meilleur point.

Fichiers générés :

- results/result-analyse/v77n_stability_and_lithium_focus/v77n_results_focused.csv
- results/result-analyse/v77n_stability_and_lithium_focus/V77N_FOCUSED_LITHIUM_REPORT.txt
- results/result-analyse/v77n_stability_and_lithium_focus/v77n_focused_decision_20260521-154314Z.json
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_focused_Li7_vs_beta_e_phys.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_focused_Litot_vs_beta_e_phys.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_focused_Li7_surface_gamma_phys.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_focused_Litot_surface_gamma_phys.png

RÉSULTAT CHIFFRÉ — STABILITÉ + LITHIUM
-------------------------------------
Date du run : 20260521-153636Z
Mode : dry-run adapter via V77L, backend réel non branché dans ce workspace

Synthèse numérique :

- verdict : not_recommended_for_v80
- refined_accepted : 1296/1331
- extended_accepted : 926/2535
- li7_ok : 926
- li_total_ok : 926
- a7_flipped : 2535
- robustness : ultra-fine
- li_verdict : Li fixé seulement de façon ultra-fine
- recommendation : V80 à manier avec prudence
- best_fit_beta_e_phys : 1.0
- best_fit_gamma_exch_phys : 1.1
- best_fit_gamma_drain_phys : 0.65

Lecture rapide :

- la zone Li-acceptable existe, mais elle reste très contrainte dans la grille
  élargie.
- le renversement A=7 est présent sur la grille testée, mais il ne dessine pas
  encore une bande robuste.
- la stabilité est réelle dans l’adapter, mais le blocage lithium n’est pas
  levé de façon convaincante au sens d’un passage V80 franc.

Fichiers générés :

- results/result-analyse/v77n_stability_and_lithium_focus/v77n_results_refined.csv
- results/result-analyse/v77n_stability_and_lithium_focus/v77n_results_extended.csv
- results/result-analyse/v77n_stability_and_lithium_focus/v77n_results_lithium_flags.csv
- results/result-analyse/v77n_stability_and_lithium_focus/V77N_STABILITY_AND_LITHIUM_REPORT.txt
- results/result-analyse/v77n_stability_and_lithium_focus/v77n_decision_20260521-153636Z.json
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_Li7_vs_beta_e_phys.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_Litot_vs_beta_e_phys.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_Li7_surface_gamma_phys.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_Litot_surface_gamma_phys.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_A7_flip_map.png
- results/result-analyse/v77n_stability_and_lithium_focus/plots/v77n_lithium_profile.png