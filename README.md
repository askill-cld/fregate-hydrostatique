# Carène de frégate — Outil d'hydrostatique et de stabilité

Outil d'architecture navale développé en Python : il génère une **carène de
frégate paramétrique**, calcule son **hydrostatique** (déplacement, centre de
carène, hauteur métacentrique GM) et trace sa **courbe de stabilité GZ(θ)**, puis
exporte la coque vers la CAO (Fusion 360 / SolidWorks).

> Projet personnel d'Ayoub — Licence Physique CUPGE (UBS Lorient).
> Objectif : projet personnel d'architecture navale pour candidature en école
> d'ingénieur (ENSTA, Centrale Nantes) et contacts industriels (Naval Group).

---

## Ce que fait le programme

1. Définit une carène de frégate par quelques paramètres (L, B, T, D).
2. Calcule toute l'hydrostatique du navire droit par la **méthode de Simpson**.
3. Calcule la **courbe de stabilité GZ(θ)** par intégration directe du volume
   immergé incliné, à déplacement constant.
4. Valide le calcul de deux façons indépendantes (GM par l'hydrostatique vs GM
   par la pente de la courbe GZ, et formule des murailles droites).
5. Génère 4 graphiques et 3 fichiers CAO.

## Résultats principaux (frégate L=100 m)

| Grandeur | Valeur |
|---|---|
| Déplacement | 2 870 t |
| Coefficient de bloc Cb | 0.444 (coque fine, typique frégate) |
| KB (centre de carène) | 2.81 m |
| BMt (rayon métacentrique) | 3.73 m |
| **GMt (hauteur métacentrique)** | **1.15 m** (stabilité initiale positive) |
| GZ max | 0.59 m à 45° |
| Limite de stabilité | 83° |

## Lancer le projet

```bash
pip install -r requirements.txt
python main.py
```

Tout est régénéré : `figures/`, `exports/`, et `resultats.json`.

## Structure du code

| Fichier | Rôle |
|---|---|
| `carene.py` | Géométrie paramétrique de la coque |
| `outils.py` | Méthode de Simpson + géométrie des polygones |
| `hydrostatique.py` | Hydrostatique du navire droit |
| `stabilite.py` | Courbe de stabilité GZ(θ) à grands angles |
| `exports.py` | Export STL, DXF, table des cotes |
| `graphiques.py` | Génération des figures |
| `main.py` | Orchestration de tout le projet |

| Dossier | Contenu |
|---|---|
| `figures/` | Plan des formes, courbe des aires, vue 3D, courbe GZ |
| `exports/` | `carene.stl`, `sections.dxf`, `table_des_cotes.csv` |

## Documentation

- `RAPPORT.md` : le rapport technique complet (théorie, méthode, résultats,
  validation).
- `REPRODUCTIBILITE.md` : protocole permettant de reconstruire l'outil de zéro
  et de retrouver les résultats publiés, avec un critère de validation chiffré
  à chaque étape. Contient également les procédures d'import de la coque dans
  Fusion 360 et SolidWorks.
- `presentation/presentation.pptx` : présentation du projet en 9 slides.
- `site/index.html` : page de présentation des résultats.

## Genèse du projet et usage de l'IA

Par souci de transparence : **ce projet a été développé avec l'assistance de
Claude (Anthropic)**.

La répartition est la suivante. J'ai défini le sujet, le type de navire, ses
paramètres principaux et le périmètre technique retenu ; l'assistant a écrit
l'implémentation Python et la documentation. L'import et l'exploitation de la
géométrie dans Fusion 360 sont de mon fait.

La finalité de ce projet est avant tout pédagogique. Mon objectif est de
réimplémenter l'outil moi-même, module par module : c'est précisément à cela que
sert le protocole `REPRODUCTIBILITE.md`, dont chaque étape se termine par un
critère de validation chiffré.

## Phase 2 : réimplémentation complète sur une carène aux dimensions de la FDI

La suite du projet consiste à **réimplémenter l'outil intégralement par mes
soins**, en suivant le protocole `REPRODUCTIBILITE.md`, et à l'appliquer à une
carène aux **dimensions principales publiques de la classe FDI** (frégate de
défense et d'intervention construite par Naval Group à Lorient, dont le Kimon
F-601) : longueur 121,6 m, largeur 17,7 m, déplacement d'environ 4 500 t à
pleine charge.

Il s'agit d'une carène paramétrique reprenant ces dimensions principales, et non
d'une reproduction des formes réelles du navire, qui ne sont pas publiques.

## Limites et pistes d'amélioration

- Coque à murailles droites au-dessus de la flottaison (pas de tonture ni de
  quête réaliste). Amélioration : ajouter de l'évasement.
- Stabilité calculée en gîte pure (pas d'assiette libre couplée).
- À ajouter ensuite : estimation de la résistance à l'avancement et de la
  puissance moteur ; étude d'un navire de soutien offshore (OSV).
