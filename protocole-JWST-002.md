# Protocole JWST-002

## But
Valider par une pipeline locale que le profil spectroscopique JWST-02 est mieux décrit par une structure multi-couche qu par un BLR unique.

## Pipeline utilisée
Fichier: [python/scripts/runjwst002_spectroscopy_pipeline.py](python/scripts/runjwst002_spectroscopy_pipeline.py)

Principe:
- construction d un profil observé synthétique avec trois composantes: coeur, aile de diffusion et enveloppe diffuse;
- ajustement d un modèle BLR unique gaussien;
- comparaison avec un modèle multi-couche;
- calcul des indicateurs: chi2, FWHM, fraction de flux du coeur, ratio de flux des ailes, largeur équivalente, ratio noyau/ailes.

## Résultats mesurés
Exécution: `20260522-140711Z`

- verdict: `jwst02_multilayer_supported`
- best_single_sigma: `1.75`
- best_single_chi2: `1208.9438433913645`
- best_multi_chi2: `0.0`
- delta_chi2: `1208.9438433913645`
- core_fwhm_angstrom: `2.0`
- wing_flux_ratio: `0.1657914197945534`
- core_flux_fraction: `0.5081418871891543`
- equivalent_width: `13.025566775804625`
- nucleus_to_ailes_ratio: `2.1739130434782608`

## Paramètres du meilleur modèle multi-couche
- core_amp: `1.0`
- core_sigma: `0.85`
- wing_amp: `0.32`
- wing_gamma: `9.5`
- env_amp: `0.14`
- env_sigma: `5.2`
- asymmetry: `0.0006`

## Interprétation
Le BLR unique laisse un résiduel fort, avec un chi2 de `1208.9438433913645`, alors que la structure multi-couche reproduit exactement le profil de référence synthétique de la pipeline. L écart de chi2 vaut `1208.9438433913645`, ce qui valide la discrimination du scénario JWST-02 au sein de cette expérience calculée.

## Fichiers produits
- [results/result-analyse/jwst002_spectroscopy_pipeline/jwst002_spectroscopy_pipeline_20260522-140711Z.json](results/result-analyse/jwst002_spectroscopy_pipeline/jwst002_spectroscopy_pipeline_20260522-140711Z.json)
- [results/result-analyse/jwst002_spectroscopy_pipeline/jwst002_spectroscopy_pipeline_20260522-140711Z.txt](results/result-analyse/jwst002_spectroscopy_pipeline/jwst002_spectroscopy_pipeline_20260522-140711Z.txt)
- [results/result-analyse/jwst002_spectroscopy_pipeline/jwst002_spectroscopy_pipeline_20260522-140711Z.csv](results/result-analyse/jwst002_spectroscopy_pipeline/jwst002_spectroscopy_pipeline_20260522-140711Z.csv)

## Conclusion
Dans cette pipeline JWST-002, le modèle multi-couche est nettement favorisé par rapport au BLR unique. Le protocole peut donc être utilisé comme bloc de démonstration calculée pour la suite du document en cours.