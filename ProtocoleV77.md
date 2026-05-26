# V77 — RÉSOLUTION PHYSIQUE DU LITHIUM
# Version : 1.0 — Version propre
# Auteur : Jean-Philippe
# Objet : évaluer si la résolution lithium de V80B est robuste, stable et physiquement motivée

Protocole précédent : ProtocoleV76.md
Protocole suivant : V77B (si la résolution est jugée fine)

Wrapper global suggéré :
- python/scripts/runv77_li_physical_resolution.py

CONTENU :
- 0. Objectif
- 1. Entrées
- 2. Pipeline
- 3. Résultat de contrôle V80B
- 4. Sensibilité locale en delta_EM
- 5. Sensibilité nucléaire Li / Be
- 6. Analyse de cohérence physique
- 7. Verdict V77
- 8. Sorties attendues
- 9. Transition

0. OBJECTIF
-----------
Évaluer si la résolution du lithium observée en V80B est :
- robuste,
- stable,
- physiquement motivée,
- ou seulement un artefact du proxy BBN.

V77 tranche la tension laissée ouverte par V75B et raffinée en V76.


1. ENTRÉES
----------
- $\varepsilon_{best} = -0.0069$ fixe
- $\delta_{EM} = -0.0069$ fixe
- $k_G$, $k_T$, $k_n$ = valeurs calibrées de V83, fixes
- proxy BBN V80 inchangé


2. PIPELINE
-----------

1. Rejeu V80B
   - recalculer D/H, $Y_p$, Li-7/H, Be-7/H
   - vérifier que les valeurs sont identiques au point de référence V80B

2. Analyse de sensibilité $\delta_{EM}$
   - scanner $\delta_{EM}$ dans la micro-fenêtre $[-0.0072, -0.0066]$
   - tracer Li-7/H vs $\delta_{EM}$
   - vérifier si la résolution Li est stable ou ultra-fine

3. Analyse de sensibilité nucléaire
   - varier les taux Li / Be de $\pm 5\%$
   - recalculer Li-7/H et le canal total Li-7 + Be-7
   - vérifier si le lithium reste dans la fenêtre observationnelle

4. Analyse de cohérence physique
   - vérifier que la correction Li vient bien du canal EM
   - vérifier qu’elle ne dépend pas d’un artefact numérique
   - comparer la sélectivité de la réponse lithium à celle de D/H et $Y_p$

5. Verdict V77
   - "résolution robuste"
   - ou "résolution fine"
   - ou "tension persistante"


3. RÉSULTAT DE CONTRÔLE V80B
----------------------------
Le point de contrôle à $\delta_{EM} = -0.0069$ doit retrouver le même point que V80B.

Références attendues :
- D/H $\approx 2.530\times 10^{-5}$
- $Y_p \approx 0.2467$
- Li-7/H $\approx 1.566\times 10^{-10}$
- Be-7/H $\approx 1.329\times 10^{-10}$

Le contrôle sert à distinguer une vraie stabilité du simple bruit d’implémentation.


4. SENSIBILITÉ LOCALE EN DELTA_EM
---------------------------------
Le scan local autour du point fixe doit montrer :
- la largeur de bande où D/H, $Y_p$ et Li-7/H passent,
- la sensibilité relative de Li-7/H par rapport à D/H et $Y_p$.

Le critère qualitatif est simple :
- si Li-7/H reste passante sur une petite fenêtre avec un profil monotone, la correction est au moins fine,
- si elle dépend d’un réglage trop étroit, la correction est fragile.


5. SENSIBILITÉ NUCLÉAIRE
------------------------
On introduit des variations raisonnables sur les taux Li / Be, à hauteur de quelques pourcents.

Le diagnostic doit répondre à :
- Li-7/H reste-t-il dans la fenêtre observationnelle ?
- le canal total Li-7 + Be-7 reste-t-il cohérent ?
- la correction survit-elle à ces variations ?

Cette partie sert à distinguer une résolution physique d’un simple ajustement local du proxy.


6. ANALYSE DE COHÉRENCE PHYSIQUE
--------------------------------
La correction est jugée physiquement motivée si :
- elle est pilotée par le canal EM,
- elle sélectionne le lithium plus fortement que D/H ou $Y_p$,
- elle ne dépend pas d’une combinaison accidentelle de paramètres nucléaires.

À l’inverse, un résultat passable sur Li-7 mais cassé par le canal total ou par de petites variations de taux doit être considéré comme une résolution fine, pas comme une fermeture robuste.


7. VERDICT V77
--------------
Le lithium est classé dans l’un des trois cas suivants :

1. Résolution robuste :
- D/H et $Y_p$ OK,
- Li-7/H et le canal total dans la fenêtre observationnelle,
- résultat stable dans la micro-fenêtre de $\delta_{EM}$,
- résultat stable vis-à-vis des variations raisonnables des taux.

2. Résolution fine :
- Li-7/H OK dans la micro-fenêtre,
- mais le canal total ou les variations nucléaires montrent une fragilité,
→ à documenter comme une tension partiellement levée mais encore tuning-dépendante.

3. Tension persistante :
- le raffinement du proxy fait réapparaître un écart significatif,
→ il faut revoir le canal EM ou la structure du modèle.


8. SORTIES ATTENDUES
--------------------
- courbes Li-7/H vs $\delta_{EM}$,
- courbes D/H vs $\delta_{EM}$,
- courbes $Y_p$ vs $\delta_{EM}$,
- tableau de sensibilité nucléaire,
- diagnostic de cohérence physique,
- verdict final sur la tension lithium.


9. TRANSITION
-------------
- si robuste → V84 peut démarrer
- si fine → V77B peut préciser le canal EM
- si tension persistante → révision du modèle


## Résultat V77
Le diagnostic numérique autour de $\delta_{EM}=-0.0069$ confirme :
- contrôle V80B : `control_ok = true`
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
- la correction Li-7 est bien reproduite par le canal EM au point fixe, mais elle reste fragile dès qu’on réintroduit le canal total Li + Be.