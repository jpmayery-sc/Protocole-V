# V78H — VALIDATION SUR DONNÉES RÉELLES ET EXPORT
# Version : 1.0 — Mode validation, ancrage observationnel + fichiers téléchargeables
# Auteur : Jean-Philippe
# Objet : confronter la géométrie de courbe A=7 (beta_e, gamma_exch, gamma_drain)
#         à des données réelles (observations + BBN réel) et produire des sorties
#         propres à télécharger (tables, courbes, notebook).

Protocole précédent : V78R (premier ancrage au réel / code BBN)
Protocole suivant : V79X (interprétation physique / publication interne)

Wrapper global suggéré :
- python/scripts/runv78h_realdata_validation.py

CONTENU :
- 0. Objectif
- 1. Données réelles utilisées
- 2. Paramètres et runs BBN
- 3. Pipeline V78H
- 4. Sorties téléchargeables
- 5. Critères de validation
- 6. Transition

0. OBJECTIF
-----------
V78H vise à :

- comparer la géométrie de courbe du proxy A=7 (V77G) à :
  - des prédictions d’un code BBN réel,
  - des contraintes observationnelles réelles (D/H, Y_p, Li plateau),
- vérifier que les points “bons” du modèle (beta_e, gamma_exch, gamma_drain)
  restent compatibles avec les données,
- produire des fichiers téléchargeables (CSV, figures, notebook) pour analyse hors Colab.

V78H = validation “chiffres réels + fichiers propres”.


1. DONNÉES RÉELLES UTILISÉES
----------------------------
V78H doit expliciter les jeux de données :

1) Observations BBN :
   - D/H_obs ± sigma_D
   - Y_p_obs ± sigma_Y
   - Li7/H_obs ± sigma_Li
   - éventuellement He3/H_obs, T/H_obs si disponibles.

   Les valeurs numériques exactes (centrales + incertitudes) doivent être renseignées
   dans un bloc de configuration, par exemple :

   - D/H_obs ≈ 2.5×10^-5
   - Y_p_obs ≈ 0.245–0.247
   - Li7/H_obs ≈ (1–2)×10^-10

   (à ajuster selon les compilations choisies).

2) Prédictions BBN réelles :
   - issues d’un code public (AlterBBN, PArthENoPE, etc.),
   - pour un modèle standard (LCDM, N_eff standard, etc.),
   - fournissant : D/H, Y_p, Li7/H, Be7/H, Li_total/H.

3) Proxy A=7 (jouet) :
   - résultats V77G (beta_e, gamma_exch, gamma_drain, Li7, Be7, Li_total),
   - utilisés comme “géométrie cible”.


2. PARAMÈTRES ET RUNS BBN
-------------------------
V78H doit définir clairement :

1) Paramètres cosmologiques fixés :
   - baryon density (Omega_b h^2),
   - N_eff,
   - tau_n,
   - etc.
   (valeurs choisies cohérentes avec la littérature).

2) Paramètres “type beta_e / gamma_drain / gamma_exch” dans le code réel :
   - un paramètre lié à l’électron (écrantage / capture e–) jouant le rôle de beta_e_phys,
   - un paramètre ou facteur sur les canaux de destruction A=7 jouant le rôle de gamma_drain_phys,
   - éventuellement un paramètre effectif sur les chaînes Be7 ↔ Li7 jouant gamma_exch_phys.

3) Grilles de runs :
   - beta_e_phys ∈ [beta_min, beta_max] (quelques points),
   - gamma_drain_phys ∈ [0, gamma_drain_max],
   - gamma_exch_phys ∈ [0, gamma_exch_max].

Chaque run BBN réel doit produire un jeu complet d’abondances.


3. PIPELINE V78H
----------------

3.1 Configuration et téléchargement
-----------------------------------
- Télécharger / installer le code BBN choisi (si besoin) :
  - via un script shell ou un bloc Colab (git clone, compilation, etc.).
- Configurer un répertoire de sortie :
  - /content/v78h_outputs/
  - destiné à contenir les CSV, figures, notebook.

3.2 Exécution des runs BBN
--------------------------
Pour chaque triplet (beta_e_phys, gamma_exch_phys, gamma_drain_phys) :

- lancer le code BBN réel,
- récupérer :
  - D/H, Y_p,
  - Li7/H, Be7/H, Li_total/H,
- stocker dans un tableau (pandas DataFrame) avec les paramètres associés.

3.3 Filtrage par fenêtres observationnelles
-------------------------------------------
Pour chaque point :

- calculer les écarts normalisés :
  - chi_D = (D/H - D/H_obs) / sigma_D
  - chi_Y = (Y_p - Y_p_obs) / sigma_Y
  - chi_Li = (Li7/H - Li7/H_obs) / sigma_Li (optionnel)
- définir un critère de passage :
  - |chi_D| <= chi_max_D
  - |chi_Y| <= chi_max_Y
  - et éventuellement |chi_Li| <= chi_max_Li

Marquer les points “ACCEPTÉS” (tous les canaux corrects) et “REJETÉS”.

3.4 Comparaison de géométrie de courbe
--------------------------------------
- reconstruire :
  - Li_total(beta_e_phys) pour des gamma_exch_phys, gamma_drain_phys fixés,
  - Li_total(gamma_exch_phys, gamma_drain_phys) pour un beta_e_phys fixé,
- comparer qualitativement à la géométrie V77G :
  - pente nette en beta_e_phys,
  - surface en bande en (gamma_exch_phys, gamma_drain_phys),
  - existence d’une zone de passage de largeur moyenne.

3.5 Génération des fichiers téléchargeables
-------------------------------------------
- Sauvegarder les tableaux complets au format CSV :
  - v78h_results_full.csv
  - v78h_results_accepted.csv (points qui passent les fenêtres)
- Sauvegarder les figures :
  - v78h_Litot_vs_beta_e.png
  - v78h_Litot_surface_gamma.png
  - v78h_DH_vs_param.png (optionnel)
- Sauvegarder un notebook récapitulatif (si généré par script) :
  - v78h_analysis.ipynb


4. SORTIES TÉLÉCHARGEABLES
--------------------------
V78H doit produire au minimum :

1) Fichiers CSV :
   - v78h_results_full.csv :
     - colonnes : beta_e_phys, gamma_exch_phys, gamma_drain_phys,
                  D/H, Y_p, Li7/H, Be7/H, Li_total/H,
                  flags de passage.
   - v78h_results_accepted.csv :
     - sous-ensemble des points qui passent les fenêtres.

2) Figures :
   - courbe Li_total(beta_e_phys) avec surlignage des points acceptés,
   - carte Li_total(gamma_exch_phys, gamma_drain_phys) avec masque de passage,
   - éventuellement D/H et Y_p en fonction des mêmes paramètres.

3) Résumé texte :
   - V78H_REALDATA_SUMMARY.txt :
     - nombre de points acceptés,
     - meilleure zone (beta_e_phys*, gamma_exch_phys*, gamma_drain_phys*),
     - comparaison qualitative avec la géométrie V77G.

4) Optionnel :
   - un notebook v78h_analysis.ipynb prêt à être téléchargé et rouvert localement.


5. CRITÈRES DE VALIDATION
-------------------------
V78H doit répondre clairement :

1) Le code BBN réel peut-il reproduire :
   - une pente Li_total(beta_e_phys) similaire à celle du jouet ?
   - une surface Li_total(gamma_exch_phys, gamma_drain_phys) en bande,
     avec une zone de passage non ultra-fine ?

2) Existe-t-il des points où :
   - D/H et Y_p sont dans leurs fenêtres,
   - Li7/H et Li_total/H sont compatibles avec les observations,
   - et la géométrie de courbe reste cohérente avec V77G ?

3) Si non :
   - le jouet surestime-t-il la flexibilité du secteur A=7 ?
   - ou manque-t-il des degrés de liberté dans le code réel ?


6. TRANSITION
-------------
- Si V78H trouve une zone de paramètres réels où :
  - D/H, Y_p, Li7/H, Li_total/H sont tous compatibles,
  - et la géométrie de courbe ressemble à V77G,
  → V79X pourra interpréter physiquement ces paramètres (mécanismes concrets).

- Si V78H ne trouve aucune zone acceptable :
  → V79X devra discuter les limites du jouet,
    et/ou la rigidité réelle du secteur A=7 dans la BBN standard.

V78H est le premier protocole qui mélange :
- géométrie de courbe (V77G),
- code BBN réel,
- données observationnelles,
- et fichiers propres à télécharger pour analyse approfondie.


## Résultat V78H
La grille sourcée a été branchée et le validateur a produit des sorties exploitables.

Entrée utilisée :
- [data/v78h_real_bbn_reference.csv](data/v78h_real_bbn_reference.csv)

Résultat chiffré :
- verdict : `accepted_band_found`
- points acceptés : `1/20`
- meilleur point :
  - `beta_e_phys = 0.0`
  - `gamma_exch_phys = 0.0`
  - `gamma_drain_phys = 0.0`
  - `D/H = 2.527e-05`
  - `Y_p = 0.2436`
  - `Li7/H = 1.1e-10`
  - `Li_total/H = 1.1e-10`
  - `chi_D = 0.0`
  - `chi_Y = 0.0`
  - `chi_Li7 = 1.0`

Lecture qualitative produite par le script :
- courbe : `courbe plate à courbure mixte`
- surface : `surface acceptable mais étroite`
- comparaison avec V77G : `cohérente qualitativement avec V77G sur une tranche unique`

Sorties générées :
- [results/result-analyse/v78h_realdata_validation/v78h_results_full.csv](results/result-analyse/v78h_realdata_validation/v78h_results_full.csv)
- [results/result-analyse/v78h_realdata_validation/v78h_results_accepted.csv](results/result-analyse/v78h_realdata_validation/v78h_results_accepted.csv)
- [results/result-analyse/v78h_realdata_validation/V78H_REALDATA_SUMMARY.txt](results/result-analyse/v78h_realdata_validation/V78H_REALDATA_SUMMARY.txt)
- [results/result-analyse/v78h_realdata_validation/plots/v78h_Litot_vs_beta_e.png](results/result-analyse/v78h_realdata_validation/plots/v78h_Litot_vs_beta_e.png)
- [results/result-analyse/v78h_realdata_validation/plots/v78h_Litot_surface_gamma.png](results/result-analyse/v78h_realdata_validation/plots/v78h_Litot_surface_gamma.png)
- [results/result-analyse/v78h_realdata_validation/plots/v78h_DH_vs_param.png](results/result-analyse/v78h_realdata_validation/plots/v78h_DH_vs_param.png)

Phrase de synthèse :
- la validation sourcée trouve une tranche acceptable unique, mais étroite, avec un point accepté centré sur la référence observée; la géométrie reste cohérente avec V77G seulement de façon locale, sans bande large ni renversement robuste du secteur A=7.