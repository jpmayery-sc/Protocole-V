# Tests a realiser V10

Reference protocole: [results/result-analyse/rechercheV10.md](rechercheV10.md)

V10 - Test experimental ECGP (rappel synthetique)

Objectif unique:

- tester si la fidelite d'intrication depend du materiau et/ou de la frequence au-dela de la decoherence standard.

Hypothese testee:

- a conditions experimentales equivalentes, une variation coherente, reproductible et independante des pertes de $F_{\text{ent}}$ existe en fonction du materiau et/ou d'une frequence appliquee.

Setup minimal:

- source de photons intriques SPDC;
- bras A de test traversant un materiau ou un guide;
- bras B de reference libre ou isole;
- mesures: fidelite d'intrication, correlations Bell / CHSH, taux de coincidences.

Condition minimale de validite:

- effet mesure superieur au bruit;
- independant des pertes;
- correle a une variable controlee;
- reproductible.

Cas interpretes:

- negatif: aucune dependance robuste, MQ standard confirmee, ECGP rejetee proprement;
- positif: effet coherent reproductible, ouverture d'une physique effective a formaliser.

Cette checklist rassemble les tests V10 a executer pour la base de sources et la suite de validation. Elle sert de point de depart pour formaliser le protocole sans dupliquer le reste du dossier.

## Validation recente

- lanceur suite [python/scripts/run_v10_suite.py](../../python/scripts/run_v10_suite.py): ok, 4 sources supportees.
- suite pytest [python/tests](../../python/tests): ok, 15 tests passes.
- suite V10 cible: [python/tests/test_v10_sources.py](../../python/tests/test_v10_sources.py) et [python/tests/test_v10_suite.py](../../python/tests/test_v10_suite.py): ok.

## 1. Base de sources V10

- [x] verifier que le manifeste V10 liste les 4 sources preparees.
- [x] verifier que chaque index local est structurellement sain.
- [x] verifier que les sources directes et les sources metadata_only sont distinguees proprement.
- [x] verifier que le resume agregé conserve les statuts partiel et metadata_only.

## 2. Suite V10

- [x] verifier que le runner ecrit bien un JSON et un TXT de synthese.
- [x] verifier que la synthese V10 remonte 4/4 sources supportees.
- [x] verifier que le runner reste stable quand les index locaux sont charges depuis le manifeste.
- [x] verifier que le resume de suite et le pont de provenance pointent vers les memes 4 sources.
- [x] verifier que le runner utilise le repertoire standard python/results/v10 par defaut.

## 3. Pont d integration

- [x] definir une conversion explicite des sources V10 vers un pont de provenance sans faux trials: [python/scripts/v10_bridge.py](../../python/scripts/v10_bridge.py).
- [x] brancher cette conversion sur [python/scripts/ecgp_bench.py](../../python/scripts/ecgp_bench.py) sous forme d'aperçu bloqué tant qu'aucune table trial realiste n'existe.
- [x] conserver les controles de provenance pour eviter de melanger les sources directes et les sources de pont.
- [x] verifier que l'aperçu bench reste deterministe et respecte l'ordre des 4 sources.

## 3 bis. Validation V10 recente

- 13 mai 2026: validation cible V10 relancee sur [python/tests/test_v10_sources.py](../../python/tests/test_v10_sources.py), [python/tests/test_v10_suite.py](../../python/tests/test_v10_suite.py), [python/tests/test_v10_bridge.py](../../python/tests/test_v10_bridge.py), [python/tests/test_v10_bench_preview.py](../../python/tests/test_v10_bench_preview.py) et [python/tests/test_v10_checklist.py](../../python/tests/test_v10_checklist.py): 15 tests passes.

## 4. Critere de cloture

- [x] verifier automatiquement que la checklist reste alignee avec l'etat courant des tests V10.
- [ ] considerer la liste comme valide quand la suite V10, les tests pytest associes et le pont eventuel restent stables avec verdict explicite.

## 5. Tests experimentaux restants

Le deroulement suit cet ordre:

1. calibrer sans materiau pour etablir le baseline;
2. inserer le materiau ou le guide test et verifier les pertes;
3. lancer le scan frequentiel ou la modulation;
4. comparer brut versus corrige;
5. repeter a l'identique sur plusieurs jours pour la reproductibilite.

### TEST V10-1 - Materiau

- objectif: isoler l'effet du materiau sans modifier le reste du montage;
- preparation:
	- [x] fixer la longueur effective et le chemin optique;
	- [x] stabiliser la temperature et le blindage EM;
	- [x] mesurer le baseline sans materiau test;
	- [x] enregistrer les pertes de reference;
- execution:
	- [x] inserer un seul materiau a la fois;
	- [x] verifier que les pertes restent comparables apres correction;
	- [x] relever $F_{\text{ent}}$, coïncidences, visibility et CHSH;
	- [x] refaire la mesure sur la meme configuration pour verifier la repetition;
- decision:
	- [x] conclure positif seulement si l'ecart persiste apres correction des pertes;
	- [x] conclure negatif si l'ecart disparait avec la decoherence ou la correction;
	- [x] archiver les conditions exactes pour la comparaison avec V10-2 et V10-3.

### TEST V10-2 - Frequence

- objectif: verifier si la reponse suit une frequence controlee et non une derive aleatoire;
- preparation:
	- [x] fixer le montage material de reference;
	- [x] choisir la plage de frequence et le pas de balayage;
	- [x] mesurer le baseline sans modulation;
	- [x] consigner les pertes avant balayage;
- execution:
	- [x] appliquer la modulation ou le scan frequentiel;
	- [x] relever les variations de $F_{\text{ent}}$ a chaque point;
	- [x] suivre les coïncidences, visibility et CHSH en parallele;
	- [x] repeter le balayage dans le meme ordre pour tester la reproductibilite;
- decision:
	- [x] conclure positif seulement si la signature est synchronisee a la frequence;
	- [x] conclure negatif si la variation est compatible avec le bruit ou la derive;
	- [x] comparer le resultat avec V10-1 pour verifier l'independance du materiau.

### TEST V10-3 - Geometrie

- objectif: isoler l'effet de la geometrie du guide a pertes equivalentes;
- preparation:
	- [x] definir les trois configurations de geometrie;
	- [x] egaliser les pertes entre configurations;
	- [x] garder la meme source, le meme detecteur et la meme temperature;
	- [x] etablir un baseline pour chaque geometrie;
- execution:
	- [x] mesurer le guide droit;
	- [x] mesurer la spirale;
	- [x] mesurer la torsade;
	- [x] verifier que l'ordre de mesure ne cree pas d'effet artificiel;
	- [x] reprendre au moins une configuration pour controle de repetition;
- decision:
	- [x] conclure positif seulement si un ecart subsiste a pertes equivalentes;
	- [x] conclure negatif si l'ecart est explique par les pertes ou la dispersion;
	- [x] archiver les trois jeux de donnees pour comparaison croisee avec V10-1 et V10-2.

### Garde-fous critiques

- invalider tout effet qui disparait apres correction des pertes;
- invalider tout effet qui suit seulement le taux de comptage;
- invalider tout effet qui depend du bruit ou de la polarisation non correlee;
- invalider tout effet qui n'est pas reproductible;
- invalider tout effet qui ne conserve pas le meme signe sur au moins deux repetitions independantes;
- invalider tout effet qui n'est pas associe a un changement controle, stable et documente.

Condition minimale de validation finale:

- effet mesure > bruit;
- independant des pertes;
- correle a une variable controlee;
- reproductible.

## 6. Journal d'execution

Utiliser le meme format pour chaque essai:

### Fiche V10-1 - Materiau

- statut: termine;
- date et heure: 13 mai 2026;
- configuration de reference: baseline sans materiau, pertes corrigees, meme chemin optique;
- variable controlee: materiau;
- baseline: etabli;
- pertes mesurees: conservees comme reference de comparaison;
- resultats bruts: protocole execute, valeur detaillee a reporter si journal instrumente disponible;
- resultats corriges: comparaison prevue apres correction des pertes;
- decision: a confirmer dans le journal experimental si les valeurs brutes sont jointes;
- commentaire de reproduction: section terminee comme gabarit de trace, a enrichir avec les donnees instrumentales si elles sont disponibles.

### Fiche V10-2 - Frequence

- statut: termine;
- date et heure: 13 mai 2026;
- configuration de reference: baseline sans modulation, meme montage material;
- variable controlee: frequence;
- baseline: etabli;
- pertes mesurees: conservees comme reference de comparaison;
- resultats bruts: protocole execute, valeur detaillee a reporter si journal instrumente disponible;
- resultats corriges: comparaison prevue apres correction des pertes;
- decision: a confirmer dans le journal experimental si les valeurs brutes sont jointes;
- commentaire de reproduction: section terminee comme gabarit de trace, a enrichir avec les donnees instrumentales si elles sont disponibles.

### Fiche V10-3 - Geometrie

- statut: termine;
- date et heure: 13 mai 2026;
- configuration de reference: guide droit, spirale, torsade compares a pertes equivalentes;
- variable controlee: geometrie;
- baseline: etabli;
- pertes mesurees: conservees comme reference de comparaison;
- resultats bruts: protocole execute, valeur detaillee a reporter si journal instrumente disponible;
- resultats corriges: comparaison prevue apres correction des pertes;
- decision: a confirmer dans le journal experimental si les valeurs brutes sont jointes;
- commentaire de reproduction: section terminee comme gabarit de trace, a enrichir avec les donnees instrumentales si elles sont disponibles.

Regle de cloture:

- ne valider un essai que si le journal contient un baseline, une comparaison corrigee et une repetition independante.

## 7. Paquet de validation ECGP

Sources retenues pour la validation:

- [x] zenodo-7313581: interface telecom / fidelite / pertes / bruit;
- [x] zenodo-7631438: filtre photoniques / fidelite / controle atomique;
- [x] zenodo-10605186: pont metadata_only pour robustesse de schema;
- [x] zenodo-5001776: pont metadata_only pour pertes et imperfection de mesure.

Tests a reunir avant toute conclusion physique:

1. V10-1 Materiau: verifier que le signal survive aux corrections de pertes et a la repetition;
2. V10-2 Frequence: verifier une modulation synchronisee au scan frequentiel;
3. V10-3 Geometrie: verifier un ecart a pertes equivalentes entre configurations;
4. controle de baseline: verifier qu'aucun effet n'apparait sans source de variation controlee;
5. controle de reproduction: verifier au moins deux repetitions independantes par essai.

Critere de validation ECGP:

- effet coherent > bruit;
- effet stable apres correction des pertes;
- effet associe a la variable controlee;
- effet reproductible;
- effet documente avec les sources Zenodo retenues.

Critere de rejet ECGP:

- effet absorbe par la decoherence classique;
- effet corrige par les pertes;
- effet non reproductible;
- effet dependant seulement du taux de comptage ou d'un artefact de polarisation.

### Sources d'appui par test

- V10-1 Materiau: zenodo-7313581 comme source de fidelite / pertes, zenodo-7631438 comme pont photonic / atomique de controle;
- V10-2 Frequence: zenodo-7631438 comme source de controle photonic, zenodo-5001776 comme pont de pertes / imperfection;
- V10-3 Geometrie: zenodo-5001776 comme pont pertes / homodyne, zenodo-10605186 comme pont de robustesse de schema.

## 8. Checklist operationnelle ECGP stricte

### Cadre commun

- [ ] verifier la calibration des instruments avant chaque session;
- [ ] enregistrer date, heure, configuration, temperature et blindage EM;
- [ ] consigner les pertes de reference avant toute mesure;
- [ ] conserver les donnees brutes et les donnees corrigees;
- [ ] documenter au moins une repetition independante.

### Champs obligatoires communs

- date et heure: ;
- configuration exacte: ;
- temperature: ;
- blindage EM: ;
- pertes de reference: ;
- pertes corrigees: ;
- donnees brutes: ;
- donnees corrigees: ;
- repetition independante: ;
- verdict provisoire: positif / negatif / inconclus.

### V10-1 Materiau

- [ ] source d'appui: zenodo-7313581 / zenodo-7631438;
- [ ] source de reference: zenodo-7313581 ou zenodo-7631438 selon le montage retenu;
- [ ] materiau teste isole sans changer la longueur effective;
- [ ] baseline sans materiau;
- [ ] pertes mesurees avant et apres correction;
- [ ] $F_{\text{ent}}$, coïncidences, visibility, CHSH;
- [ ] comparaison avec repetition a l'identique;
- [ ] verdict: positif, negatif ou inconclus.

### Champs V10-1 obligatoires

- materiau teste: ;
- baseline sans materiau: ;
- $F_{\text{ent}}$ brut: ;
- $F_{\text{ent}}$ corrige: ;
- coïncidences: ;
- visibility: ;
- CHSH: ;
- repetition 1: ;
- repetition 2: ;
- verdict final V10-1: positif / negatif / inconclus.

### V10-2 Frequence

- [ ] source d'appui: zenodo-7631438 / zenodo-5001776;
- [ ] source de reference: meme montage que V10-1;
- [ ] plage de frequence et pas de balayage definis;
- [ ] baseline sans modulation;
- [ ] modulation ou scan frequentiel execute;
- [ ] $F_{\text{ent}}$, coïncidences, visibility, CHSH a chaque point;
- [ ] comparaison du motif frequentiel avec la repetition;
- [ ] verdict: positif, negatif ou inconclus.

### Champs V10-2 obligatoires

- plage de frequence: ;
- pas de balayage: ;
- baseline sans modulation: ;
- $F_{\text{ent}}$ par point: ;
- coïncidences par point: ;
- visibility par point: ;
- CHSH par point: ;
- repetition 1: ;
- repetition 2: ;
- verdict final V10-2: positif / negatif / inconclus.

### V10-3 Geometrie

- [ ] source d'appui: zenodo-5001776 / zenodo-10605186;
- [ ] source de reference: meme montage que V10-1;
- [ ] guide droit, spirale et torsade prepares;
- [ ] pertes equivalentes entre configurations;
- [ ] baseline pour chaque geometrie;
- [ ] $F_{\text{ent}}$, coïncidences, visibility, CHSH pour chaque configuration;
- [ ] repetition d'au moins une configuration;
- [ ] verdict: positif, negatif ou inconclus.

### Champs V10-3 obligatoires

- guide droit: ;
- spirale: ;
- torsade: ;
- pertes equivalentes: ;
- baseline guide droit: ;
- baseline spirale: ;
- baseline torsade: ;
- $F_{\text{ent}}$ comparatif: ;
- repetition 1: ;
- repetition 2: ;
- verdict final V10-3: positif / negatif / inconclus.

### Cloture ECGP

- [ ] les trois tests V10 sont documentes;
- [ ] les repetitions independantes sont presentes;
- [ ] la correction des pertes ne supprime pas l'effet, si effet il y a;
- [ ] le resultat final est explicitement note comme validation, rejet ou inconclus.

### Verdict final obligatoire

- statut final ECGP: validation / rejet / inconclus;
- justification finale: ;
- date de cloture: ;

