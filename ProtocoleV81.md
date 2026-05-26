# V81 — LAGRANGIEN MINIMAL (DÉFORMATION D1 → OBSERVABLES D2/D3)

## Objectif
Construire un Lagrangien minimal L(ε) qui génère :
- delta_EM(ε) : déformation électromagnétique globale (BBN)
- pi_n(ε) : structuration neutronique, dépendante du milieu
- G_eff(ε) : gravité effective (projection D2 → D3)
- F_temps(ε) : facteur de temps local, comme dilatation émergente

Ce Lagrangien doit :
- reproduire la bande delta_EM issue de V80,
- rester compatible avec les contraintes labo (pi_n ≈ 0),
- produire les effets NS (pi_n ≈ 1),
- être le plus simple possible, selon un principe de parcimonie.

## Ancrage V80
La contrainte expérimentale issue de V80 est la suivante :
- delta_EM ∈ [-0.008, -0.0059]
- centre indicatif : delta_EM ≈ -0.00695
- meilleur ajustement proxy : delta_EM ≈ -0.0068

V81 doit donc choisir ε et les couplages de manière à reproduire cette fenêtre.

## Wrapper global suggéré
- python/scripts/runv81_lagrangian_scan.py

## Structure générale du Lagrangien
On introduit un champ scalaire géométrique φ(x), issu de la déformation D1.
La déformation globale est paramétrée par un unique paramètre ε.

L = L_kin + L_pot + L_couplages

où :

1) L_kin = (1/2) ∂_μ φ ∂^μ φ
   - dynamique minimale du champ de déformation.

2) L_pot = - (1/2) m_φ² φ² - (λ/4) φ⁴
   - potentiel simple permettant une amplitude contrôlée.

3) L_couplages =
      - α_EM φ F_{μν}F^{μν}
      - β_n φ (n̄ n)
      - γ_G φ R

avec :
- F_{μν}F^{μν} : terme électromagnétique,
- n̄ n : densité neutronique effective,
- R : scalaire de Ricci.

## Interprétation physique des couplages
1) Couplage EM : α_EM φ F²
   - génère delta_EM(ε)
   - impacte BBN via les réactions sensibles aux Q-values

2) Couplage neutronique : β_n φ (n̄ n)
   - génère pi_n(ε)
   - dépend du milieu : pi_n ≈ 0 en labo, pi_n ≈ 1 en étoile à neutrons

3) Couplage gravitationnel : γ_G φ R
   - modifie G_eff(ε)
   - effet amplifié en milieu neutronique

## Relations phénoménologiques à calibrer
On pose φ = ε φ₀, avec φ₀ une échelle de déformation de référence.

Alors :

delta_EM(ε) = k_EM ε
pi_n(ε) = k_n ε ρ_n / ρ_n^NS
G_eff(ε) = G (1 + k_G ε pi_n)
F_temps(ε) = 1 / (1 + k_T ε pi_n)

où :
- ρ_n : densité neutronique locale,
- ρ_n^NS : densité neutronique typique d’une étoile à neutrons,
- k_EM, k_n, k_G, k_T : constantes issues des couplages α_EM, β_n, γ_G.

## Paramètres libres
Paramètres fondamentaux :
- ε : amplitude de déformation D1, paramètre physique unique
- m_φ : masse du champ φ
- λ : auto-couplage
- α_EM, β_n, γ_G : couplages aux secteurs EM, neutronique et gravitationnel

Paramètres phénoménologiques dérivés :
- k_EM, k_n, k_G, k_T

## Contraintes à appliquer depuis V80
1) delta_EM(ε) doit appartenir à la bande BBN :
   - delta_EM ∈ [-0.008, -0.0059]

2) pi_n(ε) doit être :
   - ≈ 0 en labo, pour ne pas produire de variation de constantes mesurable
   - ≈ 1 en étoile à neutrons, pour activer les effets forts

3) G_eff(ε, pi_n = 0) ≈ G
   - la gravité locale doit rester inchangée

4) G_eff(ε, pi_n = 1) > G
   - la compacité des étoiles à neutrons doit augmenter

5) F_temps(ε, pi_n = 1) ≈ facteur GR
   - la dilatation du temps doit émerger correctement

## Résultat attendu de V81
Un Lagrangien minimal L(ε) qui :
- génère delta_EM(ε) compatible avec V80,
- produit pi_n(ε) cohérent avec les milieux,
- modifie G_eff(ε) comme observé dans les étoiles à neutrons,
- reproduit la dilatation du temps en régime fort,
- ne viole aucune contrainte labo.

Ce Lagrangien constitue la base de V82, qui fera la comparaison au réel.

## Résultat V81
Le scan V81 valide une bande ε commune :
- verdict : `lagrangian_band_confirmed`
- points acceptés : `14/51`
- bande ε acceptée : `[-0.0076, -0.0063]`
- valeur centrale : `ε_c = -0.00695`
- meilleur ajustement : `ε_best = -0.0069`

Chiffres au meilleur ajustement :
- `delta_EM = -0.0069`
- `pi_n_NS = 0.9928057554`
- `G_eff_NS = 1.0548028777 G`
- `F_temps_NS = 0.9605205330`

Lecture pratique :
- la fenêtre V80 est bien recopiée dans le Lagrangien minimal,
- le régime laboratoire reste quasi inactif,
- le régime neutronique active une correction gravitationnelle et temporelle nette sans casser l'ancrage BBN.

## Transition vers V82
V82 utilisera :
- delta_EM(ε) pour valider BBN,
- pi_n(ε) pour les milieux,
- G_eff(ε) pour la gravité locale et les étoiles à neutrons,
- F_temps(ε) pour le redshift et la dilatation du temps.

V82 confrontera ce modèle aux données réelles :
- BBN,
- laboratoire,
- système solaire,
- étoiles à neutrons,
- redshifts,
- relation masse-rayon,
- masse maximale.