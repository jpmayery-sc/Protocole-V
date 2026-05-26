# V22 sources

## Objectif

Ce fichier sert de dossier de collecte avant les tests V22. Il liste les sources reelles a consulter, les donnees a extraire, et le role de chaque source dans les trois branches V22-THEORY, V22-EXPERIMENT et V22-SIMULATION.

## Branches V22

- V22-THEORY: formalisation theorique de la structure emergente.
- V22-EXPERIMENT: confrontation aux donnees reelles.
- V22-SIMULATION: extension numerique et hierarchique.

## Matrice de collecte

| Axe | Source | Donnees a extraire | Priorite |
|---|---|---|---|
| Theorie | [NIST Constants](https://physics.nist.gov/cuu/Constants/) | valeur de alpha, incertitude, valeurs CODATA 2022, correlations, bibliographie | Haute |
| Theorie | [NIST Links to selected scientific data](https://physics.nist.gov/cuu/Constants/links.html) | renvois vers donnees de reference utiles a alpha et aux constantes | Haute |
| Theorie | [NIST DLMF Chapter 34](https://dlmf.nist.gov/34) | proprietes des symboles 3j, 6j, 9j, symetries, regles de triangle | Haute |
| Theorie | [NIST DLMF Section 34.2](https://dlmf.nist.gov/34.2) | definition formelle du symbole 3j et conditions de selection | Haute |
| Theorie | [arXiv hep-th/0103093](https://arxiv.org/abs/hep-th/0103093) | revue de torsion espace-temps, bornes experimentales, cadre Einstein-Cartan | Haute |
| Experiment | [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database) | lignes spectrales, niveaux d'energie, probabilites de transition, energies d'ionisation | Haute |
| Experiment | [NIST Atomic Spectra Database Contents](https://www.nist.gov/pml/atomic-spectra-database-contents) | structure de la base, holdings, types de donnees disponibles, incertitudes | Haute |
| Experiment | [NASA/IPAC Extragalactic Database](https://ned.ipac.caltech.edu/) | redshifts de galaxies/quasars, objets a haut redshift, sources spectroscopiques | Haute |
| Experiment | [SDSS DR17](https://www.sdss4.org/dr17/) | catalogues spectroscopiques, redshifts, classifications, VACs, spectra optiques | Haute |
| Experiment | [ESA XMM-Newton](https://www.cosmos.esa.int/web/xmm-newton) | spectres X-ray, campagnes observationnelles, objets astrophysiques complementaires | Moyenne |
| Simulation | [NIST DLMF Chapter 34](https://dlmf.nist.gov/34) | formules Wigner, couplages angulaires, conditions de selection pour matrices de couplage | Haute |
| Simulation | [NIST DLMF Section 34.2](https://dlmf.nist.gov/34.2) | contraintes des symboles 3j pour la structure interne simulee | Haute |
| Simulation | [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database) | jeux de lignes et niveaux pour parametrer les modeles internes | Moyenne |
| Simulation | [SDSS DR17](https://www.sdss4.org/dr17/) | spectres et catalogues pour tester robustesse et classification | Moyenne |

## Champs a preparer pour chaque jeu de donnees

Pour chaque source, recuperer ou construire les champs suivants:

- source
- branche V22
- domaine physique
- observable principal
- valeur ou intervalle
- unite
- incertitude
- date de version ou de release
- lien bibliographique
- role dans V22

## Tables de travail attendues

### Constantes fondamentales

- alpha
- incertitude sur alpha
- correlation avec autres constantes utiles

### Spectroscopie

- longueurs d'onde
- niveaux d'energie
- probabilites de transition
- redshifts mesurables
- deltas nu / nu
- deltas E

### Astrophysique

- redshifts de quasars
- redshifts de galaxies proches
- classifications spectrales
- objets a haut redshift

### Torsion

- bornes experimentales
- couplages spin-torsion
- renvois vers les modeles Einstein-Cartan

### Simulation

- symboles Wigner
- representations SU(2) et SU(3)
- matrices de couplage
- parametres de stabilite

## Ordre recommande de collecte

1. NIST Constants
2. NIST ASD et contenu de la base
3. DLMF 34 / 34.2
4. arXiv hep-th/0103093
5. NED
6. SDSS DR17
7. XMM-Newton

## Etat de consolidation

- Theorie: consolidee et validee par `v22theory_suite`
- Experiment: consolidee et validee par `v22experiment_suite`
- Simulation: consolidee et validee par `v22simulation_suite`
- Tests V22: passes pour les trois branches, puis integres au master `point_atome`

## Sources deja exploitees

- [NIST Constants](https://physics.nist.gov/cuu/Constants/) pour alpha, les valeurs CODATA 2022 et la bibliographie associee.
- [NIST Atomic Spectra Database](https://www.nist.gov/pml/atomic-spectra-database) pour les lignes spectrales, les niveaux d'energie et les grandeurs spectroscopiques.
- [NIST Atomic Spectra Database Contents](https://www.nist.gov/pml/atomic-spectra-database-contents) pour la structure et les holdings de la base.
- [NIST Links to selected scientific data](https://physics.nist.gov/cuu/Constants/links.html) pour les renvois de reference autour des constantes fondamentales.
- [NIST DLMF Chapter 34](https://dlmf.nist.gov/34) et [Section 34.2](https://dlmf.nist.gov/34.2) pour les symboles de Wigner et les regles de couplage.
- [NASA/IPAC Extragalactic Database](https://ned.ipac.caltech.edu/) pour les redshifts astrophysiques.
- [SDSS DR17](https://www.sdss4.org/dr17/) pour les catalogues spectroscopiques et les classifications.
- [ESA XMM-Newton](https://www.cosmos.esa.int/web/xmm-newton) pour les observations X-ray complementaires.
- [arXiv hep-th/0103093](https://arxiv.org/abs/hep-th/0103093) pour le cadre torsion espace-temps et les bornes experimentales.

## Prochaine action

Le dossier est maintenant aligne avec le protocole. Si une nouvelle source doit etre ajoutee, elle peut etre integree dans la matrice ci-dessus sans modifier la structure V22.

La suite globale reste `v22research_suite`.