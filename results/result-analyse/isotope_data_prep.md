# Preparation des donnees isotopiques

## But

Preparer une base de travail minimale, traçable et non retrofitee pour alimenter la branche isotopique S(A) / delta S(A).

## Priorite des sources

1. NIST Atomic Spectra Database (ASD), version la plus recente disponible.
2. NNDC / NuDat / ENSDF pour les masses isotopiques et les rayons de charge nucleaires lorsque la geometrie noyau-isotope doit etre ancres.
3. Articles primaires de spectroscopie optique de precision avec isotope shifts explicites.
4. Revues de synthese uniquement pour retrouver les publications, pas pour fixer les valeurs finales.

## Ce qu il faut extraire

Pour chaque mesure, garder au minimum:

- element,
- isotope reference A0,
- isotope compare A,
- transition spectroscopique,
- shift observe delta nu,
- incertitude,
- type de mesure (directe, King plot, modified King plot, autre),
- identifiant de niveau ou de transition si disponible,
- source primaire,
- DOI ou lien resolvable,
- commentaire sur le statut (direct / infere / mixte).

Pour l'ancrage nuclear-geometrique, garder aussi si disponible:

- masse isotopique,
- rayon de charge nucleaire,
- reference NNDC ou base equivalente,
- methode / convention utilisee pour le rayon.

## Regles de selection

- garder seulement les shifts isotope-resolus mesures,
- privilegier les familles avec plusieurs isotopes publies dans une meme experience,
- separer clairement les valeurs directes des valeurs reconstruites,
- enregistrer la reference isotope utilisee pour chaque serie,
- conserver les incertitudes et la methode d extraction,
- ne pas combler les trous par une interpolation theorique.

## Cibles prioritaires

### Candidats atomiques a fort signal

- Ca+,
- Sr+,
- Yb+,
- Ba+.

### Candidats neutres utiles pour contraste

- Sr,
- Yb,
- Ca,
- Ba.

## Format de travail recommande

Un tableau CSV ou JSON normalise avec les champs suivants:

- source_id,
- element,
- isotope_A,
- isotope_A0,
- transition,
- delta_nu_hz,
- uncertainty_hz,
- measurement_mode,
- level_info,
- nuclear_charge_radius_fm,
- isotopic_mass_u,
- nuclear_source,
- reference,
- doi,
- notes.

## Controle qualite

Le jeu de donnees est acceptable si:

- le meme isotope de reference est explicite,
- les unites sont homogenes,
- les shifts sont mesures et non inferees,
- la methode de traitement est documentee,
- les points douteux sont marques plutot que nettoyes silencieusement.

## Ce qui est refuse

- moyennes isotopiques sans detail par paire,
- valeurs reconstituees a partir d une pente supposee,
- donnees sans reference primaire,
- tableaux ou graphiques sans valeur numerique recuperable,
- series dont la methode d extraction n est pas reproductible.

## Premier lot a constituer

1. Une table de transition pour chaque element cible.
2. Une table de paires isotopiques avec delta nu et incertitude.
3. Une table de meta-donnees source.
4. Un petit jeu de validation croisee entre NIST ASD et les articles primaires.

## Etat attendu

Cette preparation ne produit pas encore de verdict physique. Elle fixe seulement le format d entree, le niveau de preuve attendu et les criteres de nettoyage autorises avant de lancer la branche isotopique.