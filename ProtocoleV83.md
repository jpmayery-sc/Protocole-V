# V83 — CALIBRATION GLOBALE : GRAVITÉ, TEMPS, ÉTOILES À NEUTRONS

## Objectif
Utiliser la bande $\varepsilon$ physique issue de V82 pour calibrer les constantes du Lagrangien de V81, afin que :
- les masses d’étoiles à neutrons tombent dans la bonne fenêtre,
- les rayons tombent dans la bonne fenêtre,
- les redshifts tombent dans la bonne fenêtre,
- la gravité locale reste inchangée,
- la BBN reste inchangée.

V83 ajuste les couplages, pas $\varepsilon$.
$\varepsilon$ est fixé par la BBN et par V82.

## Entrées nécessaires
1. Paramètre fondamental :
- $\varepsilon_{best} = -0.0069$ issu de V82

2. Fonctions du Lagrangien V81 :
- $\delta_{EM}(\varepsilon)$
- $\pi_n(\varepsilon, \rho_n)$
- $G_{eff}(\varepsilon, \rho_n)$
- $F_{temps}(\varepsilon, \rho_n)$

3. Données réelles de travail :
- masses NS : $2.01$–$2.08\,M_\odot$ pour les pulsars massifs de référence
- rayons NICER : $11$–$14$ km pour $1.4\,M_\odot$
- redshifts observés : $z \approx 0.2$–$0.4$
- gravité locale : variation $< 2\times 10^{-5}$
- variation EM labo : $< 10^{-16}$

4. Paramètres à calibrer :
- $k_G$ (gravité)
- $k_T$ (temps)
- $k_n$ (structuration neutronique)

## Pipeline V83
### Étape A — Calibration de $k_G$
Objectif : obtenir une étoile à neutrons compacte mais stable.

1. Fixer $\varepsilon = \varepsilon_{best}$.
2. Choisir $k_G$ pour placer $G_{eff}^{NS}$ dans une fenêtre utile.
3. Vérifier que le proxy $M_{max}$ reste autour de $2.0$–$2.1\,M_\odot$.

### Étape B — Calibration de $k_T$
Objectif : obtenir $z \approx 0.2$–$0.4$.

1. Fixer $\varepsilon = \varepsilon_{best}$ et $k_G$ calibré.
2. Choisir $k_T$ pour que $z_{eff} = 1/F_{temps} - 1$ tombe dans la fenêtre voulue.

### Étape C — Calibration de $k_n$
Objectif :
- $\pi_n \approx 0$ en labo,
- $\pi_n \approx 1$ en NS,
- variation EM labo $< 10^{-16}$.

1. Fixer $\varepsilon = \varepsilon_{best}$.
2. Choisir $k_n$ pour que le canal laboratoire soit très fortement supprimé et que le canal NS s’active à $\pi_n \approx 1$.

## Résultats attendus
V83 doit fournir :
- $k_G$, $k_T$, $k_n$ calibrés,
- $G_{eff}(labo)$,
- $G_{eff}(NS)$,
- $M_{max}$,
- $R_{1.4}$,
- $z_{eff}$,
- $\delta_{EM}$,
- variation EM labo.

## Résultat V83
Le calibrateur global confirme la cohérence des fenêtres de travail :
- verdict : `v83_calibration_confirmed`
- $\varepsilon_{best} = -0.0069$
- $k_G = 40.5797101449$
- $k_T = 43.4782608696$
- $k_n = 144.9275362319$

Observables calibrées :
- $\delta_{EM} = -0.0069$
- $\pi_n^{labo} = 1.0 \times 10^{-16}$
- $\pi_n^{NS} = 1.0$
- $G_{eff}^{labo} \approx 1.0\,G$
- $G_{eff}^{NS} = 1.28\,G$
- $F_{temps}^{labo} \approx 1.0$
- $F_{temps}^{NS} = 0.7692307692$
- $z_{eff} = 0.30$
- $M_{max} = 2.0327692308\,M_\odot$
- $R_{1.4} = 11.0667692308$ km
- variation EM labo = $6.9 \times 10^{-19}$

Lecture pratique :
- la BBN reste l’ancrage fixe via $\varepsilon_{best}$,
- le canal laboratoire est correctement éteint,
- le canal neutronique reste activé avec des masses, rayons et redshifts dans les fenêtres visées.

## Transition vers V84
V84 devient l’extension cosmologique :
- impact de $\varepsilon_{best}$ sur l’expansion,
- densité critique,
- structure à grande échelle,
- signatures CMB,
- cohérence avec $\Lambda$CDM.

V83 fournit les paramètres calibrés pour passer au cosmologique.

Protocole suivant : V84 (extension cosmo : expansion, structure, CMB)