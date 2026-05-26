# V77M — RE-VALIDATION PHYSIQUE + LECTURE INTERPRÉTATIVE
# Version : 1.0 — Mode synthèse, “est-ce que ça tient vraiment ?”
# Auteur : Jean-Philippe
# Objet : relancer la validation avec leviers physiques actifs (type V78H’)
#         ET produire une première lecture interprétative (type V79X),
#         pour décider si on passe à un schéma généralisé / V80.

Protocole précédent : V77L (implémentation physique des leviers)
Protocole suivant : V80 (si validation robuste) ou V79BIS (si blocage)

Wrapper global suggéré :
- python/scripts/runv77m_validation_plus_readout.py

CONTENU :
- 0. Objectif
- 1. Partie A — Re-validation physique (type V78H’)
- 2. Partie B — Lecture interprétative (type V79X)
- 3. Pipeline V77M
- 4. Sorties attendues
- 5. Critères de décision (V80 ou pas)
- 6. Transition

0. OBJECTIF
-----------
V77M fait deux choses en une passe :

- **A. Re-valider** la géométrie de courbe A=7 dans le code BBN réel,
  avec les leviers physiques actifs (beta_e_phys, gamma_exch_phys, gamma_drain_phys),
  en testant D/H, Y_p, Li7/H, Li_total/H sur une grille réaliste.

- **B. Lire** ce que ces résultats disent physiquement :
  - quels mécanismes semblent vraiment jouer,
  - si le renversement A=7 est robuste ou ultra-fin,
  - si ça vaut le coup de passer à un V80 “généralisation”.

V77M = “est-ce que le moteur physique tient debout, et qu’est-ce qu’il raconte ?”


1. PARTIE A — RE-VALIDATION PHYSIQUE (TYPE V78H’)
-------------------------------------------------
1.1 Grille de paramètres
------------------------
- beta_e_phys ∈ [beta_min, beta_max] (par ex. [0.8, 1.2], 5–7 points),
- gamma_exch_phys ∈ [0, gamma_exch_max] (par ex. [0, 1.0], 5 points),
- gamma_drain_phys ∈ [0, gamma_drain_max] (par ex. [0, 0.5], 5 points).

1.2 Runs BBN
------------
Pour chaque triplet (beta_e_phys, gamma_exch_phys, gamma_drain_phys) :

- lancer le code BBN réel (avec V77L actif),
- récupérer :
  - D/H, Y_p,
  - Li7/H, Be7/H, Li_total/H.

1.3 Filtrage
------------
- définir les fenêtres observationnelles (D/H_obs, Y_p_obs, Li7/H_obs, Li_total/H_obs),
- calculer chi_D, chi_Y, chi_Li7 (et éventuellement chi_Litot),
- marquer les points ACCEPTÉS si :
  - |chi_D| ≤ chi_max_D,
  - |chi_Y| ≤ chi_max_Y,
  - Li7/H et Li_total/H dans une plage raisonnable.

1.4 Géométrie de courbe
-----------------------
- reconstruire :
  - Li_total(beta_e_phys) pour quelques (gamma_exch_phys, gamma_drain_phys) fixés,
  - Li_total(gamma_exch_phys, gamma_drain_phys) pour un beta_e_phys fixé,
- comparer qualitativement à V77G :
  - pente nette ou non,
  - bande de passage ou point ultra-fin,
  - existence d’une zone où A=7 est réellement renversé.


2. PARTIE B — LECTURE INTERPRÉTATIVE (TYPE V79X)
------------------------------------------------
2.1 Questions physiques
-----------------------
À partir des points ACCEPTÉS, V77M doit répondre qualitativement à :

1) **Levier électronique :**
   - beta_e_phys doit-il être proche de 1, >1, <1 ?
   - l’écrantage / capture e– doit-il être fortement modifié ou seulement légèrement ?
   - y a-t-il une tension avec d’autres contraintes (plasma, CMB, etc.) ?

2) **Destruction A=7 :**
   - gamma_drain_phys doit-il être grand ou modéré ?
   - quels canaux semblent dominants (Li7(p,α), Be7(n,p), Be7(d,p)) ?
   - est-ce compatible avec les incertitudes nucléaires connues ?

3) **Échanges Be7 ↔ Li7 :**
   - gamma_exch_phys doit-il être non nul pour que ça marche ?
   - la redistribution Be7 → Li7 est-elle cruciale ou secondaire ?

4) **Robustesse :**
   - la zone acceptable est-elle :
     - large (robuste),
     - moyenne (réglage fin raisonnable),
     - ultra-fine (tuning violent) ?
   - le renversement A=7 est-il un effet structurel ou un accident de paramètre ?

2.2 Synthèse physique
---------------------
V77M doit produire un texte de lecture :

- ce que le modèle semble dire sur :
  - le rôle réel de l’électron,
  - la flexibilité des canaux de destruction A=7,
  - la possibilité d’un renversement A=7 sans casser D/H et Y_p,
- et si cela ressemble à :
  - un mécanisme plausible,
  - ou un tuning difficilement défendable.


3. PIPELINE V77M
----------------

3.1 Exécution
-------------
- Charger la config V77L (code BBN patché),
- définir la grille de paramètres,
- lancer tous les runs,
- stocker les résultats dans un DataFrame.

3.2 Analyse
-----------
- appliquer le filtrage observationnel,
- compter les points ACCEPTÉS,
- identifier :
  - le meilleur point (chi^2 minimal),
  - la largeur de la zone acceptable,
- reconstruire les courbes / surfaces Li_total.

3.3 Lecture
-----------
- générer :
  - un résumé chiffré,
  - une lecture qualitative (Partie B),
  - une phrase de synthèse décisionnelle (V80 ou pas).


4. SORTIES ATTENDUES
--------------------
- v77m_results_full.csv :
  - tous les points de la grille,
  - avec D/H, Y_p, Li7/H, Be7/H, Li_total/H, chi_D, chi_Y, flags.

- v77m_results_accepted.csv :
  - sous-ensemble des points ACCEPTÉS.

- Figures :
  - v77m_Litot_vs_beta_e_phys.png,
  - v77m_Litot_surface_gamma_phys.png,
  - éventuellement v77m_DH_vs_param.png.

- V77M_PHYS_READOUT.txt :
  - résumé chiffré,
  - lecture interprétative,
  - recommandation : “V80 recommandé / V80 non recommandé”.

- Optionnel :
  - v77m_analysis.ipynb (notebook récapitulatif).


5. CRITÈRES DE DÉCISION (V80 OU PAS)
------------------------------------
V77M doit conclure sur :

1) **Si V80 est justifié :**
   - il existe une bande de paramètres (non ultra-fine),
   - D/H, Y_p, Li7/H, Li_total/H sont compatibles,
   - la géométrie de courbe ressemble à V77G,
   - les valeurs de beta_e_phys, gamma_exch_phys, gamma_drain_phys restent plausibles.

2) **Si V80 ne l’est pas :**
   - soit aucune zone acceptable n’existe,
   - soit la zone est ultra-fine,
   - soit les paramètres requis sont physiquement déraisonnables.

Phrase de sortie typique :

> “V77M conclut que le passage à V80 (généralisation) est / n’est pas justifié,
> car la bande de paramètres physiques compatible avec les données est
> large / moyenne / ultra-fine, et le renversement A=7 est
> robuste / fragile / absent.”


6. TRANSITION
-------------
- Si V77M conclut “V80 recommandé” :
  → V80 pourra généraliser le schéma (autres noyaux, autres constantes, etc.).

- Si V77M conclut “V80 non recommandé” :
  → on pourra soit affiner le moteur (V79BIS),
    soit conclure à une rigidité forte du secteur A=7.

V77M est ton **checkpoint sérieux** :
c’est là que tu regardes froidement si ton idée tient face au réel,
ou si elle reste confinée au jouet.

RÉSULTAT CHIFFRÉ — RE-VALIDATION + READOUT
-----------------------------------------
Date du run : 20260521-151611Z
Mode : dry-run adapter via V77L, faute de tree externe AlterBBN/PArthENoPE dans le workspace

Synthèse numérique :

- verdict : recommended_for_v80
- accepted_count : 47/125
- best_fit_beta_e_phys : 1.1
- best_fit_gamma_exch_phys : 0.5
- best_fit_gamma_drain_phys : 0.25
- curve_reading : courbe croissante à courbure mixte
- surface_reading : surface en bande avec zone de passage de largeur moyenne
- recommendation : V80 recommandé

Lecture qualitative courte :
- beta_e_phys agit de manière visible mais modérée.
- gamma_exch_phys participe à la redistribution A=7.
- gamma_drain_phys concentre la réduction de Li_total.
- la zone acceptable n’est pas ultra-fine dans ce run sec.

Lecture physique plus directe :
- Le point optimal à beta_e_phys=1.1 indique que le levier électronique n’agit pas comme un simple détail de calibration: il pousse le système vers une chimie A=7 plus favorable, mais sans casser les observables légers. Le fait que D/H reste proche de l’observation et que Y_p bouge peu suggère une action locale sur la branche A=7 plutôt qu’une déformation globale du réseau BBN.
- Le maximum autour de gamma_exch_phys=0.5 montre que l’échange Be7 ↔ Li7 n’est pas décoratif. Dans ce run, il aide à redistribuer la matière vers la branche lithium tout en gardant une bande acceptable. Physiquement, cela ressemble à un mécanisme de transfert plutôt qu’à une destruction franche.
- Le meilleur point à gamma_drain_phys=0.25 plutôt qu’à une valeur extrême signifie que la réduction de Li_total n’exige pas un écrasement violent des canaux A=7. On est plutôt dans un régime de correction modérée, compatible avec une bande de passage de largeur moyenne.
- Le verdict V80 recommandé est donc structurellement important: dans l’adapter V77L, le renversement A=7 n’apparaît pas comme un accident ultra-fin. Il existe une zone continue de paramètres qui maintient D/H et Y_p dans les clous tout en déplaçant Li_total dans le bon sens.
- Limite importante: ce résultat prouve la cohérence du moteur physique dans le cadre V77L, pas encore la validité d’un patch réel sur AlterBBN/PArthENoPE. La lecture physique est donc “mécanisme plausible dans l’adapter”, pas “preuve finale du code réel”.

Fichiers générés :

- results/result-analyse/v77m_validation_plus_readout/v77m_results_full.csv
- results/result-analyse/v77m_validation_plus_readout/v77m_results_accepted.csv
- results/result-analyse/v77m_validation_plus_readout/V77M_PHYS_READOUT.txt
- results/result-analyse/v77m_validation_plus_readout/v77m_validation_plus_readout_summary_20260521-151611Z.json
- results/result-analyse/v77m_validation_plus_readout/plots/v77m_Litot_vs_beta_e_phys.png
- results/result-analyse/v77m_validation_plus_readout/plots/v77m_Litot_surface_gamma_phys.png
- results/result-analyse/v77m_validation_plus_readout/plots/v77m_DH_vs_param.png

ANNEXE — BRANCHEMENT ALTERBBN / PArthENoPE
-----------------------------------------

Pour passer de l’adapter V77L à un code BBN réel, V77M doit reposer sur un
adaptateur unique avec deux backends possibles : AlterBBN ou PArthENoPE.

1) Contrat de l’adaptateur
- Entrée : beta_e_phys, gamma_exch_phys, gamma_drain_phys, config_cosmo.
- Sortie : D/H, Y_p, Li7/H, Be7/H, Li_total/H, plus un log d’exécution.
- Le wrapper Python ne doit pas appeler directement la physique interne du code.
  Il doit écrire les fichiers d’entrée, lancer le binaire, puis parser la sortie.

2) Backend AlterBBN
- Source du projet : code C compilé avec Makefile.
- Mode attendu : un exécutable ou un dossier d’input/output avec param_file.dat
  et cosmo_file.dat si le fork le demande.
- Sortie à lire : fichier d’abondances ou stdout selon le fork.
- Adaptation V77M : le wrapper écrit les paramètres physiques dans les fichiers
  d’entrée et mappe les abondances de sortie vers les colonnes attendues.

Format AlterBBN concret retenu pour V77M :

- param_file.dat
  - `eta=<eta>` en première ligne, avec une valeur par défaut `6.137e-10`
    si aucun eta cosmologique n’est fourni.
  - `beta_e_phys=<value>`
  - `gamma_exch_phys=<value>`
  - `gamma_drain_phys=<value>`
  - `cosmo_<key>=<value>` pour toute clé scalaire additionnelle.

- cosmo_file.dat
  - tableau texte à colonnes `t T dTdt Tnu H nb_etaf`
  - une ligne par point cosmologique
  - si aucune table n’est fournie, le backend écrit un fallback lisible en
    commentaire pour signaler qu’il faut fournir `config_cosmo['cosmo_table']`.

- sortie attendue
  - `abundance_file.dat` avec des lignes clé=valeur, ou un stdout redirigé vers
    un fichier équivalent selon le fork local.

Cela fixe le contrat minimal de branchement pour V77M: AlterBBN lit un param_file
et une table cosmologique, puis renvoie un fichier d’abondances standardisé.

3) Backend PArthENoPE
- Même principe fonctionnel : exécutable externe + fichiers d’entrée/sortie.
- Le format exact des fichiers doit être celui de la version locale disponible.
- Si le fork impose un format propriétaire, l’adaptateur doit encapsuler ce
  format sans le propager à V77M.

Format PArthENoPE concret retenu pour V77M :

- `parthenope_input.json`
  - charge utile JSON avec `beta_e_phys`, `gamma_exch_phys`, `gamma_drain_phys`
    et `config_cosmo`
  - sert de contrat stable côté wrapper Python

- `parthenope_driver.ini`
  - fichier pont au format `key=value`
  - contient les trois leviers physiques et toute clé cosmologique scalaire
  - permet au backend local de lire les entrées sans dépendre du JSON interne

- sortie attendue
  - `abundance_file.dat` ou `results.json` selon le fork local
  - l’adaptateur convertit ensuite les champs vers D/H, Y_p, Li7/H, Be7/H,
    Li_total/H

Ce contrat ne prétend pas imposer le vrai format historique de PArthENoPE ; il
définit le pont minimal que V77M peut utiliser proprement dans un workspace local.

4) Structure Python recommandée
- backend = "alterbbn" | "parthenope"
- executable_path = chemin du binaire
- input_dir = dossier de travail temporaire
- output_dir = dossier de sortie
- runner.write_inputs(...)
- runner.run()
- runner.read_outputs()
- squelette concret du contrat : python/scripts/bbn_backend_adapter.py

5) Points de validation
- Vérifier que le point standard (1, 0, 0) reproduit les abondances du code
  branché.
- Vérifier qu’un changement de beta_e_phys, gamma_exch_phys ou gamma_drain_phys
  modifie réellement Li7/H, Be7/H et Li_total/H.
- Vérifier que D/H et Y_p restent stables pour de petites variations.

6) Décision d’intégration
- Si le backend réel est AlterBBN : garder le même contrat et seulement adapter
  les noms de fichiers, les variables et le parseur.
- Si le backend réel est PArthENoPE : conserver le même contrat, mais fournir un
  parseur dédié au format de sortie du code local.

En pratique, V77M ne doit pas parler directement au code BBN réel.
Il doit parler à un adaptateur stable, et cet adaptateur doit être la seule
couche qui connaît AlterBBN ou PArthENoPE.

RÉSULTAT CHIFFRÉ — BRANCHEMENT PArthENoPE
----------------------------------------
Date du jalon : 20260521-151611Z
État : contrat PArthENoPE documenté dans l’adaptateur et dans V77M

Livrables ajoutés :

- python/scripts/bbn_backend_adapter.py
  - contrat `PARTHENOPE_INPUT_CONTRACT`
  - écriture de `parthenope_input.json`
  - écriture de `parthenope_driver.ini`

- ProtocoleV77M.md
  - bloc de branchement PArthENoPE ajouté

Validation :

- compilation Python toujours propre sur le backend adapter
- le protocole contient désormais le contrat de pont PArthENoPE

Lecture opérationnelle :

- V77M sait désormais quoi écrire pour un backend AlterBBN local et quoi écrire
  pour un backend PArthENoPE local.
- La différence entre les deux backends est circonscrite au niveau de l’adaptateur
  ; le reste du pipeline V77M reste inchangé.

EXEMPLE CONCRET DE CONFIG_COSMO
-------------------------------

Pour tester le branchement sans lancer de code réel, V77M peut utiliser la
configuration cosmologique minimale suivante :

```python
{
    "eta": 6.137e-10,
    "Tnu_over_T": 0.714,
    "cosmo_table": [
        {"t": 1.0e-2, "T": 3.0, "dTdt": -1.0e2, "Tnu": 3.0, "H": 1.0e2, "nb_etaf": 1.0e-10},
        {"t": 1.0e0, "T": 1.0, "dTdt": -1.0e0, "Tnu": 1.0, "H": 1.0e0, "nb_etaf": 1.0e-12},
        {"t": 1.0e2, "T": 1.0e-1, "dTdt": -1.0e-3, "Tnu": 1.0e-1, "H": 1.0e-2, "nb_etaf": 1.0e-14},
    ],
}
```

Lecture de l’exemple :

- `eta` sert de valeur baryonique de base pour AlterBBN.
- `Tnu_over_T` est une clé scalaire libre, utile pour un fork local qui veut
  conserver une information globale sur le découplage des neutrinos.
- `cosmo_table` fournit trois points symboliques, suffisants pour valider le
  format d’écriture du `cosmo_file.dat` sans imposer une table complète.

Le même dictionnaire peut être passé à `run_v77m_validation_plus_readout(...,
backend="alterbbn", executable_path="...", backend_work_dir="...")` ou au
backend PArthENoPE équivalent, uniquement pour tester l’écriture des fichiers
avant d’exécuter un binaire réel.

RÉSULTAT CHIFFRÉ — SÉLECTEUR DE BACKEND V77M
-------------------------------------------
Date du jalon : 20260521-151611Z
État : validateur V77M paramétrable par backend, avec secours V77L par défaut

Ajout réalisé :

- python/scripts/runv77m_validation_plus_readout.py
  - options `--backend`, `--executable-path`, `--backend-work-dir`
  - prise en charge d’un backend réel via `bbn_backend_adapter.py`
  - maintien du mode dry-run V77L lorsque aucun backend n’est fourni

Lecture opérationnelle :

- si `--backend` est omis, V77M reste en mode adapter V77L.
- si `--backend alterbbn` ou `--backend parthenope` est fourni avec un
  exécutable valide, V77M bascule sur le backend réel sans changer le contrat
  d’analyse ni le format des sorties.
- le protocole est donc prêt pour l’intégration réelle, tout en conservant un
  comportement sûr quand aucun code BBN externe n’est disponible.

RÉSULTAT CHIFFRÉ — BRANCHEMENT BACKEND BBN
-----------------------------------------
Date du jalon : 20260521-151611Z
État : squelette d’adaptateur prêt, backend réel non branché dans ce workspace

Livrables produits :

- python/scripts/bbn_backend_adapter.py
  - contrat commun `BBNBackendAdapter`
  - adaptateurs `AlterBBNBackendAdapter` et `ParthenopeBackendAdapter`
  - cycle `write_inputs -> run -> parse_outputs`
  - normalisation des sorties vers D/H, Y_p, Li7/H, Be7/H, Li_total/H

- ProtocoleV77M.md
  - annexe de branchement ajoutée avec le contrat d’intégration

Validation :

- compilation Python réussie sur le module de backend
- aucune erreur de syntaxe signalée
- le protocole référence explicitement le squelette de backend

Interprétation :

- V77M dispose maintenant d’une couche d’abstraction unique pour brancher un
  code BBN réel.
- Le point restant n’est plus l’architecture, mais la présence effective d’un
  exécutable AlterBBN ou PArthENoPE local à pointer dans `executable_path`.
- Tant que ce binaire n’est pas disponible, V77M reste en mode adaptateur prêt à
  brancher, sans prétendre lancer un code externe absent du workspace.