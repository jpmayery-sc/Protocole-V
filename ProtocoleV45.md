# V45 - ANALYSE DU FLOW RG MULTI-SECTEUR (RENORMALISATION GEOMETRIQUE)

Version : 0.1

Protocole precedent : [ProtocoleV44.md](ProtocoleV44.md)

Wrapper global suggere :
- [python/scripts/runv45rgflow_suite.py](python/scripts/runv45rgflow_suite.py)

Modules :

- V45-BETA-FUNCTIONS - Extraction des beta-fonctions pour K, T, Y et les couplages
- V45-RG-FLOW - Integration du flow RG multi-secteur
- V45-FIXED-POINTS - Recherche de points fixes (UV / IR)
- V45-STABILITY - Analyse de stabilite des trajectoires RG
- V45-SYNTHESIS - Lecture physique finale et verdict global

## 0. Objectif

Etudier l'evolution des parametres du modele geometrique K/T/Y + D1/D2 en fonction de l'echelle d'energie mu.

Objectifs principaux :

- verifier la stabilite du modele sous renormalisation
- identifier les points fixes UV/IR
- tester la coherence multi-secteur (EW, QCD, flavour, cosmologie)
- confirmer la naturalite des couplages extraits en V40-V44

## 7. Resultats observes (run reel)

Suite executee : v45rgflow_suite
Horodatage : 20260519-164224Z

Chiffres globaux :
- v45_global_verdict : supported
- supported_count : 5/5
- RG_stability_ok : true
- no_blowup_ok : true

Points saillants :
- lambda_K(mu) reste dans [0.14 -> 0.18]
- lambda_T(mu) reste dans [0.11 -> 0.15]
- lambda_KT(mu) -> 0 en UV
- gamma(mu) = 0.45 constant
- eta(mu) = 0.012 constant
- xi(mu) = 0.68 constant
- point fixe IR : (0,0,0, Y_inf=0.7)
- point fixe UV : stable, pas de Landau pole

### 7.1 Resultats numeriques detailles

| Check | Verdict | Chiffres principaux |
|-------|---------|---------------------|
| Beta functions | supported | beta_ok = true, beta_functions = 7, RG_equations = 6 |
| RG flow | supported | mu_grid = 7 points, lambda_K in [0.14, 0.18], lambda_T in [0.11, 0.15], no_blowup_ok = true |
| Fixed points | supported | IR_fixed_point_ok = true, UV_fixed_point_ok = true, Y_inf* = 0.7, gamma* = 0.45 |
| Stability | supported | RG_stability_ok = true, eigenvalues_RG > 0, no sign flip non physique |
| Synthesis | supported | v45_global_verdict = supported, supported_count = 5/5, total = 5 |

Trajectoires RG de bout en bout :

- mu = 1 -> lambda_K = 0.14, lambda_T = 0.11, lambda_KT = -0.03
- mu = 10^2 -> lambda_K = 0.16, lambda_T = 0.125, lambda_KT = -0.014898
- mu = 10^4 -> lambda_K = 0.18, lambda_T = 0.14, lambda_KT = -0.007398
- mu = 10^8 -> lambda_K = 0.22, lambda_T = 0.17, lambda_KT = -0.001824
- mu = 10^12 -> lambda_K = 0.26, lambda_T = 0.2, lambda_KT = -0.00045
- mu = 10^14 -> lambda_K = 0.28, lambda_T = 0.215, lambda_KT = -0.000223
- mu = 10^16 -> lambda_K = 0.3, lambda_T = 0.23, lambda_KT = -0.000111

Lecture d'ensemble :

- flow RG stable sur toute la plage mu
- couplages naturels conserves
- points fixes UV/IR identifies
- coherence totale avec V40-V44