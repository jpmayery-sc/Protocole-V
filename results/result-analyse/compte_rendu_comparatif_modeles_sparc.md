# Compte rendu scientifique comparatif des modèles SPARC

## Résumé exécutif

Trois modèles ont été testés sur le catalogue SPARC de 175 galaxies :

1. un halo plat à une seule vitesse asymptotique $V_{\rm halo}$,
2. un halo pseudo-isotherme à deux paramètres $(\rho_0, r_0)$,
3. le même halo pseudo-isotherme avec un facteur global libre de masse-lumière stellaire $M/L$.

Le résultat principal est clair : la structure du halo et la liberté baryonique changent profondément la qualité des ajustements. Le modèle plat est trop rigide, le halo pseudo-isotherme améliore fortement les ajustements, et l'ajout d'un facteur global de $M/L$ améliore encore nettement les performances populationnelles.

## Résultats numériques

### 1) Halo plat

- Galaxies ajustées : 175
- Cas avec $V_{\rm halo} > 0$ : 136
- $V_{\rm halo}$ médian : 57.73 km/s
- $V_{\rm halo}$ moyen : 63.80 km/s
- $\rho_0$ médiane déduite pour $r_0 = 1$ kpc : $6.17 \times 10^7\,M_\odot\,\mathrm{kpc}^{-3}$
- $\chi^2_{\min}$ médian : 208.86

Interprétation : le modèle est trop pauvre pour absorber la diversité des courbes de rotation SPARC. Une fraction non négligeable de galaxies reste collée à la borne $V_{\rm halo}=0$, ce qui est un signal de saturation numérique et de rigidité du modèle, pas une mesure physique robuste.

### 2) Halo pseudo-isotherme

- Galaxies ajustées : 175
- $\rho_0$ médiane : $1.02 \times 10^7\,M_\odot\,\mathrm{kpc}^{-3}$
- $r_0$ médian : 2.51 kpc
- $\chi^2_{\min}$ médian : 18.29
- Sous-échantillon $Q=1$ : $\chi^2_{\min}$ médian 19.28, $r_0$ médian 3.63 kpc

Interprétation : la liberté de forme du halo casse la contrainte trop simple du halo plat. Le gain sur $\chi^2$ est massif, et les paramètres deviennent physiquement plus interprétables. Quelques galaxies restent sur des bords de grille, mais le comportement est désormais dominé par la structure réelle du fit, pas par l'absence de paramètre de forme.

### 3) Halo pseudo-isotherme + $M/L$ stellaire libre

- Galaxies ajustées : 175
- $M/L$ stellaire médian : 0.45
- $M/L$ stellaire moyen : 0.64
- $\rho_0$ médiane : $5.16 \times 10^7\,M_\odot\,\mathrm{kpc}^{-3}$
- $r_0$ médian : 1.94 kpc
- $\chi^2_{\min}$ médian : 5.11
- Sous-échantillon $Q=1$ : $\chi^2_{\min}$ médian 7.86, $M/L$ médian 0.53

Interprétation : libérer un seul facteur global baryonique absorbe une part importante de la dégénérescence baryons-halo. Le gain est net et cohérent avec le comportement attendu des courbes de rotation. La dispersion du $M/L$ et certaines solutions collées à la borne basse indiquent toutefois qu'un prior physique ou une séparation disque/bulbe pourrait encore stabiliser le problème.

### 4) Halo NFW

- Galaxies ajustées : 175
- $\rho_s$ médiane : $2.49 \times 10^4\,M_\odot\,\mathrm{kpc}^{-3}$
- $r_s$ médian : 55.56 kpc
- $\chi^2_{\min}$ médian : 36.28
- Sous-échantillon $Q=1$ : $\chi^2_{\min}$ médian 45.15

Interprétation : le halo cuspy améliore nettement le modèle plat, mais il reste moins performant que les halos à cœur sur SPARC. Pour ces données, la cuspide NFW n'absorbe pas aussi bien la diversité des profils internes que le pseudo-isotherme.

## Critère pénalisé

Sur l'ensemble des 175 galaxies, les sommes globales donnent :

- Halo plat : $\chi^2 \approx 327265$, AIC $\approx 327615$, BIC $\approx 327739$
- Halo pseudo-isotherme : $\chi^2 \approx 173063$, AIC $\approx 173763$, BIC $\approx 174010$
- Halo pseudo-isotherme + $M/L$ libre : $\chi^2 \approx 7598$, AIC $\approx 8648$, BIC $\approx 9018$
- Halo NFW : $\chi^2 \approx 192913$, AIC $\approx 193613$, BIC $\approx 193860$

Le classement ne change pas quand on pénalise le nombre de paramètres : le modèle pseudo-isotherme avec $M/L$ libre reste de loin le meilleur compromis statistique sur ce jeu de données.

## Lecture physique

Le passage du halo plat au halo pseudo-isotherme montre que la principale limite initiale était bien le modèle, pas seulement la qualité des données. L'ajout du $M/L$ libre prouve ensuite qu'une partie de la tension résiduelle venait de la rigidité baryonique. En d'autres termes, le catalogue SPARC a suffisamment d'information pour contraindre un modèle plus riche, mais pas un modèle trop contraint.

## Test de solidité du principe de moindre résistance

Si on formule "la moindre résistance" comme une intuition, ce n'est pas encore une loi physique. Pour être solide, il faut pouvoir dire : quelle variable résiste, à quel flux, avec quelle équation, et quelles prédictions numériques en résultent.

Les tests que nous avons maintenant permettent de trier ce qui tient vraiment :

- Le halo plat n'est pas solide physiquement comme théorie descriptive, car il sature souvent sur une borne et laisse une grande partie de la structure galactique hors du modèle.
- Le halo NFW est physiquement motivé par la cosmologie, mais sur SPARC il reste moins performant et plus souvent bloqué aux bords numériques que les modèles à cœur.
- Le halo pseudo-isotherme est déjà un bon proxy d'une physique intermédiaire : profil régulier, cœur fini, interprétation simple, meilleure compatibilité avec les courbes.
- Le halo pseudo-isotherme avec $M/L$ libre est, à ce stade, la version la plus robuste statistiquement et la plus souple physiquement, avec moins de cas de bord que les autres modèles testés.

Le point important est donc le suivant : la "moindre résistance" n'est pas encore la théorie elle-même, mais elle pointe vers une classe de modèles à cœur, réguliers, locaux et ajustables, dont le pseudo-isotherme + $M/L$ libre est actuellement le meilleur représentant.

Du côté des chiffres de stabilité numérique, les cas de bord sont :

- Halo plat : 39 / 175
- Halo pseudo-isotherme : 45 / 175
- Halo pseudo-isotherme + $M/L$ libre : 31 / 175
- Halo NFW : 67 / 175

Le sous-échantillon $Q=1$ confirme la même hiérarchie relative. Cela ne prouve pas une théorie fondamentale, mais cela montre qu'une physique intermédiaire à cœur est mieux soutenue par les données qu'un profil cuspy ou qu'un halo trop rigide.

## Principe explicite proposé

On peut rendre l'idée testable en l'écrivant comme un principe de sélection du halo :

$$
\mathcal{F}[\rho_h, M/L] = \chi^2 + \lambda_1 \int \left(\frac{d \ln \rho_h}{dr}\right)^2 dr + \lambda_2 \int \left(\frac{d^2 \ln \rho_h}{dr^2}\right)^2 dr
$$

où :

- $\chi^2$ mesure l'accord avec les courbes de rotation,
- les deux termes réguliers imposent une "résistance" faible mais non nulle aux variations brusques de structure,
- $\rho_h$ est le profil de halo,
- $M/L$ est le relâchement baryonique global.

Le principe de moindre résistance devient alors :

> parmi les profils admissibles, la galaxie réalise celui qui minimise $\mathcal{F}$, sous contraintes physiques faibles de régularité et de positivité.

Ce n'est pas encore une théorie fondamentale autonome, mais c'est une formulation mathématique claire, falsifiable et exploitable.

### Prédiction testable

Cette formulation implique une prédiction simple sur la structure galactique :

- les galaxies les plus compactes baryoniquement doivent préférentiellement avoir un $r_0$ plus petit et une $\rho_0$ plus grande,
- à l'inverse, les galaxies diffuses doivent exhiber des cœurs plus étendus et moins denses,
- si cette tendance n'apparaît pas dans les sous-échantillons de haute et faible densité de surface, le principe de moindre résistance n'est pas soutenu.

Autrement dit, la variable à tester n'est pas seulement $\chi^2$, mais la corrélation entre compacité baryonique et paramètre de cœur du halo.

### Test SPARC de cette prédiction

Sur le modèle pseudo-isotherme avec $M/L$ libre, le test direct donne un signal très faible :

- corrélation de Pearson entre $\log_{10}(\mathrm{SBdisk})$ et $\log_{10}(r_0)$ sur les 175 galaxies : $\rho \approx -0.065$,
- sur le sous-échantillon non bordé : $\rho \approx 0.057$,
- sur le sous-échantillon $Q=1$ non bordé : $\rho \approx 0.008$.

La séparation en deux moitiés compactes / diffuses ne donne pas non plus une hiérarchie stable de $r_0$.

Conclusion locale : la version simple de la prédiction "plus compact = plus petit coeur" n'est pas confirmée de manière robuste par SPARC, au moins avec ce proxy de compacité et ce modèle de halo.

## Ce qu'il faut considérer comme solide

À ce stade, ce qui est solidement établi par les tests n'est pas une loi fondamentale de résistance, mais trois faits empiriques :

1. un halo trop rigide est rejeté par SPARC,
2. un halo cuspy NFW est meilleur mais reste sous-optimal,
3. une famille à cœur, souple mais régulière, est la plus compatible avec les données quand on lui laisse une petite liberté baryonique.

Le principe de moindre résistance est donc utile comme cadre de sélection et comme intuition structurante, mais la prédiction compacte/diffuse la plus simple ne tient pas encore comme loi empirique.

## Ce qu'on peut retenir

- Le modèle plat est trop restrictif pour une interprétation populationnelle sérieuse.
- Le halo pseudo-isotherme constitue une base nettement plus crédible.
- La liberté sur $M/L$ améliore encore fortement les ajustements, mais introduit une dégénérescence qu'il faut encadrer par des priors physiques.
- Les métriques de $\chi^2$ sont très améliorées, mais une comparaison rigoureuse entre modèles devrait aussi passer par AIC/BIC ou validation croisée, car le nombre de paramètres augmente.
- Avec AIC/BIC, le verdict reste le même : le modèle pseudo-isotherme + $M/L$ libre est le plus solide parmi ceux testés ici.

## Conclusion

Le diagnostic est désormais clair : la limite venait bien du modèle, et non seulement de la qualité des galaxies. Le passage au halo pseudo-isotherme, puis à la version avec $M/L$ libre, a transformé un fit trop rigide en un cadre bien plus compatible avec SPARC. Statistiquement, cette version est la plus convaincante parmi les quatre modèles testés, même après pénalisation du nombre de paramètres.

Sur la théorie, la réponse courte est : l'idée de "moindre résistance" est bonne comme guide de construction, mais pas encore comme loi physique établie. Ce qui est solide aujourd'hui, c'est la version opérationnelle qui en découle : un halo à cœur, régulier, avec baryons libres de bouger un peu. La version la plus propre consiste à la lire comme un principe variationnel de sélection du profil, pas comme une nouvelle force brute. Pour en faire une théorie forte, il faut encore vérifier la prédiction de compacité, stabiliser les paramètres sous priors physiques et comparer à d'autres jeux de données ou à des contraintes indépendantes.

La vérification de compacité faite ici montre justement que cette étape n'est pas encore franchie : le cadre est intéressant, mais il faut désormais une formulation plus précise de la "résistance" si tu veux en faire un mécanisme prédictif solide.