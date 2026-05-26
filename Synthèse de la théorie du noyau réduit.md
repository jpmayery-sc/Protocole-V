# V23 – Synthèse de la théorie du noyau réduit
 
## 1. Objet du modèle
 
Le pipeline V11–V23 construit et teste un **noyau réduit** qui décrit un système interne
à partir de cinq paramètres principaux :
 
- alpha0 : paramètre dominant, lié à la structure fine effective,
- s_geo, s_atom : paramètres de métrique interne,
- A_kappa : paramètre de couplage de canal,
- p : paramètre de torsion interne.
 
Le modèle ne cherche pas à décrire tout le réel, mais un **régime précis** où ces cinq
axes suffisent à rendre compte :
 
- des redshifts internes,
- des corrections spectroscopiques,
- d’une torsion effective,
- d’une hiérarchie stable des paramètres.
 
---
 
## 2. Géométrie interne
 
Le noyau réduit est interprété comme vivant sur un espace interne \(\mathcal{M}_{\text{int}}\)
muni d’une métrique :
 
\[
g_{\text{int}} = \mathrm{diag}(s_{\text{geo}}, s_{\text{atom}})
\]
 
Les résultats V20–V22 montrent :
 
- **metric_consistency = true**
- **geostructureok = true**
- **curvature_indicator ≈ 0**
 
La géométrie interne est donc **faiblement courbée / quasi plate** dans le voisinage
du profil de référence V18.  
Le lien très fort entre alpha0 et la structure géométrique
(**alpha0_geometriclink ≈ 10⁶**) suggère qu’alpha0 joue le rôle
d’**invariant géométrique interne**.
 
---
 
## 3. Torsion effective
 
Le paramètre p et le couplage A_kappa sont interprétés comme définissant une
**connexion avec torsion** sur \(\mathcal{M}_{\text{int}}\) :
 
\[
\Gamma = \{ \} + K(p, A_\kappa)
\]
 
Les observables montrent :
 
- une torsion effective non nulle : **torsion_strength ≈ 1.2×10⁻⁴**,
- une stabilité locale : **torsion_stability = true**,
- un couplage lisible : **torsion_kappa_coupling ≠ 0**.
 
La torsion est donc :
 
- **réelle** (non nulle),
- **stable** (robuste aux perturbations locales),
- **couplée** au canal interne (A_kappa).
 
Elle peut être vue comme une **torsion interne effective**, compatible avec les
bornes expérimentales connues (V22‑EXPERIMENT).
 
---
 
## 4. Hiérarchie des paramètres
 
V19–V22 montrent une hiérarchie nette :
 
1. **alpha0** : paramètre dominant (invariant structurel),
2. **s_geo, s_atom** : paramètres de métrique interne,
3. **p** : paramètre de torsion,
4. **A_kappa** : paramètre de couplage de canal.
 
Cette hiérarchie est :
 
- **stable** (hierarchy_stable = true),
- **robuste** (multivariable_robustness = true),
- **cohérente** avec la lecture géométrie + torsion.
 
Elle définit un **ordre structurel** :
 
> dominant → metric → torsion → coupling
 
qui est retenu comme **invariant de structure** du modèle.
 
---
 
## 5. Domaine de validité
 
V23‑DOMAIN distingue trois zones :
 
- **zone sûre (safe_region)**  
  – noyau local autour du profil V18,  
  – V19 localement bon,  
  – V20 et V22 supportés,  
  – invariants stables.
 
- **zone tendue (borderline_region)**  
  – zone de transition autour du point V19‑ROBUST‑GLOBAL,  
  – marge de récupération faible mais positive (V21),  
  – structure encore lisible mais sensible.
 
- **zone interdite (forbidden_region)**  
  – au‑delà des plages testées,  
  – instabilité potentielle,  
  – hiérarchie ou torsion susceptibles de se casser.
 
Le modèle est donc **valide** dans une région bien définie de l’espace des paramètres
et des observables, et ne prétend pas être universel.
 
---
 
## 6. Invariants retenus
 
Les invariants structurels retenus par V23 sont :
 
- **alpha0** : invariant géométrique interne dominant,
- **metric_pair(s_geo, s_atom)** : structure métrique interne,
- **torsion_eff** : torsion effective interne,
- **hierarchy (dominant → metric → torsion → coupling)** : invariant de structure.
 
Ces invariants restent stables sur le domaine de validité identifié.
 
---
 
## 7. Questions ouvertes
 
V23‑OPEN retient plusieurs questions :
 
1. **V12 falsifiée**  
   – comment étendre le modèle pour réintégrer ou remplacer cette couche ?
 
2. **Lien avec des théories géométriques complètes**  
   – connexion précise avec Einstein–Cartan ou d’autres modèles à torsion ?
 
3. **Extension de domaine**  
   – jusqu’où peut‑on étendre la zone sûre sans casser la hiérarchie ?
 
4. **Lien avec des données astrophysiques plus larges**  
   – tests systématiques sur des catalogues plus étendus (SDSS, NED, X‑ray, etc.).
 
Ces questions définissent les pistes de travail au‑delà de V23.
 
---
 
## 8. Verdict global
 
V23 conclut :
 
- le schéma global est **cohérent** (schema_ok = true),
- les invariants sont **stables**,
- le domaine de validité est **clairement borné**,
- les questions ouvertes n’affectent pas la cohérence interne.
 
Verdict V23 :
 
- **v23verdict = coherent_model**  
- **confidence_level = very_high**  
- **recommendednextstep = exploration / extension contrôlée (V24)**
 
Ce document sert de **référence théorique minimale** pour tout travail ultérieur
sur le noyau réduit.
