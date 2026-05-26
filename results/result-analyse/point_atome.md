# Rapport global de la theorie atomique

## Resume

La theorie de travail du dossier atome ne cherche pas a imposer une loi unique et universelle. Elle organise plutot les faits en plusieurs niveaux de lecture:

- D1 pour l attraction de base et l echelle atomique,
- D2 pour le transport, le flux et la mobilite,
- D3 pour la topologie de bloc et les effets de structure,
- D4 pour la densite electronique, la degenerescence et la pression de Fermi.

Le resultat principal est simple: une partie importante des familles atomiques se laisse lire proprement avec un proxy hydrogenoide Z_eff, mais les blocs de transition et les lanthanides demandent une lecture structurelle plus fine. La balance locale D1 ≈ D4 n est pas une loi generale hors regime dense; c est une lecture d equilibre dans les cas ou la densite compte vraiment.

## Idee directrice

Le programme de travail part de l hypothese suivante: les tendances atomiques visibles dans les familles, les blocs et les sous-familles ne sont pas toutes du meme type. Il faut donc distinguer:

1. les familles regulieres,
2. les blocs partiellement reguliers,
3. les familles a residus internes forts,
4. les cas ou une sous-famille locale est plus informative que la famille complete.

Cette distinction evite de forcer une reduction unique sur des objets qui n ont pas la meme structure physique.

## Architecture de la theorie

### D1

D1 reste la lecture de base: attraction noyau-electron, echelle atomique, ordre elementaire des rayons et des energies d ionisation.

### D2

D2 sert pour les phenomenes de transport, de flux, de mobilite et de reponse collective. Dans le dossier general, cette lecture joue surtout un role de contexte, pas de pivot principal.

### D3

D3 devient necessaire quand la geometrie de bloc ou la topologie electronique dominent le cas. C est la bonne echelle pour les lanthanides et pour les transitions quand une simple lecture monotone casse.

### D4

D4 devient pertinente dans les regimes denses, quand la densite electronique, la degenerescence ou la pression de Fermi commencent a peser comme variable de controle. Dans cette lecture, D1 et D4 peuvent s equilibrer localement, mais pas partout ni toujours.

## Lecture experimentale par colonnes

Le dossier atome a ete organise en 12 colonnes de contraste.

| Colonne | Famille / bloc | Lecture |
| --- | --- | --- |
| 1 | Alcalins | regularite forte, supported |
| 2 | Alcalino-terreux | regularite forte, supported |
| 3 | Halogenes | regularite forte, supported |
| 4 | Chalcogenes | regularite forte, supported |
| 5 | Gaz nobles | regularite forte, supported |
| 6 | Pnictogenes | regularite forte, supported |
| 7 | Transition 3d | bloc partiel, lecture edge/core necessaire |
| 8 | Transition 4d | bloc partiel, lecture edge/core necessaire |
| 9 | Transition 5d | lecture dual-core robuste, supported |
| 10 | Lanthanides | bloc structurel, partiel au niveau global |
| 11 | Tetrels | famille supportee, anomalie lourde localement |
| 12 | Bore | famille supportee, raffinage local utile |

Le point commun est que Z_eff reste un bon proxy d ordre dans les familles regulieres. En revanche, les blocs de transition et les lanthanides ne doivent pas etre forces dans la meme forme: ils demandent une lecture de bord, de coeur ou de sous-ensemble.

## Ce que confirment les validations

Les validations deja lancees soutiennent trois faits importants.

1. Les familles regulieres sont coherentes avec un proxy Z_eff monotone et un screening S = Z - Z_eff monotone.
2. Les blocs de transition ne sont pas tous equivalentes a une famille simple: certains cas sont partiels, d autres reclament une lecture dual-core.
3. Les cas tetrel et bore restent supportes au niveau global, tout en gardant des anomalies locales qui justifient un commentaire de structure.

Le dossier atome rassemble ces resultats dans [atome_dossier.md](atome_dossier.md) avec un tableau de synthese et des sections detaillees par colonne.

## Suite logique S

La consolidation suivante est maintenant formalisee autour de la loi de screening S(Z,n,l).

1. Fermer la forme saturante minimale de S sur des donnees non alcalines, en comparant saturation exponentielle et loi de puissance par bloc.
2. Tester la predictivite sans recalage sur les rayons atomiques, avec un vrai controle held-out par famille.
3. Delimiter les regimes utiles de S pour eviter toute fusion artificielle en loi unique.
4. Garder un pont minimal vers la physique standard via les observables alpha et phase, sans re-deriver les constantes.
5. Chercher les contre-exemples lourds et lanthanides pour falsifier les formes trop larges avant generalisation.

La branche isotope reste a raccorder quand un jeu de donnees explicite sera disponible; le reste du protocole S est deja executable.

### Branche isotopique reservee

Le sous-bloc isotopique est maintenant specifie mais reste data-gated.

Le contrat de travail est fixe dans [isotopic_shift_contract.md](isotopic_shift_contract.md):

- observable principal: $\delta S(A) = S(Z, A) - S(Z, A_0)$,
- hypothese minimale: effet faible, monotone et borne,
- dependance attendue: coeur nucleaire et rayon nucleaire effectif,
- aucune pente isotope par isotope ne doit etre recalée a la main,
- seules des donnees isotope-resolues mesurees sont acceptables.

La preparation de donnees associee est decrite dans [isotope_data_prep.md](isotope_data_prep.md):

- NIST ASD comme source primaire de repere,
- NNDC / NuDat / ENSDF pour les masses isotopiques et les rayons de charge nucleaires,
- articles de spectroscopie optique de precision pour les shifts explicites,
- extraction normalisee en CSV ou JSON avec paire isotopique, transition, delta nu et incertitude,
- rejet des valeurs reconstruites ou des moyennes sans observation paire a paire.

Le bloc reste volontairement en attente d une source de donnees explicite. Tant que ce point n est pas leve, aucune exécution n est autorisee sur une base implicite.

### Prochain bloc non data-gated recommande

Le bloc a ouvrir maintenant est la transition de bloc $s \rightarrow p \rightarrow d \rightarrow f$.

Pourquoi ce bloc:

- il repose sur des donnees deja presentes,
- il a un fort pouvoir falsifiant,
- il permet de tester la continuite de $S$ aux frontieres de bloc sans loi unique artificielle,
- il reste compatible avec la logique de regimes deja etablie.

Les points d entree utiles sont [python/scripts/family_l_slope_check.py](../../python/scripts/family_l_slope_check.py) pour la geometrie de pente s/p/d/f et [python/scripts/spd_f_instrumentation_check.py](../../python/scripts/spd_f_instrumentation_check.py) pour l instrumentation unifiee des quatre blocs.

## Protocole exploitable depuis Electron-5

Le passage Electron-5 qui reste exploitable commence au bloc f des lanthanides. Dans ce rapport, Electron-5 sert de source de travail, mais le statut canonique reste celui du present document. La partie utile n est pas la formule universelle proposee en fin de texte, mais la structure de test qui compare une pente mesuree a une prediction de bloc.

### Hypothese de travail

L idee a tester est la suivante:

- dans une famille donnee, Z_eff doit rester lisible a partir des premieres energies d ionisation,
- la pente de Z_eff depend de la structure radiale du bloc,
- le bloc f doit montrer une pente plus faible que le bloc d et une lecture core / valence plus fine que la simple formule lineaire,
- la formule compacte m(l) = A(l + 1/2) doit etre consideree comme falsifiable, pas comme acquise.

### Partie du texte qui vaut protocole

Le noyau testable du passage est:

1. prendre une famille complete,
2. calculer Z_eff a partir de E_ion et de n,
3. mesurer la pente entre les premiers et derniers points,
4. comparer cette pente entre blocs s, p, d et f,
5. verifier si une loi compacte tient encore face aux donnees,
6. corriger la loi avec une lecture valence / core si le bloc f casse la version brute.

### Liste des tests a garder

1. Test bloc f lanthanide
- calculer Z_eff sur Ce -> Yb,
- verifier que la pente reste faible,
- verifier que la lecture 6s / coeur f rend mieux compte du comportement que la loi compacte brute.

2. Test de hierarchie des pentes
- comparer s, p, d, f,
- verifier l ordre relatif des pentes,
- noter les anomalies locales qui cassent la monotonicite naive.

3. Test de falsification de la loi compacte
- appliquer m(l) = A(l + 1/2) sur une famille simple,
- verifier si la loi reproduit les donnees,
- rejeter la loi si elle surestime ou sous-estime trop fortement la progression.

4. Test de correction core / valence
- remplacer la loi compacte par une lecture a deux couches,
- verifier si le bloc f devient coherent une fois le coeur et la valence distingues.

5. Test de famille simple pour contraste
- reprendre une famille reguliere comme les alcalins,
- verifier que la loi compactee ne suffit pas a elle seule,
- garder la famille comme controle negatif ou limite locale.

### Ce qui n est pas exploitable tel quel

La formule finale Z_eff(Z) = Z_core + A * ((l_valence + 1/2) / (l_core + 1/2)) * (Z - Z_0) n est pas encore un protocole valide en l etat. Elle doit passer par une etape de definition precise des variables l_valence, l_core et A avant d etre ajoutee au corpus de tests. Le statut confirme par les derniers checks est le suivant: m(l) = A(l + 1/2) est falsifie, la correction core / valence reste contradictoire, et l instrumentation s/p/d/f unique est supportee.

En pratique, le bon point de depart pour les tests est donc la comparaison des pentes et la falsification de la loi compacte, pas la loi universelle elle-meme.

### Liste des tests

| Test | Entree | Verification | Attendu |
| --- | --- | --- | --- |
| Bloc f lanthanide | Ce -> Yb | Calculer Z_eff a partir de E_ion et n=6 | Pente faible, lecture core / valence necessaire |
| Hierarchie des pentes | s, p, d, f | Comparer les pentes mesurees | Ordre relatif stable, anomalie du bloc f isolee |
| Loi compacte | Une famille simple | Tester m(l) = A(l + 1/2) | Loi falsifiee ou limitee par les donnees |
| Correction core / valence | Bloc f | Remplacer la loi brute par une lecture a deux couches | Bloc f rendu coherent localement |
| Contraste famille simple | Alcalins | Reprendre une famille reguliere comme controle | La loi compacte ne suffit pas seule |

### Priorite d execution

1. lancer le test bloc f lanthanide,
2. comparer les pentes s, p, d, f,
3. tester la loi compacte sur une famille simple,
4. activer la correction core / valence si le bloc f casse la version brute,
5. garder les alcalins comme controle negatif.

### Liste exploitable maintenant

| Test exploitable | Script disponible | Statut | Ce que ca valide |
| --- | --- | --- | --- |
| Contrat isotopique S(A) | [isotopic_shift_contract.md](isotopic_shift_contract.md) | reserve | Branche prete, mais bloque par l absence de donnees isotope-resolues explicites |
| Transition s/p/d/f | [python/scripts/family_l_slope_check.py](../../python/scripts/family_l_slope_check.py) puis [python/scripts/spd_f_instrumentation_check.py](../../python/scripts/spd_f_instrumentation_check.py) | exploitable | La continuite de S aux frontieres de bloc peut etre testee sans recalage artificiel |
| Screening loi S | [python/scripts/screening_law_saturation_check.py](../../python/scripts/screening_law_saturation_check.py) | exploitable | Une saturation exponentielle ou une loi de puissance peut etre comparee sur les familles non alcalines avec residus mesures |
| Predictivite rayon sans retrofit | [python/scripts/radius_predictivity_check.py](../../python/scripts/radius_predictivity_check.py) | exploitable | Le correctif core / valence est teste en held-out family et ne depend pas du recalage sur la famille de test |
| Suite logique S | [python/scripts/run_s_law_suite.py](../../python/scripts/run_s_law_suite.py) | exploitable | Enchaine screening, predictivite, regime physics, pont alpha et falsification lourde en un seul rapport |
| Saturation loi compacte | [python/scripts/run_saturation_suite.py](../../python/scripts/run_saturation_suite.py) | exploitable | Le signal de rupture reste mesurable et la loi compacte ne se generalise pas partout |
| Bloc f lanthanide | [scripts/lanthanide_block_edge_view_check.py](../../scripts/lanthanide_block_edge_view_check.py) | exploitable | Le bord de serie domine la perte de regularite |
| Residual lanthanide | [python/scripts/lanthanide_internal_residual_check.py](../../python/scripts/lanthanide_internal_residual_check.py) | exploitable | Le noyau repare est plus regulier que la serie complete |
| Omega(Z) | [python/scripts/omega_z_structure_check.py](../../python/scripts/omega_z_structure_check.py) | exploitable | Le gain local reste lisible sur les cas lourds et les probes Fr / Ra / Lr |
| Suite protocole Point Atome | [python/scripts/run_point_atome_protocol_suite.py](../../python/scripts/run_point_atome_protocol_suite.py) | exploitable | Enchaine saturation, Omega(Z), controle de bord et regime physics |
| Master protocole Point Atome | [python/scripts/run_point_atome_master_suite.py](../../python/scripts/run_point_atome_master_suite.py) | exploitable | Enchaine le protocole Point Atome, D1/D4 et Electron-5 |
| Regime D1 / D2 / D3 / D4 | [python/scripts/run_regime_physics_suite.py](../../python/scripts/run_regime_physics_suite.py) | exploitable | La grille regime / transport / densite reste coherente sur les branches atomique, metal, lanthanide et dense |
| Families regulières Z_eff | [python/scripts/alkali_halogen_zeff_check.py](../../python/scripts/alkali_halogen_zeff_check.py) | exploitable | Z_eff et S restent monotones dans les familles simples |
| Regime atomique / metal / lanthanide / dense / flow | [python/scripts/run_regime_physics_suite.py](../../python/scripts/run_regime_physics_suite.py) | exploitable | La grille D1 / D2 / D3 / D4 reste coherente au niveau global |
| Flux D1 / D2 / D3 / D4 | [python/scripts/regime_flow_check.py](../../python/scripts/regime_flow_check.py) | exploitable | Les parts relatives restent ordonnees sur les quatre regimes |
| Fine variation equivalence | [python/scripts/fine_variation_equivalence_check.py](../../python/scripts/fine_variation_equivalence_check.py) | exploitable | Geometrie et energie donnent une amelioration comparable sur les familles simples |
| Fine variation hard check | [python/scripts/fine_variation_hard_check.py](../../python/scripts/fine_variation_hard_check.py) | exploitable | Le meme schema tient sur le pnictogene avec noyau repare |
| Electron-5 core suite | [python/scripts/run_electron5_core_suite.py](../../python/scripts/run_electron5_core_suite.py) | exploitable | Quark masses, hadrons collectifs et PMNS restent supportes |
| Electron-5 extended suite | [python/scripts/run_electron5_extended_suite.py](../../python/scripts/run_electron5_extended_suite.py) | exploitable | Quartz D2, separation quartz/gluon et fine variation restent supportes |
| Alpha / phase observable | [python/scripts/alpha_phase_observable_check.py](../../python/scripts/alpha_phase_observable_check.py) | exploitable | La lecture de phase reste stable a l inverse de alpha |
| Shell / sub-shell | [python/scripts/shell_subshell_check.py](../../python/scripts/shell_subshell_check.py) | exploitable | Les ruptures locales de sous-couche restent visibles dans la periode |
| Instrumentation s/p/d/f unique | [python/scripts/spd_f_instrumentation_check.py](../../python/scripts/spd_f_instrumentation_check.py) | exploitable | Une seule instrumentation compare les quatre blocs et reduit les residus partout |

### Etat des derniers checks

- saturation compacte: conforme strict
- screening loi S: supported
- predictivite rayon sans retrofit: supported
- contrat isotopique S(A): reserve
- transition s/p/d/f: supported
- lanthanide block-edge: partiel
- lanthanide internal residual: supported
- lanthanide k/l correction: supported
- lanthanide subseries Zeff*: supported
- regime_physics globale: supported
- familles regulieres Z_eff / screening: supported
- tetrel famille: supported
- tetrel sous-famille raffinee: supported
- bore famille: supported
- bore sous-famille raffinee: supported
- fine variation equivalence: supported
- fine variation hard check: supported
- electron5 core suite: supported
- electron5 extended suite: supported
- alpha phase observable: supported
- shell / sub-shell: supported
- alpha constant: falsifie
- family l-slope: falsifie
- core / valence correction: contradicted
- omega z structure: supported
- suite protocole point atome: supported
- master protocole point atome: supported
- suite logique S: supported
- instrumentation s/p/d/f unique: supported
- suite regime_physics globale: supported

### Tests de validation du protocole

Ces tests ne valident pas encore une nouvelle loi physique. Ils valident seulement que le protocole de lecture est assez precis pour distinguer les regimes, les saturations et les cas limites sans les confondre.

#### Objectif

- verifier que chaque bloc de test a un critere observable,
- verifier que les seuils ne se contredisent pas entre eux,
- verifier que la lecture locale ne se transforme pas en loi universelle par glissement de vocabulaire,
- verifier que les cas lourds gardent leur statut de cas de bord.

#### Grille de validation

| Bloc | Ce qui est valide | Ce qui doit echouer si le protocole est sain | Verdict attendu |
| --- | --- | --- | --- |
| Saturation de la loi compacte | residu relatif, derive locale, gain structurel | stabilite artificielle de A sur toutes les familles | partiel ou contradictoire selon les familles |
| Structure Omega(Z) | torsion residuelle, courbure locale, rayon interne normalise | confusion entre rayon effectif et rayon interne | support local seulement |
| Controle de bord | indice de bord, separation de regime, robustesse locale | fusion de Fr, Ra et Lr dans un seul canal | distinction conservee entre regimes |

#### Critere de validation global

Le protocole est considere comme valide si les trois conditions suivantes restent vraies:

- la saturation de la loi compacte donne un signal de rupture mesurable,
- Omega(Z) apporte un gain local sans masquer le residu de base,
- le controle de bord maintient la distinction entre regime atomique, regime structural et regime dense.

Si l un de ces points disparait, il faut corriger le protocole avant de pretendre a une lecture generale.

#### Checklist executable

1. Tester la saturation de la loi compacte sur une famille reguliere.
- verifier le residu relatif moyen,
- verifier la derive locale entre debut et fin,
- attendre un resultat localement supporte ou partiellement contradictoire selon la famille.

2. Tester Omega(Z) sur une famille lourde.
- verifier le gain Omega,
- verifier la torsion residuelle,
- verifier la courbure locale,
- attendre un support local seulement.

3. Tester le controle de bord sur Fr, Ra et Lr.
- verifier l indice de bord,
- verifier la separation de regime,
- verifier que la lecture brute ne gagne pas contre la lecture structurelle,
- attendre une distinction conservee entre regimes.

4. Comparer les trois blocs entre eux.
- verifier que la saturation, Omega(Z) et le bord ne racontent pas la meme chose,
- verifier que chaque bloc garde son domaine d usage,
- attendre une couverture coherente sans fusion artificielle.

5. Enchainer la suite protocole Point Atome.
- lancer saturation, Omega(Z), controle de bord puis regime physics,
- verifier que chaque suite garde son propre verdict,
- attendre un resume global lisible sans ecraser les sorties locales.

#### Liste de validation concrete

| Test | Entree | Observation | Verdict attendu |
| --- | --- | --- | --- |
| Saturation compacte | famille reguliere puis famille lourde | residu relatif, derive locale, gain structurel | partiel si la famille reguliere reste lisible, contradictoire si la pente unique survit partout |
| Omega(Z) locale | cas lourds avec torsion, courbure et rayon interne | gain Omega, torsion residuelle, rayon interne normalise | support local seulement si le gain reste positif sans confusion des variables |
| Controle de bord | Fr, Ra, Lr compares aux regimes deja supportes | indice de bord, separation de regime, robustesse locale | distinction conservee entre regimes si les cas lourds se repartissent sur plusieurs lectures |
| Comparaison croisee | saturation, Omega(Z), bord | coherence entre les trois blocs | couverture valide si aucun bloc ne pretend couvrir le domaine des autres |

#### Ordre d execution conseille

1. Saturation de la loi compacte,
2. Structure Omega(Z),
3. Controle de bord,
4. Comparaison croisee des blocs.

#### Sortie attendue

- saturation compacte: rupture locale lisible, sans loi universelle,
- Omega(Z): gain structurel local, sans confusion des rayons,
- controle de bord: distinction conservee entre Fr, Ra et Lr,
- comparaison croisee: chaque bloc garde son domaine d usage.

### Bloc suivant

Le bloc suivant du protocole est la comparaison regime / transport / densite sur la grille D1 / D2 / D3 / D4.

Le but est de verifier que la lecture dominante change correctement selon le cas teste:

- D1 pour l atome leger,
- D1 + D2 pour le metal,
- D3 pour le lanthanide,
- D4 pour le regime dense.

La suite a lancer pour ce bloc est [python/scripts/run_regime_physics_suite.py](../../python/scripts/run_regime_physics_suite.py), avec [python/scripts/regime_flow_check.py](../../python/scripts/regime_flow_check.py) comme controle de parts relatives.

- saturation: signal de rupture mesurable,
- Omega(Z): gain local sans universalite,
- controle de bord: separation claire des cas lourds,
- comparaison croisee: confirmation que les trois blocs ne sont pas redondants.

#### Plan d execution concret

| Bloc | Script ou commande associee | Statut | Sortie attendue |
| --- | --- | --- | --- |
| Saturation de la loi compacte | [python/scripts/run_saturation_suite.py](../../python/scripts/run_saturation_suite.py) puis [python/scripts/run_saturation_tests.py](../../python/scripts/run_saturation_tests.py) | disponible | un signal de rupture sur au moins une famille lourde, sans loi compacte universelle |
| Structure Omega(Z) | [python/scripts/omega_z_structure_check.py](../../python/scripts/omega_z_structure_check.py) | disponible | un gain local lisible sur les cas lourds, sans confusion entre rayon effectif et rayon interne |
| Controle de bord | [scripts/lanthanide_block_edge_view_check.py](../../scripts/lanthanide_block_edge_view_check.py) puis [python/scripts/run_block_edge_suite.py](../../python/scripts/run_block_edge_suite.py) | disponible | une distinction conservee entre bord atomique, bord structural et bord dense |
| Comparaison croisee | [python/scripts/run_regime_physics_suite.py](../../python/scripts/run_regime_physics_suite.py) et [python/scripts/regime_flow_check.py](../../python/scripts/regime_flow_check.py) | disponible | aucune fusion artificielle entre saturation, Omega(Z) et bord |

#### Commande de lancement recommandee

1. lancer [python/scripts/run_saturation_suite.py](../../python/scripts/run_saturation_suite.py),
2. enchaîner avec [python/scripts/omega_z_structure_check.py](../../python/scripts/omega_z_structure_check.py),
3. valider le bord via [scripts/lanthanide_block_edge_view_check.py](../../scripts/lanthanide_block_edge_view_check.py),
4. fermer avec [python/scripts/run_regime_physics_suite.py](../../python/scripts/run_regime_physics_suite.py) et [python/scripts/regime_flow_check.py](../../python/scripts/regime_flow_check.py).

#### Note de couverture

- la saturation est couverte par la suite dediee aux familles simples et lourdes,
- Omega(Z) s appuie maintenant sur un script dedie et sur ses rapports JSON/TXT horodates,
- le controle de bord reste centre sur les lanthanides et les cas lourds,
- la comparaison croisee relie ensuite le tout a la grille D1 / D2 / D3 / D4.

### Ce qui reste a tester

Rien de critique ne reste a couvrir dans ce sous-dossier.

La couverture utile est maintenant fermee par des tests explicites pour les deux grandes branches: regime/familles et electron5.

## Limites de la theorie

La theorie n etablit pas encore:

- une loi universelle hors regime,
- une equivalence complete entre rayon, masse et Z_eff,
- une reduction fiable des lanthanides a une famille simple,
- une lecture brute des transitions sans separation core/edge.

Elle dit plutot que les structures atomiques different par regime et que le bon observateur depend du regime.

## Constraintes empiriques utiles

Le dossier a aussi fixe quelques contraintes de travail:

- la neutralite atomique sert de base,
- l ionisation doit etre lue a noyau constant,
- la rouille et l oxydation ne changent pas l identite nucleaire,
- le cas alpha exact 1/137 est falsifie face a la reference inverse de alpha, meme si l usage mnemonique reste acceptable a tolerance large,
- les seuils, saturations et effets de memoire observes dans d autres systemes doivent etre traites comme des analogies physiques, pas comme une preuve directe en physique des particules.

## Interpretation globale

La meilleure lecture actuelle est la suivante: la theorie n est pas une unique formule, mais une grille de regimes.

- Quand la famille est reguliere, Z_eff et le screening suffisent.
- Quand le bloc se complique, il faut D3.
- Quand la densite domine, il faut D4.
- Quand les signatures deviennent locales, il faut une sous-famille ou une lecture de bord.

Autrement dit, le dossier ne cherche pas a abolir les differences entre familles. Il les classe et les rend testables.

## Conclusion

Le tableau global est maintenant coherent:

- six familles regulieres sont supportees par le proxy hydrogénoide,
- trois colonnes de transition demandent une lecture de bloc,
- les lanthanides restent structurellement partiels,
- tetrels et bore sont supportes au niveau global avec des raffinements locaux utiles.

La theorie de travail tient donc comme theorie de regimes, pas comme loi unique. C est sa force actuelle et aussi sa limite principale.

## Nouveau plan de test

### Objectif

Verifier, sur quelques cas representatifs, que la grille D1 / D2 / D3 / D4 reste coherente avec les regimes identifies dans le rapport global:

- D1 domine dans les cas atomiques simples,
- D2 intervient surtout pour les cas de transport et de conduction,
- D3 devient obligatoire pour les lanthanides et les structures de bloc,
- D4 domine dans les regimes denses.

Le but n est pas de forcer une egalite exacte entre canaux, mais de verifier une hierarchy de regimes et un ordre de grandeur stable.

### Cas a tester

Le testeur doit couvrir quatre cas minimaux:

| Cas | Systeme | Lecture dominante attendue |
| --- | --- | --- |
| A | Atome leger, par exemple Na | D1 |
| B | Metal, par exemple Na ou Al | D1 + D2 |
| C | Lanthanide, par exemple Ce ou Nd | D3 |
| D | Regime dense, avec densite electronique fixee | D4 |

### Grandeurs de travail

Le test ne cherche pas une derivation exacte, mais un bilan de lecture:

$$
E_0 \approx E_{D1} + E_{D2} + E_{D3} + E_{D4}
$$

avec $E_0$ calibre sur le cas dense comme reference de regime.

Les approximations de travail sont les suivantes:

$$
E_{D1} \approx -\frac{I}{n^2}
$$

$$
\mu = \frac{e\,\tau}{m_e}, \qquad \sigma = n_e e \mu
$$

$$
P_F = \frac{(3\pi^2)^{2/3}}{5}\,\frac{\hbar^2}{m_e}\,n_e^{5/3}
$$

Le terme D3 reste un terme structurel: il vaut quasi zero dans les cas simples, mais il doit etre explicitement garde pour les lanthanides.

### Bilan a verifier

Pour chaque cas, le testeur doit:

1. calculer ou estimer $E_{D1}$, $E_{D2}$, $E_{D3}$ et $E_{D4}$,
2. fixer $E_0$ a partir du cas dense,
3. verifier que la somme reste dans l ordre attendu du regime,
4. comparer les parts relatives:

$$
\frac{E_{D1}}{E_0}, \quad \frac{E_{D2}}{E_0}, \quad \frac{E_{D3}}{E_0}, \quad \frac{E_{D4}}{E_0}
$$

Le point important est la lecture relative, pas une egalite brute.

### Critieres de lecture

- Cas A: $E_{D1}$ doit dominer, $E_{D4}$ doit rester negligeable.
- Cas B: $E_{D1}$ et $E_{D2}$ doivent etre visibles, $E_{D4}$ doit rester faible.
- Cas C: $E_{D3}$ ne doit pas etre ignore.
- Cas D: $E_{D4}$ doit etre la reference principale, les autres canaux doivent rester secondaires.

### Decision pratique

Si le testeur constate qu un cas change de regime sans que le plan le prevoie, il ne doit pas forcer le cas dans le mauvais canal. Il doit plutot:

- reclasser le systeme,
- ajuster la lecture dominante,
- conserver la trace du resultat dans le dossier de test.

### Version commentee pour le testeur

Ce plan sert a controler que le modele atomique est un modele de regimes, pas une formule unique.

Le message operational est simple:

- atomique simple: D1,
- metal: D1 + D2,
- lanthanide: D3,
- dense: D4.

Tout test qui contredit cette hierarchie doit etre traite comme une alerte de reclassification, pas comme un succes du meme regime.

Le plan est maintenant executable via [scripts/regime_flow_check.py](../../python/scripts/regime_flow_check.py) et [scripts/run_regime_flow.py](../../python/scripts/run_regime_flow.py), puis integre a la suite [scripts/run_regime_physics_suite.py](../../python/scripts/run_regime_physics_suite.py).

## Rapport des tests

La suite de validation regroupe maintenant cinq checks executables. Tous sont passes en `supported`.

| Check | Verdict | Point cle |
| --- | --- | --- |
| Atomique | supported | D1 domine, D4 reste negligible |
| Metal | supported | D1 reste dominant, D4 reste modere |
| Lanthanide | supported | D3 est necessaire |
| Dense | supported | D1 ~= D4 au point de balance locale |
| Flow | supported | La grille D1 / D2 / D3 / D4 reste ordonnee sur les quatre regimes |

### Bilan global

- 5 checks executes
- 5 checks supportes
- 0 echec
- verdict global de suite: supported

### Lecture operationnelle

Le testeur confirme maintenant la structure suivante:

- regime atomique: D1 seul domine,
- regime metallique: D1 et D2 restent visibles, D4 monte sans prendre le dessus,
- regime lanthanide: D3 est obligatoire,
- regime dense: D4 devient le canal principal,
- plan de flux: les quatre canaux restent ordonnes et compatibles avec la grille.

Ce resultat valide la transition entre le rapport theorique et la suite de tests executable.

## Complements de test issus d'Electron-5

Le passage autour de Fr, Ra et Lr sert maintenant de point de depart pour des tests complementaires. Ils restent exploratoires tant qu'ils ne sont pas relies a un script dedie, mais ils doivent etre gardes dans le dossier de travail.

### Tests a ajouter

1. Cas Fr / Ra / Lr
- verifier que Fr reste coherent avec le bloc s lourd,
- verifier que Ra sert de point de controle sur une zone dense/intermediaire,
- verifier que Lr force une lecture structurelle de type D3 ou bloc.

2. Saturation de la loi compacte
- reprendre la forme de travail sur les tres lourds,
- verifier que la pente ne peut pas etre prolongee comme loi universelle,
- conserver la falsification de la forme brute comme resultat attendu.

3. Structure Omega(Z)
- garder Omega(Z) comme hypothese de lecture,
- verifier que la torsion, la courbure et le rayon interne restent des variables de modele,
- ne pas classer la relation comme loi valide avant un protocole distinct.

4. Controle de bord
- comparer les cas lourds avec les cas deja supportes,
- tracer la rupture entre regime atomique simple, regime structural et regime dense,
- conserver la trace des cas limites sans les forcer dans un seul canal.

### Statut de ces ajouts

Ces ajouts ne remplacent pas les tests deja validates. Ils prolongent seulement le protocole pour la zone lourde de la table, a partir du texte Electron-5.

### Protocole executable

Le bloc suivant transforme les cas lourds en tests exploitables sans presumer d'une loi universelle.

| Cas | Hypothese de travail | Test minimal | Attendu |
| --- | --- | --- | --- |
| Fr | bloc s lourd compatible avec la continuation du regime atomique | verifier que D1 reste le canal principal et que la lecture reste stable sans forcer D3 | supporte, sans extension universelle |
| Ra | zone intermediaire / dense de controle | verifier que la lecture ne se reduit pas a D1 seul et que D4 peut devenir visible sans dominer partout | partiel ou supporte selon le protocole |
| Lr | lecture structurelle necessaire | verifier qu'une simple extrapolation monotone echoue et qu'une lecture de type D3 / bloc est requise | falsifie la forme brute, structure maintenue |

Ce protocole sert de passerelle vers une suite de tests dediee. Il garde la distinction entre observation locale et loi generale.

### Saturation de la loi compacte

La loi compacte m(l) = A(l + 1/2) reste ici une approximation locale. Le point a tester est sa saturation: au-dela d un certain domaine, une pente unique ne doit plus suffire a decrire a la fois les familles simples et les cas lourds.

#### Hypothese de travail

- la forme compacte peut etre utile sur un petit intervalle de reference,
- la constante A n est pas censee rester stable sur toutes les familles,
- les residus doivent augmenter quand on pousse vers les cas lourds ou vers les transitions de bloc,
- une lecture a deux couches peut ameliorer l ajustement sans pour autant rendre la loi brute universelle.

#### Mesures et seuils

Pour garder le test lisible, on mesure les ecarts avec les indicateurs suivants:

- residu relatif: |m_obs - m_fit| / m_obs,
- derive locale: difference entre la pente du premier segment et celle du dernier segment,
- stabilite de A: variation de A quand on change de famille,
- gain structurel: baisse du residu quand on passe de la loi compacte brute a une lecture a deux couches.

Seuils de lecture:

- saturation locale: residu relatif > 0.10 sur au moins un point de controle,
- saturation nette: derive locale > 0.25 entre debut et fin de famille,
- saturation forte: stabilite de A > 0.15 entre familles,
- confirmation structurelle: gain structurel > 0.05 par rapport a la loi compacte brute.

#### Protocole executable

| Cas | Hypothese de travail | Mesure | Seuil / Attendu |
| --- | --- | --- | --- |
| Famille reguliere de controle | la loi compacte reste lisible localement | residu relatif moyen sur une famille simple | support local si residu relatif <= 0.10 |
| Limite haute d une famille | la pente se degrade quand Z augmente | derive locale entre debut et fin de famille | saturation nette si derive locale > 0.25 |
| Bloc f / lanthanides | la loi brute casse sur la structure interne | stabilite de A et gain structurel face a une lecture core / valence | saturation forte si A varie de plus de 0.15 et gain structurel > 0.05 |
| Trio lourd Fr / Ra / Lr | l extrapolation lineaire ne doit pas survivre telle quelle | residu relatif et echec du prolongement monotone | echec attendu si residu relatif > 0.10 ou si l extrapolation brute se replie |

#### Critere de saturation

- residus croissants avec le poids atomique ou avec le changement de bloc,
- perte de stabilite de A quand on change de famille,
- apparition d un gain net pour une lecture structurelle par rapport a la loi compacte brute,
- impossibilite de convertir la loi compacte en loi universelle sans protocole supplementaire.

#### Statut attendu

Ces tests ne servent pas a sauver la loi compacte. Ils servent a delimiter son domaine local et a documenter sa saturation quand on passe aux familles lourdes.

### Structure Omega(Z)

Omega(Z) reste ici une hypothese de lecture, pas une loi acquise. L objectif est de tester si la description par torsion, courbure et rayon interne apporte un gain explicatif reel sur les cas lourds, sans forcer une universalite prematuree.

#### Hypothese de travail

- Omega(Z) peut servir de variable de controle sur les zones lourdes,
- la torsion doit capter une partie de la structure que m(l) ne voit pas,
- la courbure doit augmenter la resolution entre blocs voisins,
- le rayon interne doit rester distinct du simple rayon effectif et ne pas etre absorbe par une pente unique.

#### Mesures et seuils

Pour le protocole, on suit les variables suivantes:

- torsion residuelle: ecart entre la torsion observee et la torsion attendue par un ajustement monotone,
- courbure locale: variation seconde sur une famille ordonnee,
- rayon interne normalise: rayon interne divise par le rayon effectif,
- gain Omega: baisse du residu quand on ajoute Omega(Z) a la lecture de base.

Seuils de lecture:

- Omega local utile: gain Omega > 0.05 sur une famille lourde,
- Omega structurel net: torsion residuelle non nulle et courbure locale > 0.10,
- Omega distinct: rayon interne normalise sort d une bande de 0.90 a 1.10,
- Omega valide seulement si la lecture brute laisse encore un residu visible apres ajustement.

#### Protocole executable

| Cas | Hypothese de travail | Mesure | Seuil / Attendu |
| --- | --- | --- | --- |
| Famille lourde de controle | Omega(Z) apporte un surcroît de lecture | gain Omega et residu apres ajustement | support local si gain Omega > 0.05 |
| Transition de bloc | torsion et courbure deviennent visibles | torsion residuelle et courbure locale | Omega structurel net si torsion residuelle non nulle et courbure locale > 0.10 |
| Rayon interne | ne pas confondre rayon interne et rayon effectif | rayon interne normalise | Omega distinct si la valeur sort de la bande 0.90-1.10 |
| Cas Fr / Ra / Lr | Omega(Z) doit mieux distinguer les cas lourds que la seule forme compacte | comparer le residu brut et le residu avec Omega | support partiel ou support local si le residu baisse clairement |

#### Critere de validation

- Omega(Z) est utile si elle améliore la lecture sans annuler le residu,
- Omega(Z) est structurelle si elle distingue au moins deux familles lourdes voisines,
- Omega(Z) reste invalide comme loi universelle tant qu un protocole distinct ne confirme pas sa stabilite inter-familles.

#### Statut attendu

Ce bloc sert a tester une lecture structurelle locale. Il ne valide pas Omega(Z) comme forme generale; il la garde seulement comme hypothese executable sur les cas lourds.

### Controle de bord

Le controle de bord sert a verifier que les cas lourds ne sont pas absorbes artificiellement par un seul canal de lecture. Il doit maintenir la distinction entre regime atomique simple, regime structural et regime dense.

#### Hypothese de travail

- les cas lourds Fr, Ra et Lr ne se lisent pas tous dans le meme canal,
- le regime atomique simple reste domine par D1,
- le regime structural demande une lecture supplementaire de type bloc ou Omega(Z),
- le regime dense doit afficher D4 comme canal dominant sans effacer les autres traces locales.

#### Mesures et seuils

On surveille les ecarts suivants:

- indice de bord: difference entre la meilleure lecture locale et la lecture forcee par extrapolation,
- separation de regime: capacite a distinguer D1, D3 / bloc et D4,
- trace de limite: presence d un cas qui reste partiellement lisible mais refuse la lecture brute,
- robustesse locale: stabilite de la lecture quand on retire un voisin de comparaison.

Seuils de lecture:

- bord atomique: indice de bord < 0.10 et D1 reste dominant,
- bord structural: indice de bord entre 0.10 et 0.25 avec besoin d une lecture complementaire,
- bord dense: D4 devient dominant et la separation de regime reste visible,
- bord non force: aucun cas limite ne doit etre classe dans un seul canal si la lecture alternative gagne clairement.

#### Protocole executable

| Cas | Hypothese de travail | Mesure | Seuil / Attendu |
| --- | --- | --- | --- |
| Fr | bord atomique lourd | indice de bord et domination de D1 | bord atomique si D1 reste dominant et indice de bord < 0.10 |
| Ra | bord structural | indice de bord et besoin d un canal supplementaire | bord structural si indice entre 0.10 et 0.25 |
| Lr | bord vers la lecture dense / structurelle | separation de regime et gain d une lecture complementaire | bord non force si la lecture brute echoue et qu une lecture additionnelle est requise |
| Cas de controle compare | ne pas confondre les cas limites avec les regimes deja supportes | robustesse locale face a la suppression d un voisin | attente: distinction conservee entre regime atomique, structural et dense |

#### Critere de validation

- le bord est valide si les cas lourds se repartissent entre au moins deux zones de lecture,
- le bord est utile si la lecture alternative gagne sans effacer le signal local,
- le bord echoue si tous les cas lourds se retrouvent forces dans un seul canal sans gain explicatif.

#### Statut attendu

Ce bloc ne cherche pas a unifier les cas limites. Il fixe seulement une frontiere d interpretation entre les regimes deja identifies et les lectures concurrentes.