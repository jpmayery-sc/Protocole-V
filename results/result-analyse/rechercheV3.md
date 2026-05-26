# Rapport V3 - Recherche vectorielle HF

## Objectif

Documenter la suite de tests V3 qui cherche une structure vectorielle stable dans les donnees HF, sans fit global unique.

## Synthese

| Test | Objet | Verdict |
| --- | --- | --- |
| TEST0 | Donnees et perimetre | supported |
| TEST1 | Construction de l espace invariant | supported |
| TEST2 | Geometrie inter-materiaux | supported |
| TEST3 | Leave-one-material-out | supported |
| TEST4 | Changement de regime | supported |
| TEST5 | Stabilite statistique | supported |
| TEST6 | Reduction scalaire optionnelle | supported |

Verdict global: supported

Le rapport machine de reference est [results/result-analyse/protocol_v3_vector_summary_20260512-142014Z.json](protocol_v3_vector_summary_20260512-142014Z.json).

## Contexte de travail

La suite V3 part du manifeste HF transport et des quatre materiaux de base Cu, Al, Ag et Fe.
Elle ne cherche pas a revalider un fit global, mais a verifier si une representation vectorielle simple reste geometriquement stable quand on change de materiau, de bande et de projection.

Le schema actuel utilise l espace invariant suivant:

- log10(A/A_ref_material)
- sigma/sigma_Cu

avec A = delta * sqrt(f).

## Resultats detailles

### TEST0 - Donnees et perimetre

Verdict: supported

Le manifeste expose bien les quatre materiaux requis et chaque serie contient cinq points.
Les bandes presentes sont bf_proxy, hf_classic et hf_advanced_proxy.
Le DC explicite reste absent, mais un ancrage basse frequence est disponible.

### TEST1 - Construction de l espace invariant

Verdict: supported

Chaque point est projete dans un espace vectoriel 2D fonde sur un rapport d amplitude invariant et sur la conductivite relative au cuivre.

Centroides materiels:

- Cu: [-0.00014803235388901665, 1.0]
- Al: [-5.605060566032808e-05, 0.6113475177304966]
- Ag: [-5.115207748554385e-05, 1.0842767295597484]
- Fe: [0.000195296374851966, 0.17754891864057673]

### TEST2 - Geometrie inter-materiaux

Verdict: supported

La geometrie vectorielle separe beaucoup mieux les materiaux que l espace brut.

Chiffres clefs:

- Separation ratio brut: 15.712479203340548
- Separation ratio vectoriel: 244.3700844615297
- PCA top2 expliquee: 1.0

Voisins les plus proches:

- Cu -> Ag
- Al -> Cu
- Ag -> Cu
- Fe -> Al

### TEST3 - Leave-one-material-out

Verdict: supported

Quand on retire un materiau, la structure geometrique reconstruite conserve le meme voisin le plus proche et le meme ordre local.

Folds:

- Held out Cu: voisin projetee Ag, ordre conserve, displacement 0.3756089865812533
- Held out Al: voisin projetee Cu, ordre conserve, displacement 0.14259437551550883
- Held out Ag: voisin projetee Cu, ordre conserve, displacement 0.4879779198188274
- Held out Fe: voisin projetee Al, ordre conserve, displacement 0.7209925516379556

### TEST4 - Changement de regime

Verdict: supported

La geometrie relative reste stable sur les trois bandes observees.
Les voisins les plus proches restent identiques sur bf_proxy, hf_classic et hf_advanced_proxy, et le deplacement moyen inter-bandes reste tres faible.

Chiffres clefs:

- band_mean_shift: 0.00013619727403195073
- band_max_shift: 0.00029576767267756437
- band_pca_top2: 1.0 sur chaque bande

### TEST5 - Stabilite statistique

Verdict: supported

Le passage au vecteur invariant garde une dispersion inter-materiaux comparable au brut, sans rupture de stabilite.

Chiffres clefs:

- raw_pairwise_cv: 0.533089750427372
- vector_pairwise_cv: 0.5330897121130956
- improvement_ratio: 0.9999999281279066
- leave_one_out_pairwise_cv: [0.354539689507365, 0.6111786625442106, 0.35514775570368573, 0.5294631440198087]

### TEST6 - Reduction scalaire optionnelle

Verdict: supported

Le premier axe principal preserve la stabilite de la geometrie vectorielle.
La reduction scalaire ne degrade pas le comportement observe sur le vecteur.

Chiffres clefs:

- scalar_pairwise_cv: 0.5330897817729272
- vector_pairwise_cv: 0.5330897121130956

## Lecture physique

Le resultat principal n est pas un fit meilleur, mais une geometry plus lisible et plus stable.
Le noyau invariant obtenu est nettement plus separatif que l espace brut, reste robuste au leave-one-out, et ne change pas de structure visible entre les bandes disponibles.

La consequence pratique est simple:

- on peut garder l espace vectoriel comme representation de travail;
- on ne depend pas d un fit global unique;
- la reduction scalaire est acceptable comme option, mais elle n apporte pas de gain supplementaire sur la stabilite.

## Points de vigilance

- Le jeu de donnees reste petit: quatre materiaux seulement.
- Le point DC explicite n est pas disponible, donc le bas de bande reste un proxy.
- Un warning Matplotlib a encore ete emis a l export du plot PCA, sans bloquer la generation des resultats.

## Fichiers de reference

- [Script V3](../../python/scripts/run_protocol_v3_suite.py)
- [Resume machine V3](protocol_v3_vector_summary_20260512-142014Z.json)
- [Rapport V3 existant](protocole_v3_vectoriel.md)

## Conclusion

La suite V3 est concluante: 7/7 tests sont supportes.
Le protocole vectoriel est donc valide comme representation de recherche pour cette phase du travail.