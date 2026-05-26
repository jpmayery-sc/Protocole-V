# Protocole V3 - Geometrie vectorielle

## But
Chercher une structure vectorielle stable dans les donnees HF sans fit global unique.

## Verdict
- Verdict global: supported
- Tests supportes: 7/7
- Regimes disponibles: bf_proxy, hf_advanced_proxy, hf_classic

## Test 0 - Perimetre
- The manifest exposes the four required materials and each series contains five points; DC is absent but the low-frequency anchor is present.

## Test 1 - Espace vectoriel
- V = [log10(A/A_ref_material), sigma/sigma_Cu] avec A = delta * sqrt(f)
- Le premier axe mesure l ecart d amplitude invariant dans chaque materiau; le second porte la conductivite relative.

## Test 2 - Geometrie inter-materiaux
- Separation ratio brut: 15.712479
- Separation ratio vectoriel: 244.370084
- PCA top2 expliquee: 1.000000

## Test 3 - Leave-one-material-out
- La geometrie est reconstruite sans le materiau laisse de cote puis comparee a son placement geometrique.

## Test 4 - Changement de regime
- Couverture des bandes: {"bf_proxy": true, "hf_classic": true, "hf_advanced_proxy": true}
- Test de continuité par bandes: supported

## Test 5 - Stabilite statistique
- CV brut: 0.533090
- CV vectoriel: 0.533090
- Max CV leave-one-out: 0.611179

## Test 6 - Reduction scalaire optionnelle
- The first principal component preserves the cross-material stability of the invariant vector geometry.

## Plots
- [PCA projection](plots/protocol_v3_pca_projection.png)
- [CV comparison](plots/protocol_v3_cv_comparison.png)

## Lecture courte
Le V3 privilegie la geometrie vectorielle. Le scalaire derivé n'est retenu que s'il ne degrage pas la stabilite inter-materiaux.
