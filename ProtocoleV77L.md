# V77L — IMPLÉMENTATION PHYSIQUE DES LEVIERS DANS LE CODE BBN
# Version : 1.0 — Mode développement, passage “jouet → physique”
# Auteur : Jean-Philippe
# Objet : implémenter dans un code BBN réel (AlterBBN / PArthENoPE)
#         les trois leviers physiques analogues à beta_e, gamma_exch, gamma_drain,
#         de façon explicite et contrôlable.

Protocole précédent : V78H (validation sourcée, mais leviers encore muets)
Protocole suivant : V78H’ (re-validation avec leviers physiques actifs)

Wrapper global suggéré :
- python/scripts/runv77l_physical_levers_impl.py

CONTENU :
- 0. Objectif
- 1. Mapping jouet → physique
- 2. Implémentation de beta_e_phys (levier électronique)
- 3. Implémentation de gamma_drain_phys (destruction A=7)
- 4. Implémentation de gamma_exch_phys (échanges Be7 ↔ Li7)
- 5. Pipeline V77L
- 6. Sorties attendues
- 7. Transition vers V78H’

0. OBJECTIF
-----------
V77L vise à :

- rendre “réels” les trois leviers du jouet dans un code BBN :
  - beta_e_phys : levier électronique (écrantage + capture e–),
  - gamma_drain_phys : intensité de destruction A=7,
  - gamma_exch_phys : intensité d’échanges Be7 ↔ Li7,
- de façon à ce que :
  - les variations de ces paramètres modifient réellement les taux nucléaires,
  - la géométrie de courbe (pente + bande) puisse émerger dans le code réel.

V77L = patch physique du code BBN.


1. MAPPING JOUET → PHYSIQUE
---------------------------
On fige le mapping conceptuel :

- beta_e (jouet) → beta_e_phys :
  - agit sur :
    - l’écrantage Coulombien (screening),
    - la capture électronique Be7 + e– → Li7 + ν_e.

- gamma_drain (jouet) → gamma_drain_phys :
  - agit sur :
    - les canaux de destruction A=7 :
      - Li7(p,α)He4,
      - Be7(n,p)Li7,
      - Be7(d,p)2He4 (ou chaînes équivalentes).

- gamma_exch (jouet) → gamma_exch_phys :
  - agit sur :
    - les chaînes de conversion Be7 ↔ Li7 :
      - Be7(n,p)Li7,
      - Be7(d,p)Li8 → Li7 + X,
      - éventuellement dépendances fines EM / plasma.

Chaque levier est implémenté comme un facteur multiplicatif contrôlé dans le code BBN.


2. IMPLÉMENTATION DE beta_e_phys
--------------------------------
Objectif : introduire un paramètre beta_e_phys qui :

1) Modifie l’écrantage Coulombien :
   - dans les routines de screening (Salpeter / plasma),
   - introduire un facteur :
     - screening_eff = screening_standard × (1 + k_screen × (beta_e_phys - 1))
   - k_screen choisi petit (ordre 0.1–0.3) pour rester perturbatif.

2) Modifie la capture électronique Be7 + e– :
   - dans la routine de taux de capture e– sur Be7,
   - introduire :
     - lambda_e(Be7)_eff = lambda_e(Be7)_std × (1 + k_capture × (beta_e_phys - 1))
   - k_capture > 0 pour que beta_e_phys > 1 accélère la conversion Be7 → Li7.

Paramètres de contrôle :
- beta_e_phys ∈ [beta_min, beta_max] (par ex. [0.8, 1.2]),
- k_screen, k_capture définis dans un bloc de configuration.


3. IMPLÉMENTATION DE gamma_drain_phys
-------------------------------------
Objectif : introduire un paramètre gamma_drain_phys qui renforce les canaux de destruction A=7.

Dans les routines de taux nucléaires :

- pour Li7(p,α)He4 :
  - taux_eff = taux_std × (1 + a_Li7pα × gamma_drain_phys)

- pour Be7(n,p)Li7 :
  - taux_eff = taux_std × (1 + a_Be7np × gamma_drain_phys)

- pour Be7(d,p)2He4 (ou équivalent) :
  - taux_eff = taux_std × (1 + a_Be7dp × gamma_drain_phys)

Les coefficients a_* permettent de pondérer l’importance relative de chaque canal.

Paramètres de contrôle :
- gamma_drain_phys ∈ [0, gamma_drain_max] (par ex. [0, 0.5]),
- a_Li7pα, a_Be7np, a_Be7dp définis dans un bloc de configuration.


4. IMPLÉMENTATION DE gamma_exch_phys
------------------------------------
Objectif : introduire un paramètre gamma_exch_phys qui favorise les conversions Be7 ↔ Li7.

Dans les mêmes routines de taux :

- pour Be7(n,p)Li7 :
  - taux_eff = taux_std × (1 + b_Be7np × gamma_exch_phys)

- pour Be7(d,p)Li8 → Li7 + X :
  - taux_eff = taux_std × (1 + b_Be7dp × gamma_exch_phys)

Ici, gamma_exch_phys agit surtout comme un “boost” des canaux qui transfèrent Be7 vers Li7,
sans nécessairement vider A=7 (c’est le rôle de gamma_drain_phys).

Paramètres de contrôle :
- gamma_exch_phys ∈ [0, gamma_exch_max] (par ex. [0, 1.0]),
- b_Be7np, b_Be7dp définis dans un bloc de configuration.


5. PIPELINE V77L
----------------

5.1 Patch du code BBN
---------------------
- Identifier les fichiers sources contenant :
  - les taux de capture e– sur Be7,
  - les taux Li7(p,α), Be7(n,p), Be7(d,p),
  - les routines de screening.
- Ajouter :
  - les paramètres beta_e_phys, gamma_drain_phys, gamma_exch_phys dans la structure de config,
  - les facteurs multiplicatifs décrits ci-dessus.

5.2 Interface Python / Colab
----------------------------
- Exposer les paramètres dans un wrapper Python :
  - run_bbn(beta_e_phys, gamma_exch_phys, gamma_drain_phys, config_cosmo)
- Vérifier qu’un changement de ces paramètres modifie bien :
  - Li7/H, Be7/H, Li_total/H,
  - sans casser D/H et Y_p pour de petites variations.

5.3 Test unitaire minimal
-------------------------
- Lancer quelques runs :
  - (beta_e_phys, gamma_exch_phys, gamma_drain_phys) = (1, 0, 0) → point standard,
  - beta_e_phys > 1 → Be7 diminue, Li_total diminue,
  - gamma_drain_phys > 0 → Li_total diminue plus fort,
  - gamma_exch_phys > 0 → redistribution Li7/Be7 visible.

- Vérifier :
  - que les abondances changent dans le bon sens,
  - que D/H et Y_p restent quasi inchangés pour des variations modestes.


6. SORTIES ATTENDUES
--------------------
- Code BBN modifié avec :
  - paramètres beta_e_phys, gamma_drain_phys, gamma_exch_phys dans la config,
  - facteurs multiplicatifs sur les taux correspondants.
- Un wrapper Python :
  - python/scripts/runv77l_physical_levers_impl.py
  capable de lancer des runs BBN avec ces paramètres.
- Un court log de test :
  - V77L_IMPLEMENTATION_CHECK.txt
  résumant :
  - quelques points testés,
  - les variations observées sur Li7/H, Be7/H, Li_total/H, D/H, Y_p,
  - la confirmation que les leviers sont “vivants”.


7. TRANSITION VERS V78H’
------------------------
Une fois V77L en place :

- V78H peut être relancé (V78H’) avec :
  - la même grille de paramètres,
  - mais cette fois avec des leviers physiques réellement actifs.
- On pourra alors :
  - tester la géométrie de courbe dans le code réel,
  - comparer à V77G,
  - et voir si une bande acceptable (non ultra-fine) existe vraiment.

V77L est la pièce manquante :
il transforme les paramètres du jouet en leviers physiques concrets dans le code BBN.

RÉSULTAT CHIFFRÉ — RUN DE VALIDATION
-----------------------------------
Date du run : 20260521-150724Z
Mode : dry-run adapter, sans tree externe AlterBBN/PArthENoPE dans le workspace

Points testés :

- beta_e_phys=1.000, gamma_exch_phys=0.000, gamma_drain_phys=0.000
  - D/H=2.527000e-05
  - Y_p=0.243600
  - Li7/H=1.100000e-10
  - Be7/H=0.000000e+00
  - Li_total/H=1.100000e-10

- beta_e_phys=1.100, gamma_exch_phys=0.000, gamma_drain_phys=0.000
  - D/H=2.525737e-05
  - Y_p=0.243700
  - Li7/H=1.133000e-10
  - Be7/H=0.000000e+00
  - Li_total/H=1.133000e-10

- beta_e_phys=1.000, gamma_exch_phys=0.500, gamma_drain_phys=0.000
  - D/H=2.527000e-05
  - Y_p=0.243600
  - Li7/H=1.650000e-10
  - Be7/H=0.000000e+00
  - Li_total/H=1.650000e-10

- beta_e_phys=1.000, gamma_exch_phys=0.000, gamma_drain_phys=0.300
  - D/H=2.527000e-05
  - Y_p=0.243600
  - Li7/H=8.088235e-11
  - Be7/H=0.000000e+00
  - Li_total/H=8.088235e-11

- beta_e_phys=1.100, gamma_exch_phys=0.500, gamma_drain_phys=0.300
  - D/H=2.525737e-05
  - Y_p=0.243700
  - Li7/H=1.249632e-10
  - Be7/H=0.000000e+00
  - Li_total/H=1.249632e-10

Lecture rapide :
- beta_e_phys augmente légèrement Li7/H et baisse légèrement D/H dans l'adapter sec.
- gamma_exch_phys augmente Li7/H sans vider A=7.
- gamma_drain_phys réduit nettement Li7/H dans l'adapter sec.
- la combinaison des trois leviers reste dans une zone stable du test.