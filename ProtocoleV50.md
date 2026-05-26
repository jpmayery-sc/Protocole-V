# V50 — INTRICATION
# Détection du mécanisme d’intrication manquant via le scan γ → fσ₈(z)
Version : 0.1

Protocole précédent : ProtocoleV49.md
Protocole suivant : ProtocoleV51.md

Wrapper global suggéré :
- python/scripts/runv50intrication_suite.py

Modules :

- V50-SCAN        - Balayage du paramètre γ et calcul de fσ₈(z)
- V50-FIT         - Détermination du point optimal γ*
- V50-RESIDU      - Détection du résidu inexpliqué
- V50-FORME       - Analyse géométrique au point γ*
- V50-ROBUSTNESS   - Validation renforcée du résultat
- V50-INTRICATION - Extraction du terme manquant
- V50-SYNTHESIS   - Verdict global


0. OBJECTIF
-----------
Détecter la structure d’intrication manquante dans le modèle K/T/Y + D1/D2 en :

- scannant le paramètre γ du potentiel V_Y(Y)
- identifiant la valeur γ* qui colle le mieux aux données fσ₈(z)
- mesurant le résidu inexpliqué
- analysant la forme géométrique imposée par γ*
- en déduisant le terme d’intrication V_ent nécessaire pour tomber juste

Ce protocole ne cherche pas à ajuster γ.
Il cherche à révéler la forme manquante.


1. V50-SCAN — BALAYAGE DU PARAMÈTRE γ
--------------------------------------
On fait varier γ dans un intervalle large mais physique :

    γ ∈ [0.1, 5.0]

Pour chaque γ :
- on résout Y(z)
- on calcule fσ₈(z)
- on compare aux données DESI + KiDS + Planck
- on calcule l’erreur quadratique :

    χ²(γ) = Σ_z [ (fσ₈_mod(z) – fσ₈_obs(z))² / σ(z)² ]

Sorties :
- gamma_values
- chi2_values
- fs8_curves
- scan_summary


2. V50-FIT — DÉTERMINATION DU POINT OPTIMAL γ*
----------------------------------------------
On identifie :

    γ* = argmin_γ χ²(γ)

Sorties :
- gamma_star
- chi2_min
- fs8_best_fit
- fit_summary


3. V50-RESIDU — DÉTECTION DU RÉSIDU INEXPLIQUÉ
----------------------------------------------
Même au point optimal γ*, on calcule :

    R(z) = fσ₈_mod(z; γ*) – fσ₈_obs(z)

On analyse :
- la forme de R(z)
- sa dépendance en z
- sa corrélation avec Y(z)
- sa corrélation avec dY/dz
- sa corrélation avec K, T

Sorties :
- residual_curve
- residual_norm
- residual_pattern
- residual_summary


4. V50-FORME — ANALYSE GÉOMÉTRIQUE AU POINT γ*
----------------------------------------------
On étudie la forme du potentiel :

    V_Y(Y) = (γ*/2) (Y – Y∞)²

On regarde :
- la courbure
- la convexité
- la stabilité
- la relation entre Y(z) et fσ₈(z)
- la relation entre Y(z) et le résidu R(z)

Sorties :
- VY_shape
- curvature
- Y_profile
- Y_correlation
- form_summary


5. V50-ROBUSTNESS — VALIDATION RENFORCÉE
----------------------------------------
On impose des contrôles plus stricts que le simple meilleur ajustement :

5.1 Cohérence du minimum
- γ* doit rester stable entre un balayage grossier et un balayage raffiné
- écart autorisé : |γ*_coarse - γ*_refined| ≤ 0.1

5.2 Stabilité par sous-échantillonnage
- le signe global du résidu doit rester cohérent sur les sous-ensembles en z
- la structure du résidu doit survivre à une re-pondération raisonnable des points

5.3 Robustesse du terme d’intrication
- la forme torsionnelle doit rester la meilleure après pénalisation des formes non locales
- la hiérarchie des candidats ne doit pas dépendre d’un seul point de données

5.4 Géométrie locale
- la forme V_Y(Y) doit rester convexe au voisinage de γ*
- la courbure doit rester positive sur la plage physique testée

Sorties :
- robustness_checks
- robustness_pass
- robustness_summary


6. V50-INTRICATION — EXTRACTION DU TERME MANQUANT
--------------------------------------------------
On cherche un terme V_ent tel que :

    fσ₈_mod(z; γ*, V_ent) = fσ₈_obs(z)

On teste des formes candidates :

6.1 Intrication géométrique :
    V_ent^(1) = χ₁ K Y

6.2 Intrication torsionnelle :
    V_ent^(2) = χ₂ T (dY/dz)

6.3 Intrication non locale :
    V_ent^(3) = χ₃ ∫ dz' G(z,z') Y(z')

6.4 Intrication multi-échelle (D1/D2) :
    V_ent^(4) = χ₄ Y_D1 Y_D2

Sorties :
- entanglement_candidates
- entanglement_best_form
- entanglement_summary


7. V50-SYNTHESIS — VERDICT GLOBAL
----------------------------------
Sorties attendues :
- gamma_star
- residual_pattern
- entanglement_best_form
- v50_global_verdict


8. CRITÈRES DE VERDICT
----------------------

supported :
- γ* bien défini sur l’intervalle de scan
- χ²_min significatif et stable
- résidu non nul mais structuré
- courbure positive au voisinage de γ*
- robustesse validée sur les sous-échantillons

intrication_required :
- le meilleur ajustement laisse un résidu dynamique
- la forme torsionnelle domine les candidats
- le terme V_ent est nécessaire pour expliquer la structure restante

rejected :
- minimum instable
- résidu incohérent
- absence de structure géométrique exploitable
- candidat d’intrication non discriminable


9. RÉSULTATS OBSERVÉS (RUN RÉEL)
---------------------------------

Suite exécutée : v50intrication_suite
Horodatage : 20260520-100909Z

Chiffres globaux :
- v50_global_verdict : intrication_required
- supported_count : 5/7
- intrication_required_count : 2/7
- total : 7

Points saillants :
- γ* = 1.73
- χ²_min = 1.12
- résidu R(z) ≠ 0 → structure non expliquée
- R(z) corrélé à dY/dz
- V_Y(Y) convexe autour du point optimal
- robustesse validée sur le balayage et la hiérarchie des candidats
- V_total partiel reste cohérent mais insuffisant sans V_ent
- meilleure forme d’intrication :

      V_ent = χ₂ T (dY/dz)

Fichiers de sortie générés :
- JSON : results/result-analyse/v50_intrication/v50intrication_suite_summary_20260520-100909Z.json
- TXT : results/result-analyse/v50_intrication/v50intrication_suite_summary_20260520-100909Z.txt

Items validés :
- v50_scan : supported
- v50_fit : supported
- v50_residu : supported
- v50_forme : supported
- v50_robustness : supported
- v50_intrication : intrication_required
- v50_synthesis : intrication_required

Interprétation :
- le modèle sans intrication est cohérent mais jamais exact
- le résidu a une forme dynamique, pas statique
- la meilleure correction est un terme d’intrication torsionnelle
- ce terme relie T (torsion interne) et la dynamique de Y
- cohérent avec l’expérience Rydberg 2026 (interaction émergente dépendant de la corrélation dynamique)

Verdict :
- v50_global_verdict : intrication_required
- forme manquante identifiée :

      V_ent = χ₂ T (dY/dz)
