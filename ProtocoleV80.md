# V80 — MODÈLE BBN (VERSION « MÉCANISME FIXÉ »)

## Objectif
- Figer le mécanisme D1/D2/D3 côté BBN uniquement.
- Déterminer une bande numérique propre pour delta_EM compatible avec les abondances primordiales.
- Produire des sorties claires pour un testeur externe, reproductibles, lisibles et sans spéculation.

## Hypothèses de travail
- delta_EM : petite déformation électromagnétique globale issue de D1.
- pi_n : paramètre de structuration neutronique, mais en BBN le milieu est peu neutronique, donc pi_n ≈ pi_n_BBN fixé.
- G_eff, facteur de temps, etc. ne sont pas encore utilisés dans les équations BBN. On reste proche du formalisme standard, seule delta_EM agit sur les taux EM pertinents.
- On ne touche pas à la structure du code BBN de base, on ajoute une couche delta_EM.

## Wrapper global suggéré
- python/scripts/runv80_bbn_scan.py

## Entrées principales
- Plage de delta_EM à scanner : [delta_EM_min, delta_EM_max] (par exemple de -2 % à -0.1 %).
- Paramètres cosmologiques standards (η_b, N_eff, etc.) fixés à leurs valeurs usuelles.
- pi_n_BBN fixé, avec une valeur raisonnable ou neutre documentée dans le texte.

## Pipeline V80
1. Initialisation
   - Définir la plage delta_EM.
   - Charger ou initialiser le code BBN standard, ou son équivalent jouet.
   - Documenter clairement les constantes utilisées.

2. Implémentation de delta_EM
   - Introduire delta_EM comme correction sur les termes EM pertinents, par exemple masses effectives, Q-values, taux de réaction sensibles.
   - Garder une trace explicite de l’endroit où delta_EM intervient, avec des commentaires clairs.

3. Scan de delta_EM
   - Boucler sur la plage delta_EM.
   - Pour chaque valeur :
     - lancer le calcul BBN,
     - extraire les abondances finales : D/H, He-4, Li-7, éventuellement Be-7.
   - Stocker les résultats dans des tableaux structurés.

4. Critères de sélection
   - Définir des fenêtres d’acceptation pour :
     - D/H, avec barres d’erreur observationnelles,
     - Y_p (He-4),
     - Li-7, avec l’objectif de soulager le problème du lithium,
     - Be-7 si suivi.
   - Marquer les delta_EM acceptables, sous forme de booléen ou de masque.

5. Résultats et visualisation
   - Tracer :
     - D/H vs delta_EM,
     - Y_p vs delta_EM,
     - Li-7 vs delta_EM,
     - Be-7 vs delta_EM si nécessaire.
   - Mettre en évidence la bande de delta_EM qui satisfait tous les critères.
   - Afficher en texte :
     - delta_EM_min_acceptable,
     - delta_EM_max_acceptable,
     - valeur(s) centrale(s) possible(s).

6. Résumé pour le testeur
   - Bloc texte en fin de notebook :
     - rappel des hypothèses,
     - plage scannée,
     - bande delta_EM compatible avec les données BBN,
     - limitations : pas encore de Lagrangien, pas encore de couplage explicite à G_eff, etc.
   - Mention explicite : v80 = BBN only, mécanisme paramétré par delta_EM, sans Lagrangien.

## Sorties attendues
- Une bande numérique claire pour delta_EM, par exemple delta_EM ∈ [a, b].
- Des graphiques propres, lisibles, avec légendes explicites.
- Un résumé textuel réutilisable tel quel dans v81 pour la construction du Lagrangien.

## Transition vers v81
- v81 introduit un paramètre de déformation ε de D1 et formalise le Lagrangien minimal correspondant dans [ProtocoleV81.md](ProtocoleV81.md).
- Objectif v81 : trouver un Lagrangien minimal qui reproduit delta_EM(ε), puis pi_n(ε) et G_eff(ε).
- v80 sert de référence expérimentale BBN et fournit la bande delta_EM ∈ [-0.008, -0.0059] qui contraint ε.