"""
outils.py
=========
Briques de calcul numerique reutilisees partout dans le projet.

Le cœur de l'architecture navale, c'est l'integration : on calcule des volumes
et des aires a partir de la geometrie de la coque. La methode historique des
architectes navals est la **methode de Simpson**. On la code nous-memes ici,
c'est le point pedagogique central du projet.
"""

import numpy as np


def simpson(f, x):
    """
    Integrale de f(x) par la methode de Simpson composite.

    La methode de Simpson approche la courbe par des petites paraboles
    (au lieu de simples trapezes), ce qui est beaucoup plus precis.

    Contrainte : il faut un nombre PAIR d'intervalles, donc un nombre IMPAIR
    de points. On utilise partout des grilles de 101 points (100 intervalles).

    Formule : integrale ~= (h/3) * [f0 + 4(f1+f3+...) + 2(f2+f4+...) + fN]
      - h = pas (distance entre deux points, suppose constant)
      - on pondere par 4 les points d'indice impair, par 2 les points pairs
        interieurs, par 1 les deux extremites.

    Parametres
    ----------
    f : tableau des valeurs de la fonction aux points x
    x : tableau des abscisses (espacement regulier)

    Retour
    ------
    float : valeur approchee de l'integrale
    """
    f = np.asarray(f, dtype=float)
    x = np.asarray(x, dtype=float)
    if f.ndim != 1 or x.ndim != 1:
        raise ValueError("simpson() : f et x doivent etre des vecteurs 1D")
    elif len(f) != len(x):
        raise ValueError("simpson() : f et x doivent avoir la meme taille")
    elif len(f) < 3:
        raise ValueError("simpson() : il faut au moins 3 points")
    elif len(f) % 2 == 0:
        raise ValueError("simpson() : il faut un nombre impair de points")
    else:
        len_f = len(f)
        h = (x[-1] - x[0]) / (len_f - 1)
        somme = f[0] + f[-1] + 4 * np.sum(f[1:-1:2]) + 2 * np.sum(f[2:-2:2])
        return (h / 3) * somme
    


def aire_centroide_polygone(points):
    """
    Aire et centre de gravite (centroide) d'un polygone ferme.

    On utilise la "formule du lacet" (shoelace). Elle marche pour n'importe
    quel polygone simple, ce qui est parfait pour une section de coque que
    l'on aura decoupee par la ligne de flottaison.

    Parametres
    ----------
    points : tableau Nx2 des sommets (y, z), dans l'ordre, polygone ferme
             (le dernier point n'a pas besoin d'etre egal au premier).

    Retour
    ------
    (aire, yc, zc) : aire positive, et coordonnees du centroide.
                     Si l'aire est nulle, on renvoie (0, 0, 0).
    """
    p = np.asarray(points, dtype=float)
    if len(p) < 3:
        return 0.0, 0.0, 0.0
    y = p[:, 0]
    z = p[:, 1]
    y1 = np.roll(y, -1)
    z1 = np.roll(z, -1)
    cross = y * z1 - y1 * z          # produit en croix de chaque arete
    a_signe = 0.5 * np.sum(cross)    # aire signee (depend du sens de parcours)
    if abs(a_signe) < 1e-12:
        return 0.0, 0.0, 0.0
    yc = np.sum((y + y1) * cross) / (6.0 * a_signe)
    zc = np.sum((z + z1) * cross) / (6.0 * a_signe)
    return abs(a_signe), yc, zc


def decoupe_demi_plan(points, a, b, c):
    """
    Decoupe (clipping) d'un polygone par un demi-plan a*y + b*z <= c.

    Algorithme de Sutherland-Hodgman. On garde la partie du polygone qui est
    "sous l'eau". Pour une coque inclinee, la surface de l'eau est une droite
    dans le plan (y, z) de la section, et on ne garde que ce qui est immerge.

    Parametres
    ----------
    points : tableau Nx2 des sommets (y, z) du polygone d'origine
    a, b, c : coefficients de la droite de flottaison a*y + b*z = c
              (on conserve les points tels que a*y + b*z <= c)

    Retour
    ------
    tableau Mx2 des sommets du polygone immerge (peut etre vide).
    """
    pts = list(np.asarray(points, dtype=float))
    if not pts:
        return np.zeros((0, 2))

    def dedans(p):
        return a * p[0] + b * p[1] - c

    sortie = []
    n = len(pts)
    for i in range(n):
        S = pts[i]
        E = pts[(i + 1) % n]
        gS = dedans(S)
        gE = dedans(E)
        if gE <= 0:                 # extremite E immergee
            if gS > 0:              # on entre dans l'eau -> point d'intersection
                t = gS / (gS - gE)
                sortie.append(S + t * (E - S))
            sortie.append(E)
        else:                       # extremite E hors de l'eau
            if gS <= 0:             # on sort de l'eau -> point d'intersection
                t = gS / (gS - gE)
                sortie.append(S + t * (E - S))
    if not sortie:
        return np.zeros((0, 2))
    return np.array(sortie)
