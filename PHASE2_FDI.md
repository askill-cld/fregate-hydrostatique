# Phase 2 : carène aux dimensions principales de la FDI (Kimon, F-601)

Pour reproduire les résultats :

```bash
python calage.py fregate_phase2_fdi kv
python main.py fregate_phase2_fdi
```

Les paramètres sont dans `navires.py` (jeu `FREGATE_PHASE2_FDI`), les résultats
dans `resultats_fregate_phase2_fdi.json`, les figures dans
`figures/fregate_phase2_fdi/` et les fichiers CAO dans `exports/fregate_phase2_fdi/`.

## 1. Ce que représente cette carène

C'est une **carène paramétrique** (famille de Wigley, définie dans `carene.py`)
dont la longueur, la largeur et le déplacement sont ceux publiés pour la
frégate de défense et d'intervention (FDI), classe à laquelle appartient le
Kimon (F-601), construit par Naval Group à Lorient.

Ce n'est **pas la carène de la FDI**. Son plan de formes n'est pas public. Le
modèle ne représente ni l'étrave inversée, ni le dôme sonar, ni l'évasement
des flancs, ni les appendices.

L'objectif est d'appliquer l'outil de la phase 1 à un navire réel de taille
connue, avec des hypothèses explicites et chiffrées, et de mesurer ce que ces
hypothèses changent aux résultats.

## 2. Sources

| Grandeur | Valeur | Source | Date | Lien |
|---|---|---|---|---|
| Longueur hors tout | 122 m | Naval Group, communiqué « Naval Group delivers the first defence and intervention frigate » | 20/10/2025 | [naval-group.com](https://naval-group.com/en/presse/naval-group-delivers-first-defence-and-intervention-frigate) |
| Largeur (« Width ») | 18 m | idem | 20/10/2025 | idem |
| Déplacement | 4 500 t, état de chargement non précisé | idem | 20/10/2025 | idem |
| Longueur hors tout | 122 m | Ministère des Armées, page « Defense and Intervention Frigate » | non datée, consultée le 26/10/2026 | [defense.gouv.fr](https://www.defense.gouv.fr/en/defense-and-intervention-frigate) |
| Largeur hors tout | 17,7 m | idem | idem | idem |
| Déplacement | 4 500 t, état de chargement non précisé | idem | idem | idem |

Remarques :

- Les deux sources officielles ne donnent pas la même largeur (18 m, valeur
  arrondie, et 17,7 m). La valeur du constructeur, 18 m, est retenue. Avec
  17,7 m, le tirant d'eau déduit (section 3) serait de 4,52 m au lieu de 4,44 m.
- Les chiffres publiés concernent la classe FDI. La version grecque (FDI HN),
  dont fait partie le Kimon, peut différer légèrement.
- Aucune source fiable ne donne le **tirant d'eau**, le **creux** ni le **KG**.
- Wikipédia (page « Greek frigate Kimon ») donne 121,6 m, 17,7 m, un tirant
  d'eau de 6,2 m et 4 603 t, sans référence pour ces chiffres. Ils ne sont pas
  utilisés.
- Janes parlerait de déplacement « standard ». L'article n'a pas été consulté
  directement : à vérifier avant de le citer.

## 3. Hypothèses

| Grandeur | Valeur retenue | Justification |
|---|---|---|
| L | 122 m | Longueur hors tout utilisée comme longueur entre perpendiculaires (ce qu'attend `Carene`). La carène modélisée est donc plus longue que la carène immergée réelle. |
| B | 18 m | Largeur maximale utilisée comme largeur à la flottaison. La FDI ayant des flancs évasés, sa largeur à la flottaison est plus faible. |
| Cb visé | 0,45 | Ordre de grandeur pour une frégate. **Source à trouver** (manuel d'architecture navale). |
| T | 4,44 m | Déduit du déplacement publié : T = ∇ / (Cb · L · B) = 4 390 / (0,45 × 122 × 18) = 4,44 m, avec ∇ = Δ / ρ = 4 500 / 1,025 = 4 390 m³. |
| D | 9 m | Environ 2 × T, même règle que la phase 1. D n'intervient pas dans l'hydrostatique du navire droit (intégration de 0 à T), seulement dans la courbe GZ aux grands angles. |
| KG | 5,4 m | 0,6 × D, même règle que la phase 1. Valeur non publiée : le GM qui en découle est conditionnel (section 6). |
| ρ | 1,025 t/m³ | Eau de mer, comme en phase 1. |
| État de chargement | non précisé | Les 4 500 t sont traités comme le déplacement du cas étudié, sans hypothèse sur l'état de chargement. |

L, B, T et Cb sont liés par L · B · T · Cb = ∇, qui est fixé par le déplacement
publié. Un premier essai avec le tirant d'eau de Wikipédia (6,2 m), L = 122 m et
B = 18 m donnait Cb = 0,32, une valeur invraisemblable pour une frégate. Ce
tirant d'eau a donc été écarté au profit d'un T déduit d'un Cb typique.

## 4. Calage

**Pourquoi caler.** Une fois L, B et T fixés, le déplacement publié impose
Cb = ∇ / (L · B · T) = 0,4503 (T étant arrondi à 4,44 m). La carène de Wigley
d'origine (`kp = 1`, `kv = 2`) a un Cb de 0,444 et donne 4 442 t, soit −1,29 %.

**Deux réglages, une contrainte.** Dans ce modèle, la demi-largeur est un
produit b(x, z) = (B/2) · P(x) · V(z), donc Cb = Cp × Cm :

- `kp` règle P(x), c'est-à-dire la finesse des extrémités, donc Cp et la
  flottaison (Cw, inertie It, donc BM) ;
- `kv` règle V(z), c'est-à-dire la forme des sections, donc Cm et KB, sans
  toucher à la flottaison.

Le déplacement ne fixe que le produit des deux : le choix du réglage est une
hypothèse supplémentaire.

**Méthode.** `calage.py` cherche par dichotomie la valeur du réglage qui donne
4 500 t. La fonction `cale_forme()` vérifie d'abord que la cible est encadrée
par les bornes de recherche, puis réduit l'intervalle en gardant à chaque tour
la moitié où l'écart au déplacement publié change de signe. Cette règle
fonctionne quel que soit le sens de variation : le déplacement augmente avec
`kv` mais diminue avec `kp`.

**Les deux calages possibles :**

| | Calage sur `kv` (retenu) | Calage sur `kp` |
|---|---|---|
| Valeur | kv = 2,0808 | kp = 0,9541 |
| Déplacement | 4 500,0 t | 4 500,0 t |
| Cp / Cm / Cw | 0,667 / 0,675 / 0,667 | 0,675 / 0,667 / 0,675 |
| KB | 2,764 m | 2,775 m |
| BMt | 6,174 m | 6,290 m |
| KMt | 8,938 m | 9,065 m |
| GMt (KG = 5,4 m) | 3,538 m | 3,665 m |

**Choix : `kv = 2,0808`.** La carène de Wigley a un coefficient de maître-couple
faible (0,667), et ce calage le fait monter. Il laisse la flottaison intacte et
donne le KM le plus bas des deux, donc le GM le plus prudent.

**Écart restant :** 4 500,02 t calculées pour 4 500 t publiées, soit +0,0005 %.

**Sensibilité :** le seul choix du réglage de calage fait varier KM de 0,13 m.

## 5. Limites du modèle

- **Flancs verticaux au-dessus de la flottaison**, alors que la FDI a des
  flancs évasés. Dans le modèle, le livet de pont s'immerge vers 27° de gîte
  (atan((D − T) / (B/2)) avec D = 9 m, T = 4,44 m, B = 18 m). Sur le navire
  réel, l'évasement retarde cette immersion : la courbe GZ du modèle est
  vraisemblablement sous-estimée aux grands angles.
- **Formes de carène** de la famille de Wigley, symétriques entre l'avant et
  l'arrière (LCB = LCF = 0). Sur un vrai navire, le centre de carène est
  généralement décalé.
- **Étrave inversée, dôme sonar, appendices** (safrans, lignes d'arbres,
  ailerons stabilisateurs) et superstructures ne sont pas modélisés.
- **Dimensions hors tout** utilisées comme dimensions de carène (section 3) :
  L et B sont surestimés, ce qui surestime BM (BM varie comme B² / T).
- **KG non publié** : le GM dépend entièrement de cette hypothèse (section 6).
- **Stabilité à l'état intact**, en gîte pure, sans assiette libre, avec une
  coque supposée étanche jusqu'au pont (comme en phase 1).

## 6. Résultats

Calcul avec le jeu `FREGATE_PHASE2_FDI` calé (`kv = 2,0808`), comparé à la
frégate de la phase 1.

| Grandeur | Phase 1 (fictive) | FDI (calée) |
|---|---|---|
| L × B × T | 100 × 14 × 4,5 m | 122 × 18 × 4,44 m |
| Volume immergé ∇ | 2 800 m³ | 4 390 m³ |
| Déplacement Δ | 2 870 t | 4 500 t |
| Cb / Cp / Cm / Cw | 0,444 / 0,667 / 0,667 / 0,667 | 0,450 / 0,667 / 0,675 / 0,667 |
| KB | 2,81 m | 2,76 m |
| BMt | 3,73 m | 6,17 m |
| **KMt** | **6,55 m** | **8,94 m** |
| GMt (KG = 5,4 m) | 1,15 m | 3,54 m |
| TPC | 9,6 t/cm | 15,0 t/cm |
| GZ max | 0,59 m à 45° | 1,50 m à 40° |
| Angle d'annulation | 83° | 85° |
| Aire sous GZ jusqu'à 30° | 0,134 m·rad | 0,408 m·rad |
| Aire sous GZ jusqu'à 40° | 0,226 m·rad | 0,661 m·rad |

**KM est le résultat robuste, GM est conditionnel.** KM = KB + BM ne dépend que
de la géométrie. GM = KM − KG dépend entièrement du KG supposé. À titre
d'illustration, avec KM = 8,94 m :

| KG supposé | 5,4 m | 6,5 m | 7,5 m |
|---|---|---|---|
| GMt | 3,54 m | 2,44 m | 1,44 m |

Le GM de 3,54 m obtenu avec KG = 5,4 m est donc à lire comme « GM pour ce KG »,
pas comme le GM de la FDI. Il est élevé pour deux raisons : la carène est large
par rapport à son tirant d'eau (B/T = 4,05 contre 3,11 en phase 1, et BM varie
comme B² / T), et le KG reprend la règle d'un navire fictif plus petit.

**Validation.**

- GM hydrostatique : 3,538 m. Pente de la courbe GZ mesurée à 1° : 3,536 m
  (écart 0,06 %).
- La pente mesurée entre 0 et 5° (affichée par `main.py`) vaut 3,493 m
  (−1,3 %, même écart relatif qu'en phase 1). Ce n'est pas une erreur de
  précision : un maillage cinq fois plus fin donne la même valeur. La courbe
  s'infléchit déjà entre 0 et 5°, parce que les sections de Wigley se
  rétrécissent sous la flottaison, et que le flanc qui émerge atteint vite
  cette partie rétrécie sur une carène large et peu profonde.
- Pour la même raison, la formule des murailles droites s'écarte de la courbe
  GZ dès 10° environ.

**Courbe GZ.** L'immersion du livet de pont (vers 27°) marque le point
d'inflexion de la courbe : GZ continue de croître, mais moins vite, et atteint
son maximum à 40°, plus tôt qu'en phase 1 (45°).

Figures : `figures/fregate_phase2_fdi/` (plan des formes, courbe des aires,
vue 3D, courbe GZ).

## 7. Suite

- Trouver une source pour le Cb typique d'une frégate (hypothèse de T).
- Rendus SolidWorks à partir de `exports/fregate_phase2_fdi/`, et comparaison
  du volume et du centre de carène donnés par les propriétés de masse avec
  ∇ = 4 390 m³ et KB = 2,76 m (troisième méthode indépendante).
