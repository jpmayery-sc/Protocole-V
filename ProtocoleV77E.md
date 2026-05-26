# V77E — ÉCHANGES INTERNES A=7 ET VIDANGE EXPLICITE
# Version : 1.0 — Mode recherche, niveau flux internes
# Auteur : Jean-Philippe
# Objet : tester si des échanges internes Li-7 ↔ Be-7 et une vidange explicite A=7 peuvent faire passer Li_total dans la fenêtre

Protocole précédent : ProtocoleV77D.md
Protocole suivant : V78R (si un schéma d’échanges viable est identifié)

Wrapper global suggéré :
- python/scripts/runv77e_a7_exchange_drain.py

CONTENU :
- 0. Objectif
- 1. Hypothèses
- 2. Nouveaux termes
- 3. Questions de recherche
- 4. Pipeline V77E
- 5. Sorties attendues
- 6. Transition

0. OBJECTIF
-----------
Après V77D, on sait que l’électron fournit un levier réel ($\beta_e$) qui fait baisser Li_total sans casser D/H ni $Y_p$, mais Li_total ne passe pas encore la fenêtre.

V77E cherche à :
- introduire explicitement des échanges internes Li-7 $\leftrightarrow$ Be-7,
- introduire une vidange explicite du réservoir A=7,
- tester si une combinaison échange + vidange permet de faire passer Li_total dans la fenêtre observationnelle.

V77E est un test de flux internes, pas un ajustement cosmologique.


1. HYPOTHÈSES
-------------
- Paramètres globaux fixés :
  - $\varepsilon_{best} = -0.0069$
  - $\delta_{EM} = -0.0069$
  - $k_G$, $k_T$, $k_n$ = V83
- Paramètre électronique fixé au meilleur point de V77D :
  - $\beta_e = 1.2$
- On part des valeurs A=7 de V77D au meilleur point :
  - Li7_base, Be7_base, Li_total_base
- On ajoute deux nouveaux degrés de liberté :
  - $\gamma_{exch}$ = intensité d’échange interne Li-7 $\leftrightarrow$ Be-7
  - $\gamma_{drain}$ = intensité de vidange A=7 vers plus léger.


2. NOUVEAUX TERMES
------------------
On modélise les flux internes A=7 de façon phénoménologique :

1) Échange interne Li-7 $\leftrightarrow$ Be-7 (contrôlé par $\gamma_{exch}$)
   - modèle jouet :
     - $Be7_{exch} = Be7_{base} \cdot (1 - \gamma_{exch})$
     - $Li7_{exch} = Li7_{base} + \eta_{exch} \cdot (Be7_{base} - Be7_{exch})$
   - $\eta_{exch} \in [0,1]$ : fraction de Be-7 convertie en Li-7 (par défaut $\eta_{exch} = 1$).

2) Vidange A=7 (contrôlée par $\gamma_{drain}$)
   - modèle jouet :
     - $Li7_{final} = Li7_{exch} \cdot (1 - \gamma_{drain})$
     - $Be7_{final} = Be7_{exch} \cdot (1 - \gamma_{drain})$

3) $Li_{total,final} = Li7_{final} + Be7_{final}$

Plages de test :
- $\gamma_{exch} \in [0.0, 1.0]$ (5 points)
- $\gamma_{drain} \in [0.0, 0.5]$ (5 points)


3. QUESTIONS DE RECHERCHE
-------------------------
V77E doit répondre à :

1) Un schéma échange + vidange peut-il réduire fortement Be-7, maintenir Li-7 dans la fenêtre, et faire passer Li_total dans la fenêtre ?

2) Existe-t-il une zone $(\gamma_{exch}, \gamma_{drain})$ où Li-7/H et Li_total/H sont tous deux dans la fenêtre, avec D/H et $Y_p$ quasi inchangés ?

3) L’équilibre interne A=7 peut-il réellement s’inverser ?


4. PIPELINE V77E
----------------

4.1 Grille de test
------------------
- Fixer D/H et $Y_p$ à leurs valeurs de V77D au meilleur $\beta_e$.
- Fixer Li7_base et Be7_base à leurs valeurs de V77D au meilleur $\beta_e$.
- Définir les grilles :
  - $\gamma_{exch} \in [0.0, 1.0]$ avec 5 points
  - $\gamma_{drain} \in [0.0, 0.5]$ avec 5 points

Pour chaque paire $(\gamma_{exch}, \gamma_{drain})$ :
- calculer Li7_exch, Be7_exch,
- calculer Li7_final, Be7_final,
- calculer Li_total_final,
- enregistrer les valeurs.


4.2 Critères de passage
-----------------------
Définir les fenêtres observationnelles utilisées dans la chaîne V77/V80 :
- Li-7/H_obs $\in [1.27, 1.89] \times 10^{-10}$
- Li_total/H_obs $\in [1.27, 1.89] \times 10^{-10}$

Pour chaque $(\gamma_{exch}, \gamma_{drain})$ :
- marquer Li7_pass et LiTot_pass.


4.3 Analyse des flux
--------------------
Pour les points intéressants (Li7_pass et LiTot_pass) :
- comparer Be7_final vs Be7_base,
- comparer Li7_final vs Li7_base,
- comparer Li_total_final vs Li_total_base,
- vérifier que Be-7 a bien été vidé et que Li_total a réellement baissé.


5. SORTIES ATTENDUES
--------------------
- V77E_EXCHANGE_DRAIN_SCAN.txt
- cartes Li7_final vs $(\gamma_{exch}, \gamma_{drain})$
- cartes Be7_final vs $(\gamma_{exch}, \gamma_{drain})$
- cartes Li_total_final vs $(\gamma_{exch}, \gamma_{drain})$
- un résumé textuel avec la meilleure paire et les flags de passage.

Phrase de synthèse attendue :
> "Il existe / n’existe pas une zone $(\gamma_{exch}, \gamma_{drain})$ où Li-7/H et Li_total/H sont tous deux dans la fenêtre, avec Be-7 vidée et un équilibre interne A=7 inversé."


6. TRANSITION
-------------
- Si V77E trouve une zone physiquement plausible où Li7 et Li_total passent :
  → V78R pourra tenter de relier ces paramètres à des mécanismes physiques concrets.
- Si V77E ne trouve aucune zone acceptable :
  → même avec échange + vidange, le proxy A=7 reste trop rigide.

V77E est un test de flux internes :
il doit dire si "vider d’un côté et remplir de l’autre" peut réellement inverser l’équilibre A=7.


## Résultat V77E
Le scan échange + vidange trouve une zone viable :
- verdict : `zone_viable_trouvee`
- nombre de points où Li-7 et Li_total passent : 4

Meilleure paire :
- $\gamma_{exch} = 1.0$
- $\gamma_{drain} = 0.375$

Valeurs associées :
- Li7_exch = $2.225\times 10^{-10}$
- Be7_exch = $0$
- Li7_final = $1.390625\times 10^{-10}$
- Be7_final = $0$
- Li_total_final = $1.390625\times 10^{-10}$

Lecture :
- Be-7 est totalement vidé au meilleur point,
- Li-7 reste dans la fenêtre,
- Li_total entre aussi dans la fenêtre,
- l’équilibre interne A=7 est donc inversé dans ce proxy jouet.