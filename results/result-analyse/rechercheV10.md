# Rapport V10 - Statut experimental cible de l'ECGP

Note de test associee: [results/result-analyse/TestV10.md](TestV10.md)

## Finalite de V10

V10 ne cherche pas a conclure par principe sur l'ECGP.
V10 cherche a savoir si une dependance materiau / frequence de la fidelite d'intrication existe au-dela des effets de decoherence deja connus.

Le point teste est unique:

- la MQ standard suffit-elle a expliquer toute variation observee, ou reste-t-il un effet coherent a tester experimentalement ?

## Contraintes experimentales incontournables

V10 ne doit pas seulement regarder une fidelite; il doit separer un vrai effet coherent des artefacts classiques.

### A. Controle absolu des pertes

Toute variation de $F_{\text{ent}}$ doit etre verifiee en parallele avec:

- le taux de comptage, notamment les coïncidences;
- la visibility des interferences;
- la fidelite quantique ou la concurrence.

Lecture attendue:

- si la fidelite varie mais pas les pertes, l'effet reste candidat;
- si la fidelite suit les pertes, il s'agit d'une decoherence classique ou d'un artefact de couplage.

### B. Synchronisation frequence -> signal

Le coeur du test est une reponse de $F_{\text{ent}}$ synchronisee avec une variable controlee, par exemple:

- modulation sinusoïdale d'un champ EM;
- scan frequentiel impose;
- autre excitation periodique reproductible.

Signature attendue:

- pic ou creux a une frequence specifique;
- reproductibilite du signal;
- independance vis-a-vis des pertes.

### C. Replicabilite interne avant tout exterieur

Le meme dispositif, les memes parametres, et des repetitions sur plusieurs jours doivent retrouver le signal avant toute lecture forte.

Lecture attendue:

- si le signal disparait, il s'agit d'un artefact;
- s'il reste, il devient un candidat physique.

### D. Design minimal robuste

Le protocole minimal doit rester simple:

- source SPDC, de preference type-II;
- paire intriquee polarisee;
- un bras avec guide et materiau test;
- un bras de reference isole.

Ordre logique:

- calibration sans materiau;
- insertion du materiau et controle des pertes;
- scan frequentiel ou modulation;
- comparaison brute puis corrigee.

Condition de validation:

- effet superieur au bruit experimental;
- survit a la correction des pertes;
- est synchronise avec la variable controlee;
- est reproductible.

Sinon, rejet automatique.

## Ce que dit la MQ standard

Verdict: supported

Lecture:

- l'intrication ne depend pas du materiau en tant que tel;
- les variations attendues passent par des effets de pertes, de bruit, d'absorption ou de decoherence;
- une modulation coherente resonante du type ECGP n'est pas deduite de la MQ standard.

Conclusion locale:

- la MQ standard fixe le cadre de reference;
- elle ne fournit pas, a elle seule, une prediction positive de type ECGP.

## Ce que la proposition ECGP ajoute

Verdict: partiellement soutenu comme hypothese testable

Lecture:

- la proposition ECGP introduit une dependance faible mais mesurable de $F_{\text{ent}}$ au materiau et/ou a la frequence;
- cette dependance n'est pas imposee par la MQ standard;
- elle devient donc une hypothese experimentale autonome.

Conclusion locale:

- la proposition est testable;
- elle n'est pas deja demontree;
- elle ne peut pas etre confondue avec un simple rappel de decoherence.

## TEST V10-1 - Materiau pur

Verdict: a tester

Lecture attendue:

- si, a pertes, longueur, temperature et blindage egaux, la fidelite varie de maniere reproductible selon le materiau, l'effet devient non trivial;
- si toute variation disparait apres correction des pertes, l'ECGP est rejetee.

Conclusion locale:

- le test est decisif pour la composante materiau;
- sans variation robuste, il ne reste qu'un effet classique.

## TEST V10-2 - Frequence

Verdict: a tester

Lecture attendue:

- une modulation synchronisee de la fidelite autour d'une frequence imposee constituerait un signal coherent non standard;
- un bruit erratique ou une simple baisse de contraste resterait compatible avec la decoherence classique.

Conclusion locale:

- la frequence est le point cle pour distinguer signal coherent et perte ordinaire;
- le resultat doit etre reproductible et corrige des artefacts.

## TEST V10-3 - Geometrie

Verdict: a tester

Lecture attendue:

- une difference entre guide droit, spiralé ou torsade, a pertes equivalentes, indiquerait une dependance geometrique reelle;
- une absence d'effet affaiblirait l'idee que la geometrie du guide porte un canal de coherence specifique.

Conclusion locale:

- ce test ne suffit pas seul;
- il sert de controle de robustesse pour eviter une lecture trop locale du materiau.

## Gardes-fous

Verdict: necessaires

Lecture:

- tout effet qui disparait apres correction des pertes doit etre traite comme non specifique;
- tout effet qui suit seulement le taux de comptage doit etre traite comme artefact;
- tout effet qui depend de la polarisation sans coherence doit etre traite comme non concluant;
- tout resultat non reproductible inter-labo doit rester hors promotion physique.
- toute variation qui suit seulement le taux de detection doit etre traite comme artefact.

Conclusion locale:

- sans ces gardes-fous, V10 ne discrimine rien;
- avec eux, V10 devient un vrai test de statut.

## Synthese physique

V10 place l'ECGP dans une position epistemiquement propre:

- soit l'effet n'existe pas, et la MQ standard reste suffisante;
- soit un effet coherent reproductible survit aux corrections, et une nouvelle physique effective minimale devient serieusement envisageable.

Dans les deux cas, le test est utile.

## Verdict global

V10 est ouvert.

Ce qui est deja acquis:

- la MQ standard ne predit pas une modulation coherent materiau / frequence de type ECGP;
- une telle modulation ne peut donc pas etre fermee sans test experimental dedie.

Ce qui ne l'est pas:

- l'existence effective d'un canal de coherence non standard;
- la robustesse inter-labo d'un effet ECGP;
- la portee physique eventuelle d'une telle dependance.

## Conclusion finale

Le bon statut de l'ECGP est celui d'une hypothese experimentale falsifiable, pas celui d'une consequence deja contenue dans la MQ standard.

Elle doit donc rester:

- testable;
- corrigee des effets de decoherence;
- et decidee par resultat experimental, non par fermeture conceptuelle.

Regle de cloture:

- si V10 est negatif, la MQ standard est renforcee et l'ECGP est rejetee proprement;
- si V10 est positif, il faut reformuler le statut de l'effet comme physique effective candidate.

Lecture normative des resultats:

- cas negatif: aucune dependance coherente du materiau ou de la frequence ne subsiste apres correction des pertes; la MQ standard suffit;
- cas positif: un effet coherent reproductible depasse les pertes et necessite une modelisation effective, sans invoquer ECGP comme conclusion automatique.