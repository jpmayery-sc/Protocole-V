# V77C — AUTOPSIE DU CANAL A=7
# Version : 1.0 — Mode recherche
# Auteur : Jean-Philippe
# Objet : comprendre pourquoi Li_total reste verrouillé trop haut dans le proxy V80 / V77B

Protocole précédent : ProtocoleV77B.md
Protocole suivant : V78R (si un verrou structurel est identifié)

Wrapper global suggéré :
- python/scripts/runv77c_a7_autopsy.py

CONTENU :
- 0. Objectif
- 1. Hypothèses
- 2. Ce qu’on sait déjà
- 3. Questions de recherche
- 4. Pipeline V77C
- 5. Sorties attendues
- 6. Transition

0. OBJECTIF
-----------
Passer en mode recherche fondamentale sur le cœur BBN A=7.

V77C ne cherche pas à réparer le lithium, mais à :
- identifier la cause structurelle qui empêche Li_total de descendre,
- localiser le verrou dans le proxy A=7,
- préparer une éventuelle révision profonde du modèle (V78R).

V77C est une autopsie du moteur A=7, pas un pipeline de calibration.


1. HYPOTHÈSES
-------------
- On ne touche plus aux paramètres globaux :
  - $\varepsilon_{best} = -0.0069$
  - $\delta_{EM} = -0.0069$ (point de référence)
  - $k_G$, $k_T$, $k_n$ = valeurs V83
- On ne joue plus sur :
  - $\alpha_{Be}$
  - les variations de taux Li / Be
- On se concentre sur :
  - la structure interne du proxy BBN A=7,
  - les flux de production / destruction Li-7 / Be-7,
  - la façon dont Li_total est construit.


2. CE QU’ON SAIT DÉJÀ
---------------------
Issu de V77 et V77B :

- Li-7/H réagit bien à $\delta_{EM}$.
- Be-7/H réagit un peu, mais reste élevée.
- Li_total = Li-7/H + Be-7/H reste systématiquement trop haut.
- $\alpha_{Be}$ ne change pas qualitativement Li_total.
- $\pm 5\%$ sur les taux Li / Be ne suffisent pas à faire passer Li_total.
- 0/225 cas où Li_total passe dans V77B.

Conclusion :
- le problème n’est pas un réglage fin,
- le problème est structurel dans la façon dont le proxy A=7 est construit.


3. QUESTIONS DE RECHERCHE
-------------------------
V77C doit répondre à :

1) Comment le proxy V80 modélise-t-il exactement :
   - la production de Li-7,
   - la production de Be-7,
   - la destruction de Li-7,
   - la destruction de Be-7,
   - la construction de Li_total ?

2) Existe-t-il un verrou structurel :
   - corrélation trop forte Li-7 / Be-7,
   - normalisation interne A=7,
   - destruction A=7 absente ou mal modélisée,
   - compression des canaux dans un terme effectif trop rigide ?

3) Quel canal, s’il est coupé ou modifié artificiellement, fait enfin descendre Li_total ?


4. PIPELINE V77C
----------------

4.1 Extraction de la structure A=7
---------------------------------
Objectif : rendre explicite ce qui est implicite dans le code.

Actions :
- Documenter les règles utilisées pour :
  - Li-7 production,
  - Be-7 production,
  - Li_total.
- Si le proxy n’a pas de destruction explicite, le signaler comme fait structurel.

Sortie :
- un dump textuel V77C_A7_STRUCTURE.txt.


4.2 Flux internes pour $\delta_{EM} = 0$ et $\delta_{EM} = -0.0069$
-----------------------------------------------------------------
Objectif : voir qui domine dans le budget A=7.

Actions :
- Pour $\delta_{EM} = 0$ : calculer Li-7, Be-7, Li_total.
- Pour $\delta_{EM} = -0.0069$ : refaire la même chose.
- Comparer les variations relatives.

Sortie :
- V77C_A7_FLUXES.txt.


4.3 Chirurgie numérique : coupure de canaux
-------------------------------------------
Objectif : identifier le canal qui verrouille Li_total.

Actions artificielles :
- couper la production Be-7,
- couper la production Li-7,
- couper le canal A=7 total,
- comparer Li_total.

But :
- si couper un canal fait descendre Li_total, ce canal est un candidat verrou,
- si rien ne change vraiment, le verrou est dans la structure globale ou la somme elle-même.

Sortie :
- V77C_A7_SURGERY.txt.


4.4 Recherche de normalisation / saturation interne A=7
-------------------------------------------------------
Objectif : vérifier si le proxy impose implicitement un plateau A=7.

Actions :
- Inspecter le code pour :
  - facteurs de normalisation spécifiques à A=7,
  - saturations numériques,
  - contraintes du type A=7 fixé par une fraction constante.
- Tester un cas où Li_total est autorisé à descendre librement.

Sortie :
- V77C_A7_NORMALISATION.txt.


4.5 Comparaison qualitative avec un schéma BBN standard
-------------------------------------------------------
Objectif : vérifier si le proxy A=7 est qualitativement cohérent.

Actions :
- comparer la hiérarchie qualitative avec la littérature BBN,
- vérifier si le proxy respecte une logique A=7 réaliste ou s’il compresse trop les canaux.

Sortie :
- V77C_A7_COMPARISON.txt.


5. SORTIES ATTENDUES
--------------------
V77C doit produire au minimum :
- V77C_A7_STRUCTURE.txt
- V77C_A7_FLUXES.txt
- V77C_A7_SURGERY.txt
- V77C_A7_NORMALISATION.txt
- V77C_A7_COMPARISON.txt

Et surtout :
- une phrase claire du testeur sur le verrou structurel qui empêche Li_total de descendre.


6. TRANSITION
-------------
- Si V77C identifie clairement un verrou :
  → V78R pourra proposer une refonte ciblée du proxy A=7.
- Si V77C ne trouve pas de verrou clair :
  → il faudra envisager que le proxy V80 est trop simplifié pour traiter A=7.

V77C est un protocole de recherche, pas de validation.
Il doit éclairer où le modèle pêche, pas le sauver.


## Résultat V77C
L’autopsie numérique confirme un verrou structurel clair :
- le proxy A=7 est l’addition de deux canaux positifs,
- il n’existe aucun canal de destruction explicite,
- il n’existe aucune saturation ni normalisation cachée qui puisse faire tomber Li_total,
- Be-7 reste la branche dure qui fixe le plancher de Li_total.

Chiffres de référence :
- à $\delta_{EM} = 0$ : Li7/H = $5.240000\times 10^{-10}$, Be7/H = $4.150000\times 10^{-10}$, Li_total/H = $9.390000\times 10^{-10}$
- à $\delta_{EM} = -0.0069$ : Li7/H = $1.566465\times 10^{-10}$, Be7/H = $1.329241\times 10^{-10}$, Li_total/H = $2.895706\times 10^{-10}$

Chirurgie numérique :
- couper la production Be-7 donne Li_total/H = $1.566465\times 10^{-10}$
- couper la production Li-7 donne Li_total/H = $1.329241\times 10^{-10}$
- couper tout le canal A=7 donne Li_total/H = $0$

Diagnostic structurel :
- aucun facteur de normalisation A=7 caché n’a été trouvé,
- aucun clamp numérique n’a été trouvé,
- le verrou est bien l’addition de deux branches positives sans canal compensateur.

Phrase de synthèse :
- le verrou structurel est l’addition de deux canaux positifs sans destruction explicite ; Li7 et Be7 décroissent avec $\delta_{EM}$, mais leur somme reste pilotée par la branche Be7, et le proxy ne contient ni canal compensateur ni saturation interne pour faire tomber Li_total.

Fichiers produits :
- V77C_A7_STRUCTURE.txt
- V77C_A7_FLUXES.txt
- V77C_A7_SURGERY.txt
- V77C_A7_NORMALISATION.txt
- V77C_A7_COMPARISON.txt