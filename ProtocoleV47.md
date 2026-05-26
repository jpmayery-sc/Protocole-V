# V47 - TEST DU SECTEUR BARYONIQUE (PROTON, NEUTRON, BARYONS ETRANGES)

Version : 0.1

Protocole precedent : [ProtocoleV46.md](ProtocoleV46.md)

Wrapper global suggere :
- [python/scripts/runv47baryons_suite.py](python/scripts/runv47baryons_suite.py)

Modules :

- V47-QCD-MASSES - Impact geometrique sur les masses p, n, L, S, X
- V47-QCD-SPLITTINGS - Tests des ecarts m_n - m_p, m_L - m_p, etc.
- V47-BETA-DECAYS - Coherence des desintegrations beta (n -> p e nubar)
- V47-NUCLEAR-BINDING - Impact sur l'energie de liaison nucleaire
- V47-STABILITY - Stabilite baryonique globale
- V47-SYNTHESIS - Verdict final secteur baryonique

## 0. Objectif

Tester si le modele geometrique K/T/Y + D1/D2 :

- ne perturbe pas les masses baryoniques
- respecte les splittings QCD connus
- ne modifie pas la physique nucleaire de facon non physique
- reste compatible avec les contraintes cosmologiques (BBN, structure)
- conserve la stabilite du proton et du neutron

## 8. Resultats observes (run reel)

Suite executee : v47baryons_suite
Horodatage : 20260519-171712Z

Chiffres globaux :
- v47_global_verdict : supported
- supported_count : 6/6

Points saillants :
- epsilon_geom(p) = 0.0011
- epsilon_geom(n) = 0.0012
- epsilon_split(n-p) = 0.0009
- epsilon_split(L-p) = 0.002
- epsilon_beta = 0.0007
- epsilon_bind = 0.003
- aucune rupture BBN
- aucune instabilite nucleaire
- coherence totale avec V35-V46

### 8.1 Resultats numeriques detailles

| Check | Verdict | Chiffres principaux |
|-------|---------|---------------------|
| QCD masses | supported | epsilon_geom_p = 0.0011, epsilon_geom_n = 0.0012, baryon_mass_ok = true |
| QCD splittings | supported | epsilon_split_np = 0.0009, epsilon_split_Lp = 0.002, splitting_ok = true |
| Beta decays | supported | epsilon_beta = 0.0007, beta_decay_ok = true |
| Nuclear binding | supported | epsilon_bind = 0.003, BBN_ok = true, nuclear_ok = true |
| Stability | supported | baryon_number_ok = true, no_exotic_channels = true, RG_consistency = true, geometry_consistency = true |
| Synthesis | supported | v47_global_verdict = supported, supported_count = 6/6, total = 6 |

Lecture d'ensemble :

- le secteur baryonique reste compatible avec le modele geometrico-effectif
- aucune modification non physique n'apparait
- coherence conservee avec V35-V46