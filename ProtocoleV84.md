# V84 — EXTENSION COSMO : EXPANSION, STRUCTURE, CMB
# Version : 1.0 — Mode confrontation cosmologique, epsilon fixé
# Auteur : Jean-Philippe
# Objet : tester l’impact cosmologique global de la bande physique epsilon
#         issue de V82–V83 sur H(z), distances, croissance et CMB.

Protocole précédent : V83 (calibration globale : gravité, temps, NS)
Protocole suivant : V85B (réparation cosmologique après V84)

Wrapper suggéré :
- python/scripts/runv84_cosmo_extension.py

CONTENU :
- 0. Objectif
- 1. Entrées
- 2. Hypothèse clé V84
- 3. Pipeline V84
- 4. Critères d’acceptation
- 5. Résultat attendu V84
- 6. Transition

0. OBJECTIF
-----------
Prendre la bande physique epsilon issue de V82–V83 et tester son impact
cosmologique global :

- expansion H(z),
- densité critique et paramètres Omega,
- croissance de structure,
- signatures CMB,
- cohérence globale avec LambdaCDM.

V84 ne retouche plus epsilon : epsilon = epsilon_best = -0.0069 est fixé.
On teste si le cosmos accepte cette déformation D1.


1. ENTRÉES
----------
1. Paramètre fondamental
- epsilon_best = -0.0069
- bande epsilon in [-0.0076, -0.0063] pour la robustesse du scan

2. Fonctions issues de V81–V83
- delta_EM(epsilon)
- pi_n(epsilon, rho)
- G_eff(epsilon, rho)
- F_temps(epsilon, rho)

3. Cosmo de référence
- modele LambdaCDM standard (Planck-like)
- H0, Omega_m, Omega_Lambda, Omega_b, Omega_r
- distances DA(z), DL(z)
- croissance f_sigma8(z)
- CMB : distance de recombinaison et position du premier pic


2. HYPOTHÈSE CLÉ V84
--------------------
À l’échelle cosmologique diffuse, on prend pi_n^{cosmo} petit mais non nul.

- Cas A : pi_n^{cosmo} ~ 0
  - cosmologie quasi standard

- Cas B : pi_n^{cosmo} ~ 10^-2 à 10^-1
  - cosmologie légèrement déformée

On teste si la bande epsilon reste compatible dans les deux cas.


3. PIPELINE V84
---------------
Pour chaque epsilon et chaque hypothèse sur pi_n^{cosmo} :

1) Calculer G_eff^{cosmo}(epsilon) et F_temps^{cosmo}(epsilon).
2) Modifier les équations de Friedmann toy.
3) Recalculer H(z), DA(z), DL(z) et les comparer à SN/BAO/CMB.
4) Recalculer un proxy f_sigma8(z).
5) Vérifier la distance angulaire et la position du premier pic CMB.
6) Construire un chi2_cosmo phenomenologique.


4. CRITÈRES D’ACCEPTATION
-------------------------
Une valeur epsilon est retenue si :

- BBN validée par V80–V82,
- local validé par V82–V83,
- cosmologie compatible avec SN, BAO, CMB et croissance,
- pas de décalage catastrophique des pics CMB.


5. RÉSULTAT ATTENDU V84
----------------------
Deux scénarios possibles :

1) Bande cosmologique confirmée
- la bande epsilon reste compatible,
- la même deformation D1 explique BBN, NS et cosmologie.

2) Rupture cosmologique
- une partie de la bande est exclue,
- V84 identifie la sous-bande viable ou l’étage à raffiner.


RÉSULTAT CHIFFRÉ — EXÉCUTION V84
---------------------------------
Statut du run : réussi, mais avec rupture cosmologique dans ce modèle jouet.

Grille utilisée :
- epsilon ∈ [-0.0076, -0.0063] avec 14 points
- pi_n^{cosmo} ∈ {0.0, 0.01, 0.03, 0.1}
- taille totale de la grille : 56 points

Point le plus favorable :
- best_fit_epsilon = -0.0076
- best_fit_pi_cosmo = 0.0
- best_fit_G_eff_cosmo = 1.0
- best_fit_F_temps_cosmo = 1.0

Verdict global :
- verdict = cosmo_rupture
- accepted_count = 0/56
- epsilon_min_acceptable = None
- epsilon_max_acceptable = None

Score du meilleur point :
- best_fit_chi_total = 2260.618411984395
- best_fit_chi_sn = 0.0
- best_fit_chi_bao = 2222.2222222222226
- best_fit_chi_cmb = 5.535026856094648
- best_fit_chi_growth = 32.86116290607792
- best_fit_DA_rec = 10.38260259907672
- best_fit_first_peak_shift = 0.0

Lecture physique :
- le canal BAO domine largement la rupture dans ce proxy cosmologique,
- le canal croissance contribue aussi à la tension,
- le canal SN reste quasi standard dans le meilleur point,
- aucune sous-bande epsilon ne reste viable dans cette configuration toy.

Fichiers produits :
- v84_cosmo_extension_results.csv
- v84_cosmo_extension_summary_20260522-090846Z.json
- v84_cosmo_extension_summary_20260522-090846Z.txt


6. TRANSITION
------------
- Si bande confirmée : V84 devient la base d’un papier de synthèse.
- Si bande partiellement ou totalement exclue : V84 sert de point de rupture
  propre et localise où D1 doit être corrigé.