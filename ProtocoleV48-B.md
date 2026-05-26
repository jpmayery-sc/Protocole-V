# V48-B — SECTEUR MATIÈRE UNIFIÉ (QUARKS, LEPTONS, NEUTRINOS, HADRONS)

Version : 0.2

Protocole précédent : [ProtocoleV48.md](ProtocoleV48.md)

Wrapper global suggéré :
- [python/scripts/runv48b_suite.py](python/scripts/runv48b_suite.py)

Modules :

- V48-QUARK-MASS-DERIVATION   - Cohérence des masses des quarks u, d, s, c, b, t
- V48-HADRON-COLLECTIVE-MODE  - Cohérence des masses hadroniques simples
- V48-PMNS-NEUTRINO-LIGHT     - Angles PMNS et spectre léger
- V48-HEAVY-NEUTRINOS         - Neutrinos lourds / stériles (N_R)
- V48-GEOMETRIC-CONSISTENCY   - Cohérence géométrique K/T/Y + D1/D2 sur tout le secteur matière
- V48-SYNTHESIS               - Verdict global secteur matière


## 0. Objectif

Unifier dans un même protocole :

- les résultats electron5_core (quarks, hadrons, PMNS légers)
- les tests neutrinos lourds / stériles (N_R)
- la cohérence géométrique K/T/Y + D1/D2
- la cohérence avec V35–V47

V48 doit répondre à la question :  
**le secteur matière complet (quarks + leptons + neutrinos + hadrons) est‑il compatible avec la géométrie K/T/Y + D1/D2 validée jusqu’à V47 ?**


## 1. V48-QUARK-MASS-DERIVATION

On reprend le bloc electron5_core :

- masses des quarks u, d, s, c, b, t
- comparaison aux valeurs de référence PDG
- tolérance relative typique : < 5 %

Sorties :
- quark_mass_table
- light_quark_ok
- heavy_quark_ok
- quark_mass_ok
- verdict


## 2. V48-HADRON-COLLECTIVE-MODE

On reprend les hadrons simples :

- π⁺, K⁺, p, n, Λ⁰, Δ⁺⁺
- masses prédites vs masses de référence
- tolérance relative : < 1 %

Sorties :
- hadron_mass_table
- meson_ok
- baryon_ok
- hadron_mass_ok
- verdict


## 3. V48-PMNS-NEUTRINO-LIGHT

On reprend la structure PMNS :

- angles θ₁₂, θ₂₃, θ₁₃
- spectre léger (m₁, m₂, m₃)
- splittings Δm²₂₁, Δm²₃₁

Contraintes :
- angles dans les intervalles globaux
- Σmν compatible avec V43/V48‑heavy

Sorties :
- PMNS_angles
- light_spectrum
- splittings_ok
- PMNS_ok
- verdict


## 4. V48-HEAVY-NEUTRINOS (N_R)

On intègre le bloc N_R :

- matrice de masse étendue M_ν = [[0, m_D], [m_Dᵀ, M_R]]
- m_D = λ_i K (hérité V35)
- M_R = M0 + α_K K + α_T T

On calcule :

- masses lourdes M_R
- mélange actif‑stérile Θ ≈ m_D M_R⁻¹
- contraintes cosmologiques (ΔN_eff, Σmν)
- contraintes de désintégration (X‑ray, stabilité)

Sorties :
- heavy_neutrino_masses
- mixing_angles
- delta_Neff
- sum_mnu
- heavy_neutrino_ok
- verdict


## 5. V48-GEOMETRIC-CONSISTENCY

On vérifie que :

- les corrections géométriques (K/T/Y) utilisées pour :
  - quarks
  - leptons (e, μ, τ)
  - neutrinos légers
  - neutrinos lourds
  - hadrons
  restent :
  - petites (ε_geom ≲ quelques × 10⁻³)
  - cohérentes avec V44 (potentiel)
  - stables sous V45 (flow RG)
  - compatibles avec V47 (baryons) et V49 (photon)

Sorties :
- epsilon_geom_quarks
- epsilon_geom_leptons
- epsilon_geom_hadrons
- multisector_geometry_ok
- RG_consistency_ok
- verdict


## 6. V48-SYNTHESIS

Sorties attendues :
- quark_summary
- hadron_summary
- PMNS_summary
- heavy_neutrino_summary
- geometry_summary
- v48_global_verdict


## 7. Critères de verdict

supported :
- quark masses dans les tolérances
- hadrons simples dans les tolérances
- PMNS et spectre léger cohérents
- neutrinos lourds compatibles (ΔN_eff, Σmν, X‑ray)
- corrections géométriques petites et stables
- cohérence totale avec V35–V47

partially_supported :
- un sous‑bloc marginal mais contrôlé

rejected :
- incohérence forte dans un sous‑secteur
- violation cosmologique
- rupture géométrique multi‑secteur


## 8. Résultats observés (run réel)

Suite exécutée : v48b_suite  
Horodatage : 20260519-212817Z

Chiffres globaux :
- v48_global_verdict : supported
- supported_count : 5/5

Résumé généré :
- [v48b_suite_summary_20260519-212817Z.json](results/result-analyse/v48_b/v48b_suite_summary_20260519-212817Z.json)
- [v48b_suite_summary_20260519-212817Z.txt](results/result-analyse/v48_b/v48b_suite_summary_20260519-212817Z.txt)

Points saillants :
- quark_mass_ok : true
- hadron_mass_ok : true
- PMNS_ok : true
- heavy_neutrino_ok : true
- multisector_geometry_ok : true
- RG_consistency_ok : true
- max_rel_err(quarks) : 0.032
- max_rel_err(hadrons) : 0.0048
- θ12 = 33.4°
- θ23 = 49.0°
- θ13 = 8.6°
- Σmν = 0.058 eV
- M_R = {2.1 GeV, 14.3 GeV}
- |Θ| = {0.021, 0.008}
- ΔN_eff = 0.04
- ε_geom = {0.0011, 0.0012, 0.0014}

### 8.1 Résultats numériques détaillés

| Check | Verdict | Chiffres principaux |
|-------|---------|---------------------|
| Quark masses | supported | max_rel_err = 0.032, light_quark_ok = true, heavy_quark_ok = true |
| Hadrons simples | supported | max_rel_err = 0.0048, meson_ok = true, baryon_ok = true |
| PMNS léger | supported | θ12 = 33.4°, θ23 = 49.0°, θ13 = 8.6°, Σmν = 0.058 eV |
| Neutrinos lourds | supported | M_R = {2.1, 14.3} GeV, |Θ| = {0.021, 0.008}, ΔN_eff = 0.04 |
| Cohérence géométrique | supported | ε_geom = {0.0011, 0.0012, 0.0014}, RG_consistency_ok = true |
| Synthesis | supported | v48_global_verdict = supported, supported_count = 5/5, total = 5 |

Lecture d’ensemble :

- le secteur matière complet (quarks + leptons + neutrinos + hadrons)
  reste compatible avec la géométrie K/T/Y + D1/D2
- aucune rupture cosmologique ou structurelle n’apparaît dans les observables retenues
- la lecture V48-B reste cohérente avec V35–V47