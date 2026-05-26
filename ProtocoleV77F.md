# V77F — FORME DE LA COURBE ET POINT DE BASCULE
# Version : 1.0 — Mode recherche, lecture globale des flux
# Auteur : Jean-Philippe
# Objet : demander une vision claire de la forme de la courbe Li_total dans l’espace des paramètres

Protocole précédent : ProtocoleV77E.md
Protocole suivant : V78R (ancrage au réel / code BBN)

Wrapper global suggéré :
- python/scripts/runv77f_curve_shape.py

CONTENU :
- 0. Objectif
- 1. Paramètres considérés
- 2. Questions au testeur
- 3. Pipeline V77F
- 4. Sorties attendues
- 5. Transition

0. OBJECTIF
-----------
V77F ne cherche pas à explorer de nouveaux paramètres,
mais à obtenir une vision globale de la forme de la courbe Li_total :

- y a-t-il une pente nette ?
- y a-t-il un point de bascule ?
- la zone acceptable est-elle large ou ultra-fine ?
- l’équilibre interne A=7 se renverse-t-il vraiment ou juste marginalement ?

V77F demande explicitement une lecture qualitative de la courbe, pas seulement des chiffres.


1. PARAMÈTRES CONSIDÉRÉS
------------------------
V77F se place dans l’espace des paramètres déjà explorés :

- $\beta_e$ : levier électronique (V77D)
- $\gamma_{exch}$ : intensité d’échange interne Li-7 $\leftrightarrow$ Be-7 (V77E)
- $\gamma_{drain}$ : intensité de vidange A=7 (V77E)

On considère :

1) La courbe Li_total($\beta_e$) à $\gamma_{exch} = 0$, $\gamma_{drain} = 0$ (V77D pur).
2) La surface Li_total($\gamma_{exch}, \gamma_{drain}$) au meilleur $\beta_e$ (V77E).
3) Des coupes 1D :
   - Li_total($\gamma_{exch}$) à $\gamma_{drain}$ fixé,
   - Li_total($\gamma_{drain}$) à $\gamma_{exch}$ fixé.


2. QUESTIONS AU TESTEUR
-----------------------
Le testeur doit répondre qualitativement aux questions suivantes :

1) Courbe Li_total($\beta_e$) (V77D) :
   - est-elle monotone, convexe, concave ?
   - y a-t-il un minimum net autour de $\beta_e \approx 1.2$ ?
   - la zone basse est-elle large ou très localisée ?

2) Surface Li_total($\gamma_{exch}, \gamma_{drain}$) (V77E) :
   - voit-on une pente claire qui mène d’une zone Li_total haut à une zone Li_total bas ?
   - y a-t-il une ligne de bascule où Li_total passe sous un seuil critique ?
   - la zone où Li_total est dans la fenêtre est-elle robuste, fine ou ultra-fine ?

3) Équilibre interne A=7 :
   - dans la zone bonne, Be-7 est-il vraiment vidé ?
   - Li-7 reste-t-il acceptable ?
   - l’impression globale est-elle celle d’un vrai renversement ou d’un rabotage sans bascule nette ?

4) Vision globale :
   - si tu dessinais Li_total à la main, verrais-tu un plateau, une pente, un minimum, ou une simple descente douce ?


3. PIPELINE V77F
----------------

3.1 Récupération des données
----------------------------
- Charger les résultats de V77D : $\beta_e$, Li7($\beta_e$), Be7($\beta_e$), Li_total($\beta_e$).
- Charger les résultats de V77E : $\gamma_{exch}$, $\gamma_{drain}$, Li7_final, Be7_final, Li_total_final.

3.2 Tracés
----------
- Tracer Li_total($\beta_e$) (courbe 1D).
- Tracer Li_total($\gamma_{exch}, \gamma_{drain}$) (carte 2D).
- Optionnel : tracer des contours et marquer la zone de passage.

3.3 Lecture qualitative
-----------------------
Le testeur doit regarder les courbes / cartes, répondre aux questions ci-dessus et formuler une vision synthétique.


4. SORTIES ATTENDUES
--------------------
- V77F_CURVE_SHAPE.txt
- une description qualitative de la courbe Li_total($\beta_e$)
- une description qualitative de la surface Li_total($\gamma_{exch}, \gamma_{drain}$)
- une appréciation de la largeur de la zone bonne
- un commentaire sur l’existence ou non d’un point de bascule

Phrase de synthèse attendue :
> "La courbe Li_total présente / ne présente pas une pente nette avec un point de bascule, et la zone acceptable est large / moyenne / ultra-fine."


5. TRANSITION
-------------
- Si V77F conclut à une vraie pente avec un point de bascule et une zone acceptable non ultra-fine :
  → V78R pourra tenter un ancrage au réel (code BBN).
- Si V77F conclut à une zone ultra-fine ou à l’absence de bascule nette :
  → V78R devra être formulé avec prudence.

V77F ne produit pas de nouveaux nombres,
il produit une vision de la courbe que le modèle dessine.


## Résultat V77F
La lecture globale confirme une pente nette sans point de bascule interne marqué.

Courbe V77D :
- monotonie : décroissante
- courbure : convexe
- plage en beta_e : $[0.8, 1.2]$
- Li_total : de $3.763645\times 10^{-10}$ à $2.225423\times 10^{-10}$
- baisse relative : $40.87\%$
- points de passage dans le canal direct : 3
- lecture : descente douce et régulière, avec minimum au bord supérieur de la grille, pas de bascule interne nette.

Surface V77E :
- meilleur point de minimum absolu : $\gamma_{exch} = 0.75$, $\gamma_{drain} = 0.5$
- nombre de points où Li-7 et Li_total passent : 4
- largeur de zone : moyenne
- lecture : surface en bande, contrôlée par la vidange plutôt que par l’échange seul.

Vision synthétique :
- la courbe Li_total présente une pente nette sans point de bascule interne marqué ; la zone acceptable est moyenne, avec une surface en bande plutôt qu’un puits ultra-fin.
- Be-7 est vidé dans la zone utile, et l’équilibre A=7 est réellement renversé dans le proxy jouet.