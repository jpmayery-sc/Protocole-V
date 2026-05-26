# Rapport V4 - Interpretation physique de l'espace invariant HF

## Finalite de V4

V4 ne cherche pas un meilleur modele.
V4 cherche ce que represente physiquement l espace invariant V3.

Autrement dit, V3 a montre qu il existe une structure stable.
V4 cherche quelle physique minimale cette structure encode.

Aucune loi universelle n est attendue a ce stade.

## Hypothese centrale

L invariant vectoriel HF correspond a une decomposition naturelle du transport en contributions physiques distinctes, et non a un parametre global effectif.

En pratique:

- chaque axe correspond a un mecanisme dominant;
- la stabilite observee indique que ces mecanismes se combinent lineairement au premier ordre dans cet espace, mais pas forcement de facon orthogonale au sens fort.

## Definition de depart, inchangee depuis V3

On repart exactement de l espace V3:

- V1 = log10(A / A_ref)
- V2 = sigma / sigma_Cu
- A = delta * sqrt(f)

Aucune nouvelle transformation n est introduite.

## Sources utilisees

- [Rapport V3](rechercheV3.md)
- [Protocole V3 vectoriel](protocole_v3_vectoriel.md)
- [Suite V3 machine](protocol_v3_vector_summary_20260512-142014Z.json)
- Donnees HF normalisees Cu, Al, Ag, Fe dans le manifeste transport

## Resume numerique V3 utile a V4

- Centroides materiels V3:
  - Cu: [-0.00014803235388901665, 1.0]
  - Al: [-5.605060566032808e-05, 0.6113475177304966]
  - Ag: [-5.115207748554385e-05, 1.0842767295597484]
  - Fe: [0.000195296374851966, 0.17754891864057673]
- Voisins les plus proches en V3:
  - Cu -> Ag
  - Al -> Cu
  - Ag -> Cu
  - Fe -> Al
- Separation ratio brut: 15.712479203340548
- Separation ratio vectoriel: 244.3700844615297
- PCA top2 expliquee: 1.0

## Methode de lecture V4

Les tests V4 restent descriptifs et ne definissent aucun nouvel espace.
Ils cherchent seulement a qualifier le couplage residuel entre V1 et V2 a partir des trajectoires HF deja observees.

Les diagnostics retenus sont:

- normalisation conditionnelle de V1;
- pente locale dV1/df;
- recherche de plateau en HF avancee;
- projection minimale en V1 seul.

## TEST V4-1 - Interpretation dimensionnelle

Verdict: supported

Mesures et lecture:

- A = delta * sqrt(f) reste un rapport d echelle de type longueur HF;
- V1 = log10(A / A_ref) devient un indicateur sans dimension de longueur d activation HF;
- V2 = sigma / sigma_Cu reste un facteur de portance conductrice relatif.

Hypothese physique retenue:

- V1 code une activation geometrique HF;
- V2 code une contrainte de portance electronique.

Conclusion locale:

- V1 reste compatible avec une longueur caracteristique de transport HF;
- V2 reste compatible avec une capacite conductive materielle.

## TEST V4-2 - Decorrelation causale des axes

Verdict: contradicted

Mesures calculées sur les donnees V3 reconstruites sans nouvelle transformation:

- correlation globale sur tous les points: -0.3518146474928859
- correlation des centroides materiels: -0.8734438046856208
- correlation par bande:
  - bf_proxy: -0.463304645136301
  - hf_classic: -0.20200791587494726
  - hf_advanced_proxy: -0.6658830393850861

Lecture:

- V1 et V2 se separent fonctionnellement;
- mais ils gardent un couplage residuel statistique;
- ce couplage n est pas compatible avec une decorrelation causale stricte.

Conclusion locale:

- V4 echoue a prouver une independance forte des axes;
- il soutient seulement une separation fonctionnelle, pas une orthogonalite statistique complete.

## TEST V4-3 - Lecture par regimes physiques

Verdict: supported, avec reserve sur l orientation fine

Observation par materiau:

- Cu: V1 varie tres peu, V2 reste constant a 1.0
- Al: V1 varie tres peu, V2 reste constant a 0.6113475177304966
- Ag: V1 varie tres peu, V2 reste constant a 1.0842767295597484
- Fe: V1 varie tres peu, V2 reste constant a 0.17754891864057673

Lecture:

- les trajectoires sont continues et quasi horizontales dans l espace V3;
- V1 suit une saturation geometrique lente;
- V2 reste fixe a l interieur d une serie donnee et joue le role de fond materiel.

Comparaison regime par regime:

- Cu et Ag restent dans la zone haute de V2;
- Al et Fe occupent la zone basse de V2;
- Fe s ecarte le plus fortement de Cu et Ag, ce qui renforce l idee d une lecture regime dependante.

## TEST V4-4 - Causalite minimale

Verdict: supported

Sur chaque materiau, l evolution frequentielle fait bouger V1 point par point, tandis que V2 ne bouge pas.

Autrement dit:

- le premier mecanisme visible est l activation geometrique HF;
- la portance conductrice agit comme contrainte materielle fixe dans la serie.

Conclusion locale:

- l ordre causal minimal stable est: geometrie HF, puis capacite conductrice comme fond materiel.

## TEST V4-5 - Projection physique controlee

Verdict: supported

Lecture qualitative proposee:

- V1 = confinement geometrique HF
- V2 = portance electronique

Compatibilite observee:

- Cu et Ag restent compatibles avec une meme zone haute de portance electronique;
- Al et Fe restent compatibles avec une meme zone basse de portance electronique;
- aucune contradiction majeure ne force un changement de lecture.

Point nuance:

- Al et Fe ne sont pas des doublons; ils partagent seulement une famille de comportement sur V2, pas une position identique.

## Synthese physique detaillee

Le resultat V4 ne dit pas que V3 cache une loi universelle.
Il dit quelque chose de plus modeste et plus solide:

- l invariant V3 encode bien un espace physique a deux composantes;
- la premiere composante decrit une activation geometrique HF;
- la seconde decrit une capacite conductrice materielle;
- ces deux composantes sont separables, mais pas orthogonales au sens statistique fort sur le petit jeu de donnees disponible.

En termes physiques simples:

- oui, V3 ressemble a un espace (geometrie HF, capacite conductive);
- non, on ne peut pas encore pretendre que ces deux axes sont totalement independants.

## Verdict global

V4 est partiellement soutenu.

Ce qui survit aux tests:

- l interpretation minimale de V1 comme axe d activation geometrique HF;
- l interpretation minimale de V2 comme axe de capacite conductrice;
- la stabilite des trajectoires et leur compatibilite avec une lecture regime par regime.

Ce qui ne survit pas pleinement:

- l hypothese d une decorrelation causale forte entre les deux axes.

## Conclusion finale

L invariant V3 encode clairement un espace physique minimal: geometrie HF d un cote, capacite conductive de l autre.

Mais cet espace n est pas encore prouve comme orthogonal au sens fort; il reste un couplage residuel entre les deux axes.

La bonne lecture de V4 est donc:

- interpretation physique oui;
- independance stricte non.
