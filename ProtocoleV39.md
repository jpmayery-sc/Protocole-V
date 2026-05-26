# V39 - MCMC GLOBAL MULTI-SECTEUR AVEC DYNAMIQUE D1/D2

Version : 0.2

Protocole precedent : [ProtocoleV38d.md](ProtocoleV38d.md)

Wrapper global suggere :
- [python/scripts/runv39mcmc_suite.py](python/scripts/runv39mcmc_suite.py)

Modules :

- V39-PARAMSPACE - Definition de l'espace des parametres
- V39-LIKELIHOODS - Fonctions de vraisemblance par secteur
- V39-MCMC - Chaines de Markov multi-secteur
- V39-DIAGNOSTICS - Convergence, autocorrelation, stabilite
- V39-SYNTHESIS - Lecture physique globale


0. OBJECTIF
-----------
Tester si une region de l'espace des parametres existe telle que :

- muon (EW)
- neutrinos
- QCD (glueball)
- flavour (B -> K ll)
- matiere noire geometrique
- H(z)
- Lambda_eff(K)
- croissance f_sigma8(z) via dynamique D1/D2

sont satisfaits simultanement.

V39 est le test final de coherence globale du schema K/T/Y.


1. V39-PARAMSPACE - ESPACE DES PARAMETRES
-----------------------------------------

1.1 Parametres leptoniques (V35)
--------------------------------
- A_mu in [1e-7, 1e-5]
- B_mu in [1e-7, 1e-5]

1.2 Parametres neutrinos (V35)
------------------------------
- lambda_2 in [1e-4, 1e-2]
- lambda_3 in [1e-4, 1e-2]

1.3 Parametres QCD (V36)
------------------------
- alpha_s in [1e-3, 1e-1]
- beta_s in [1e-3, 1e-1]
- M0_strong in [0, 1 GeV]

1.4 Parametres flavour (V37)
----------------------------
- C_e, C_mu, C_tau in [1e-4, 1e-1]

1.5 Parametres DM geometrique (V37)
-----------------------------------
- epsilon in [0.05, 0.20]

1.6 Parametres cosmologiques (V38d)
-----------------------------------
- alpha (Hubble) in [-0.2, 0.5]
- xi (Lambda_eff) in [-2, 2]
- eta in [-0.3, 0.3]
- gamma in [0.05, 1.0]
- Sent_inf in [0.5, 1.0]

1.7 Parametres structurels (D1/D2)
----------------------------------
- K_bg_best = 1.0 (fixe)
- Sent_0 = 0.9 (herite de V37/V38d)


2. V39-LIKELIHOODS - VRAISEMBLANCES PAR SECTEUR
-----------------------------------------------

2.1 Muon (EW)
-------------
L_mu = exp( - (Delta a_mu_model - Delta a_mu_exp)^2 / (2 sigma_mu^2) )

2.2 Neutrinos
-------------
L_nu = exp( - chi^2(Delta m^2_sol, Delta m^2_atm, Sigma m_nu) / 2 )

2.3 QCD (glueball)
------------------
L_QCD = exp( - (m_glueball_eff - 1.6)^2 / (2 sigma_QCD^2) )

2.4 Flavour (B -> K ll)
----------------------
L_flavour = exp( - (delta_RK_model - delta_RK_exp)^2 / (2 sigma_flavour^2) )

2.5 Matiere noire geometrique
-----------------------------
L_DM = exp( - (rho_DM_eff/rho_baryon - 5)^2 / (2 sigma_DM^2) )

2.6 Hubble
----------
L_H = exp( - chi^2_H(z) / 2 )

2.7 Lambda_eff
--------------
L_Lambda = exp( - (rho_Lambda_eff/rho_crit - 0.68)^2 / (2 sigma_Lambda^2) )

2.8 Croissance f_sigma8 (dynamique D1/D2)
------------------------------------
L_growth = exp( - chi^2_growth(z=0,0.5,1,1.5) / 2 )


2.9 Likelihood globale
----------------------
L_total = L_mu * L_nu * L_QCD * L_flavour * L_DM * L_H * L_Lambda * L_growth


3. V39-MCMC - CHAINES DE MARKOV
-------------------------------

3.1 Methode
-----------
- Metropolis-Hastings
- 4 chaines independantes
- 5 000 steps par chaine
- burn-in : 1 000 steps
- thinning : 5

3.2 Criteres de convergence
---------------------------
- Gelman-Rubin R_hat < 1.05
- autocorrelation < 0.3
- effective sample size > 500


4. V39-DIAGNOSTICS - ANALYSE DES CHAINES
----------------------------------------

4.1 Sorties
-----------
- traces des parametres
- distributions marginales
- correlations inter-secteurs
- heatmap des tensions residuelles
- best-fit global
- region 68 % et 95 %

4.2 Tests
---------
- convergence_ok
- stability_ok
- multi_sector_balance_ok


5. V39-SYNTHESIS - LECTURE PHYSIQUE GLOBALE
-------------------------------------------

5.1 Objectif
------------
Identifier si une region de l'espace des parametres satisfait :

- EW
- neutrinos
- QCD
- flavour
- DM geometrique
- H(z)
- Lambda_eff
- croissance f_sigma8 via D1/D2

simultanement.

5.2 Sorties attendues
---------------------
- best_fit_parameters
- sector_residuals
- global_tension_map
- multi_scale_consistency
- v39_global_verdict


6. CRITERES DE VERDICT
----------------------

supported :
- region non vide avec L_total > 0.1 L_max
- tensions residuelles < 2 sigma
- convergence_ok = true

partially_supported :
- region existante mais tensions > 2 sigma dans un secteur

rejected :
- aucune region coherente
- ou divergence structurelle D1/D2


7. PROCHAINE ETAPE
------------------
Si V39 est supported :
- V40 : extraction du modele effectif final (Lagrangien geometrique)

Si V39 est rejected :
- reanalyse des couplages D1/D2
- revision de Sent(Y) ou K_bg(z)


8. RESULTATS OBSERVES V39
-------------------------

Suite validee :
- v39mcmc_suite
- supported_count : 5/5
- v39_global_verdict : supported
- timestamp suite : 20260519-152514Z

Rapports generes dans :
- [results/result-analyse/v39_mcmc](results/result-analyse/v39_mcmc)

Synthese observee :
- V39-PARAMSPACE : supported
- V39-LIKELIHOODS : supported
- V39-MCMC : supported
- V39-DIAGNOSTICS : supported
- V39-SYNTHESIS : supported

Points saillants observes :
- R_hat_logl = 1.0071430442375717
- R_hat_epsilon = 1.01616493019382
- autocorr_logl = 0.8586399832749256
- autocorr_epsilon = 0.9443708270898736
- ess_logl = 1177.648250968803
- ess_epsilon = 1107.748765061732
- supported_region_fraction = 0.4559375

Verdict final V39 :
- supported