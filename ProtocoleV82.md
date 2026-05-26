# V82 — COMPARAISON AU RÉEL ET EXTENSION GRAVITÉ / TEMPS / NS

## Objectif
Prendre le Lagrangien minimal de V81 comme acquis et le confronter à des données réelles ou à des fenêtres expérimentales représentatives pour vérifier qu'une même bande de $\varepsilon$ reste acceptable.

V82 doit tester simultanément :
- la BBN,
- les contraintes de laboratoire sur les constantes fondamentales,
- la gravité locale et système solaire,
- les observables d'étoiles à neutrons.

## Ancrage V80 et V81
V82 conserve l'ancrage numérique suivant :
- $\delta_{EM} \in [-0.008, -0.0059]$
- centre indicatif : $\delta_{EM} \approx -0.00695$
- meilleur ajustement proxy : $\delta_{EM} \approx -0.0068$

Le Lagrangien V81 reste la base de travail :
- $\delta_{EM}(\varepsilon) = k_{EM} \varepsilon$
- $\pi_n(\varepsilon) = k_n \varepsilon \rho_n / \rho_n^{NS}$
- $G_{eff}(\varepsilon) = G (1 + k_G \varepsilon \pi_n)$
- $F_{temps}(\varepsilon) = 1 / (1 + k_T \varepsilon \pi_n)$

## Fenêtres de comparaison utilisées en V82
Les valeurs ci-dessous sont utilisées comme fenêtres de travail et non comme dérivation fondamentale :

1. BBN
- bande V80 sur $\delta_{EM}$

2. Laboratoire / EM
- clocks atomiques et comparaisons de fréquences à l'échelle $10^{-16}$ à $10^{-18}$ comme ordre de grandeur de référence
- l'observable de laboratoire est supposée fortement suppressée par le milieu, donc proportionnelle à $\pi_n \ll 1$

3. Gravité locale
- $G$ codata : $6.67430(15) \times 10^{-11}$ SI
- incertitude relative de référence : $2.2 \times 10^{-5}$
- variation locale admissible : de l'ordre de cette fenêtre ou plus petite

4. Étoiles à neutrons
- masses observées proches ou au-dessus de $2\,M_\odot$
- borne de travail pour les masses maximales : $M_{max} \gtrsim 2\,M_\odot$
- rayon de référence pour une étoile de $1.4\,M_\odot$ : ordre de $10$ à $14$ km
- redshift effectif de travail : ordre $0.1$ à $0.5$

## Pipeline V82
Pour chaque $\varepsilon$ :
- calculer $\delta_{EM}(\varepsilon)$,
- calculer $\pi_n$ en milieu laboratoire et en milieu neutronique,
- calculer $G_{eff}$ en labo et en régime neutronique,
- calculer un facteur de temps effectif $F_{temps}$ en régime neutronique,
- construire des proxys pour $M_{max}$, le rayon à $1.4\,M_\odot$ et un redshift effectif,
- vérifier la compatibilité de chaque classe de données,
- produire un score global ou un $\chi^2$ phénoménologique.

## Critères d'acceptation
Une valeur de $\varepsilon$ est retenue si :
- la contrainte BBN est respectée,
- la variation EM de laboratoire reste sous la fenêtre expérimentale retenue,
- $G_{eff}$ reste compatible avec la gravité locale lorsque $\pi_n \approx 0$,
- le régime neutronique produit une étoile à neutrons stable et compacte,
- les proxys $M_{max}$, rayon et redshift restent dans des ordres de grandeur observés.

## Résultat attendu
V82 doit fournir :
- une bande $\varepsilon$ compatible avec plusieurs classes de données,
- les valeurs associées de $\delta_{EM}$, $G_{eff}$ et $F_{temps}$,
- les tensions résiduelles si une classe de données contraint plus fortement que les autres.

## Résultat V82
Le scan global valide une bande commune :
- verdict : `global_band_confirmed`
- points acceptés : `14/51`
- bande $\varepsilon$ acceptée : $[-0.0076, -0.0063]$
- valeur centrale : $\varepsilon_c = -0.00695$
- meilleur ajustement : $\varepsilon_{best} = -0.0069$

Chiffres au meilleur ajustement :
- $\delta_{EM} = -0.0069$
- $\pi_n^{NS} = 0.9928057554$
- $G_{eff}^{NS} = 1.0548028777\,G$
- $F_{temps}^{NS} = 0.9605205330$
- $M_{max}^{NS} = 2.3880364666\,M_\odot$
- $R_{1.4}^{NS} = 11.3951098005$ km
- $z_{NS} = 0.2504117090$
- décalage EM laboratoire : $6.8503597122 \times 10^{-15}$

Lecture pratique :
- la bande BBN reste l'ancrage principal,
- le canal laboratoire reste fortement suppressé,
- le canal neutronique active une compacité et une dilatation du temps compatibles avec les ordres de grandeur observés.

## Transition
Si une bande commune existe, elle devient la valeur physique de travail pour les extensions cosmologiques et compactes.
Sinon, V82 sert de point de rupture pour réviser le Lagrangien de V81.