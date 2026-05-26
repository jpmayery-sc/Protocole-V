# V77B — STRESS TEST A=7 : LI-7, BE-7, CANAL EM
# Version : 1.0 — Direction EM différentielle
# Auteur : Jean-Philippe
# Objet : tester si un canal EM différentiel peut corriger Li_total sans casser D/H et Y_p

Protocole précédent : ProtocoleV77.md
Protocole suivant : V78 (si une direction claire apparaît)

Wrapper global suggéré :
- python/scripts/runv77b_em_stress_test.py

CONTENU :
- 0. Objectif
- 1. Hypothèses fixes
- 2. Paramètres de test
- 3. Observables suivies
- 4. Pipeline V77B
- 5. Ce qu’on cherche à voir
- 6. Verdict V77B
- 7. Sorties attendues
- 8. Transition

0. OBJECTIF
-----------
Ne plus raisonner à l’aveugle sur Li-7 seul, mais :
- tester simultanément Li-7, Be-7 et Li_total,
- faire bouger de façon contrôlée le canal EM global ($\delta_{EM}$),
- introduire une pondération EM spécifique pour Be-7,
- varier les taux nucléaires Li / Be,
- et regarder qui réagit, comment, et avec quelle sensibilité.

V77B ne cherche pas encore à réparer; il cherche une direction claire.


1. HYPOTHÈSES FIXES
-------------------
On ne touche pas au cœur du modèle :
- $\varepsilon_{best} = -0.0069$
- couplages gravité / temps / neutrons $(k_G, k_T, k_n)$ = V83
- proxy BBN = V80, même code, mêmes constantes de base

On joue uniquement sur :
- $\delta_{EM}$ (micro-variations autour de $-0.0069$),
- une pondération EM spécifique pour Be-7,
- des variations de taux nucléaires Li / Be.


2. PARAMÈTRES DE TEST
---------------------
1) $\delta_{EM}$ global
   - plage : $[-0.0072, -0.0066]$
   - pas : 5 points

2) pondération EM spécifique Be-7
   - introduire un facteur $\alpha_{Be}$ :
     - $\delta_{EM}^{(Li)} = \delta_{EM}$
     - $\delta_{EM}^{(Be)} = \alpha_{Be} \cdot \delta_{EM}$
   - plage $\alpha_{Be}$ : $[0.5, 1.0]$

3) variations de taux nucléaires Li / Be
   - Li-7 : $\pm 5\%$
   - Be-7 : $\pm 5\%$
   - cas croisés inclus


3. OBSERVABLES SUIVIES
----------------------
Pour chaque combinaison $(\delta_{EM}, \alpha_{Be}, taux)$ :
- D/H
- $Y_p$
- Li-7/H
- Be-7/H
- Li_total = Li-7/H + Be-7/H
- $\chi^2_{proxy\_BBN}$ pour $(D, Y, Li_total)$


4. PIPELINE V77B
----------------
1) Boucle sur $\delta_{EM} \in [-0.0072, -0.0066]$
2) Pour chaque $\delta_{EM}$, boucle sur $\alpha_{Be} \in [0.5, 1.0]$
3) Pour chaque $(\delta_{EM}, \alpha_{Be})$, boucle sur variations de taux Li / Be ($\pm 5\%$)
4) À chaque point :
   - lancer le proxy BBN différentiel
   - enregistrer D/H, $Y_p$, Li-7/H, Be-7/H, Li_total
5) Construire :
   - cartes Li-7/H($\delta_{EM}, \alpha_{Be}$)
   - cartes Be-7/H($\delta_{EM}, \alpha_{Be}$)
   - cartes Li_total($\delta_{EM}, \alpha_{Be}$)
   - indicateurs de stabilité sous variations de taux


5. CE QU’ON CHERCHE À VOIR
--------------------------
1) Qui est le plus sensible à $\delta_{EM}$ ?
   - Li-7 ?
   - Be-7 ?
   - les deux pareil ?
   - le total Li bouge-t-il vraiment ou seulement la répartition interne ?

2) $\alpha_{Be}$ change-t-il quelque chose de significatif ?
   - si Li_total est sensible à $\alpha_{Be}$, bonne piste pour un canal EM différentiel
   - si Li_total ne réagit presque pas, le problème est ailleurs

3) Les variations de taux Li / Be :
   - si Li_total explose dès $\pm 5\%$, résolution fragile
   - si Li_total reste dans une bande raisonnable, résolution potentiellement robuste si bien réglée


6. VERDICT V77B
--------------
V77B doit répondre à :

> Est-ce que le canal EM, modulé différemment sur Be-7, a le pouvoir de corriger Li_total sans casser D/H et $Y_p$ ?

Trois cas possibles :

1) Canal EM différentiel efficace :
- Li_total baisse en jouant sur $\alpha_{Be}$,
- D/H et $Y_p$ restent stables,
- sensibilité aux taux nucléaires raisonnable.

2) Canal EM différentiel inefficace :
- Li_total reste trop haut quelle que soit $\alpha_{Be}$,
- ou D/H / $Y_p$ se dégradent dès qu’on force.

3) Résolution ultra-fine :
- petite zone $(\delta_{EM}, \alpha_{Be})$ où tout passe,
- mais forte sensibilité aux taux nucléaires.


7. SORTIES ATTENDUES
--------------------
- cartes Li-7/H($\delta_{EM}, \alpha_{Be}$)
- cartes Be-7/H($\delta_{EM}, \alpha_{Be}$)
- cartes Li_total($\delta_{EM}, \alpha_{Be}$)
- tableau de stabilité sous variations de taux
- verdict qualitatif : direction EM différentiel utile / inutile / tuning


8. TRANSITION
-------------
- si une direction claire apparaît :
   → V78 peut intégrer un canal EM différentiel Li / Be
- si aucune direction nette n’apparaît :
   → le canal EM seul ne suffit pas, et le lithium reste une tension physique ouverte

## Résultat V77B
Le stress test numérique sur la grille par défaut donne :
- verdict : `resolution_ultra_fine`
- interprétation : direction EM différentiel tuning
- meilleur point : $\delta_{EM} = -0.0072$, $\alpha_{Be} = 1.0$
- D/H = $2.533\times 10^{-5}$
- $Y_p = 0.24673$
- Li-7/H = $1.412\times 10^{-10}$
- Be-7/H = $1.202\times 10^{-10}$
- Li_total = $2.614\times 10^{-10}$

Comptages de passage :
- direct : $225/225$
- total-lithium : $0/225$

Lecture :
- Li-7 direct est stable sur toute la grille,
- Li_total reste au-dessus de la fenêtre observationnelle,
- la pondération EM différentielle sur Be-7 ne ferme pas le canal total.