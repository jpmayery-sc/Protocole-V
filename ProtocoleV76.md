# V76 — RÉSOLUTION CIBLÉE DU LITHIUM
# Version : 1.0 — Pont entre V75B et V80B
# Auteur : Jean-Philippe
# Objet : mesurer si la correction lithium est robuste ou seulement fine

Protocole précédent : ProtocoleV75B.md
Protocole suivant : V77 (branche alternative si la robustesse échoue)

Wrapper global suggéré :
- python/scripts/runv76_li_diagnostics.py

CONTENU :
- 0. Objectif
- 1. Ancrages
- 2. Hypothèses V76
- 3. Rejeu V80B avec diagnostics étendus
- 4. Analyse de sensibilité locale
- 5. Robustesse du résultat Li
- 6. Résultats attendus
- 7. Verdict V76
- 8. Transition

0. OBJECTIF
-----------
Clarifier la tension lithium vue en V75B en s’appuyant sur :
- le point physique $\varepsilon_{best} = -0.0069$,
- le succès numérique de V80B,
- une analyse plus fine et plus honnête du canal Li.

V76 ne cherche pas à améliorer artificiellement les chiffres. Il répond à la question centrale :
- le lithium est-il vraiment résolu de façon robuste ?
- ou bien est-ce un effet fragile du proxy jouet ?


1. ANCRAGES
-----------
- V75B : D/H et $Y_p$ OK, tension Li encore ouverte dans le benchmark standard.
- V80B : à $\delta_{EM} = -0.0069$, D/H, $Y_p$ et Li-7/H tombent numériquement dans les fenêtres observationnelles du proxy jouet.
- V81--V83 : $\varepsilon_{best}$, $k_G$, $k_T$, $k_n$ sont déjà fixés ; V76 ne touche pas ces paramètres.


2. HYPOTHÈSES V76
-----------------
- $\varepsilon = \varepsilon_{best} = -0.0069$ fixe
- $\delta_{EM} = -0.0069$ fixe
- couplages gravité / temps / neutrons = ceux de V83, fixes
- on ne joue que sur :
  - la finesse du proxy BBN,
  - la compréhension de la sensibilité du canal Li.


3. REJEU V80B AVEC DIAGNOSTICS ÉTENDUS
-------------------------------------
Étape A : refaire le calcul BBN à $\delta_{EM} = -0.0069$.

Sorties attendues :
- D/H, $Y_p$, Li-7/H, Be-7/H,
- un diagnostic de canal lithium avec :
  - contribution directe Li-7,
  - contribution de feed-down via Be-7,
  - score de cohérence pour la somme effective Li-7 + Be-7.


4. ANALYSE DE SENSIBILITÉ LOCALE
--------------------------------
Étape B : scanner $\delta_{EM}$ dans une micro-fenêtre, par exemple

$$
\delta_{EM} \in [-0.0072, -0.0066].
$$

Pour chaque point :
- calculer D/H, $Y_p$, Li-7/H, Be-7/H,
- tracer Li-7/H vs $\delta_{EM}$,
- tracer D/H vs $\delta_{EM}$,
- tracer $Y_p$ vs $\delta_{EM}$.

Lecture attendue :
- si la correction Li reste stable dans une petite bande, elle est au moins fine,
- si elle dépend d’un réglage ultra-étroit, elle est fragile.


5. ROBUSTESSE DU RÉSULTAT LI
----------------------------
Étape C : introduire des variations raisonnables sur les taux nucléaires Li / Be, à l’échelle de quelques pourcents.

Le diagnostic doit répondre à :
- Li-7/H reste-t-il dans la fenêtre observationnelle ?
- la somme effective Li-7 + Be-7 reste-t-elle cohérente ?
- la correction survit-elle à ces variations ?

Cette étape est volontairement un proxy de sensibilité. Elle ne remplace pas une BBN complète, mais elle permet de tester la fragilité du point V80B.


6. RÉSULTATS ATTENDUS
---------------------
Le testeur doit produire :
- des courbes de sensibilité autour de $\delta_{EM} = -0.0069$,
- un tableau de robustesse sous variations des taux,
- un verdict textuel sur le statut du lithium.


7. VERDICT V76
--------------
À l’issue de V76, le lithium est classé dans l’un des trois cas suivants :

1. Résolution robuste :
- D/H et $Y_p$ OK,
- Li-7/H dans la fenêtre observationnelle,
- résultat stable dans une petite bande de $\delta_{EM}$,
- résultat stable vis-à-vis des variations raisonnables des taux.

2. Résolution fine / tuning :
- Li-7/H OK seulement dans une bande étroite,
- ou résultat très sensible aux variations des taux,
→ à documenter comme une tension partiellement levée mais fragile.

3. Tension persistante :
- le raffinement du proxy fait réapparaître un écart significatif,
→ il faudra revoir le canal EM ou la structure du modèle.


## Résultat V76
Le diagnostic numérique autour de $\delta_{EM}=-0.0069$ donne :
- D/H = $2.530\times 10^{-5}$, passe
- $Y_p = 0.2467$, passe
- Li-7/H = $1.566\times 10^{-10}$, passe
- Li total proxy = $2.896\times 10^{-10}$, ne passe pas
- Be-7/H = $1.329\times 10^{-10}$

Sensibilité locale :
- bande acceptée pour D/H, $Y_p$ et Li-7/H : $[-0.0072, -0.0066]$
- largeur de bande : $0.0006$
- bande acceptée pour le Li total proxy : aucune dans cette fenêtre

Robustesse sous variations de taux :
- cas directs Li-7 : $9/9$ passent
- cas Li total proxy : $0/9$ passent

Verdict numérique :
- `resolution_fine`
- Li est corrigé au point central, mais la correction n’est pas robuste sur le canal total incluant Be-7.


8. TRANSITION
-------------
- Si V76 conclut à une résolution robuste :
  → V80B–V83 restent valides, on peut avancer vers V84 cosmologie.
- Si V76 conclut à un tuning ou à une tension persistante :
  → on ouvre une branche V77 pour modifier soit le canal EM, soit le couplage au secteur nucléaire.