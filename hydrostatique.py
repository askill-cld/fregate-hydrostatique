"""
hydrostatique.py
================
Calcul des grandeurs hydrostatiques du navire DROIT (sans gite), au tirant
d'eau de projet T.

On calcule, dans l'ordre :
  - le volume immerge (carene) et le deplacement (poids du navire)
  - la position du centre de carene B (KB en hauteur, LCB en longueur)
  - les caracteristiques du plan de flottaison (aire, centre, inerties)
  - le rayon metacentrique BM, la position du metacentre KM
  - la hauteur metacentrique GM (le critere de stabilite initiale)
  - les coefficients de forme (Cb, Cp, Cm, Cw)

Toutes les integrales utilisent la methode de Simpson (voir outils.py).
"""

import numpy as np
from outils import simpson

RHO_MER = 1.025  # masse volumique de l'eau de mer (t/m^3)
G = 9.81         # gravite (m/s^2), pour info


def calcul_hydrostatique(carene, KG, rho=RHO_MER, n=101):
    """
    Calcule toutes les grandeurs hydrostatiques au tirant d'eau T.

    Parametres
    ----------
    carene : objet Carene
    KG     : hauteur du centre de gravite au-dessus de la quille (m).
             C'est une donnee de chargement du navire (a estimer), pas une
             propriete de la coque. On la fournit en entree.
    rho    : masse volumique de l'eau (t/m^3)
    n      : nombre de points des grilles (impair -> Simpson)
     

    Retour
    ------
    dict des resultats.
    """
    L, B, T = carene.L, carene.B, carene.T

    xs = carene.stations(n)            # positions longitudinales
    zsT = np.linspace(0.0, T, n)       # hauteurs de la quille a la flottaison

    # --- courbe des aires A(x), volume immerge et deplacement ---
    A = np.array([simpson(2.0 * carene.demi_largeur(x, zsT), zsT) for x in xs])
    volume = simpson(A, xs)             # volume immerge (m^3)
    deplacement = volume * rho          # masse du navire (t)
    poids = deplacement * G          # poids du navire (kN)

    # --- Centre de carene B (KB en hauteur, LCB en longueur) ---
    Mz = np.array([simpson(zsT * 2 * carene.demi_largeur(x, zsT), zsT) for x in xs])
    KB = simpson(Mz, xs) / volume               # hauteur au-dessus de la quille (m)
    LCB = simpson(A * xs, xs) / volume          # position longitudinale (m, /milieu)

    # --- Plan de flottaison (a z = T) : bw, Aw, LCF, It, IL ---
    # bw : les demi-largeurs à la flottaison (z = T), pour toutes les stations
    bw = carene.demi_largeur(xs, T)
    #Aw : l’aire du plan de flottaison
    Aw = simpson(2.0 * bw, xs)                 # aire du plan de flottaison (m^2)
    #LCF : son centre (le centre de flottaison)
    LCF = simpson(2.0 * bw * xs, xs) / Aw       # centre de flottaison (m, /milieu)
    #It : son inertie transversale (axe longitudinal)
    It = simpson(2.0 * bw**3 / 3.0, xs)         # inertie transversale (m^4)
    #IL : son inertie longitudinale (axe transversal)
    IL = simpson(2.0 * bw * (xs - LCF)**2, xs)  # inertie longitudinale (m^4)

    # --- Metacentre ---
    BMt = It / volume                  # rayon metacentrique transversal (m)
    BML = IL / volume                  # rayon metacentrique longitudinal (m)
    KMt = KB + BMt                     # hauteur du metacentre transversal (m)
    GMt = KMt - KG                     # hauteur metacentrique transversale (m)
    GML = KB + BML - KG                # hauteur metacentrique longitudinale (m)

    # --- Coefficients de forme (sans dimension, decrivent la finesse) ---
    Am = A.max()                       # aire du maitre-couple (section max)
    Cb = volume / (L * B * T)          # coefficient de bloc
    Cm = Am / (B * T)                  # coefficient de maitre-couple
    Cp = volume / (Am * L)             # coefficient prismatique
    Cw = Aw / (L * B)                  # coefficient de flottaison

    # --- Grandeurs pratiques ---
    TPC = Aw * rho / 100.0             # tonnes par cm d'enfoncement
    MCT = deplacement * GML / (100.0 * L)  # moment pour faire varier l'assiette de 1 cm

    return {
        "L": L, "B": B, "T": T, "D": carene.D, "KG": KG, "rho": rho,
        "volume": volume, "deplacement": deplacement,"poids": poids,
        "LCB": LCB, "KB": KB,
        "Aw": Aw, "LCF": LCF, "It": It, "IL": IL,
        "BMt": BMt, "BML": BML, "KMt": KMt, "GMt": GMt, "GML": GML,
        "Am": Am, "Cb": Cb, "Cm": Cm, "Cp": Cp, "Cw": Cw,
        "TPC": TPC, "MCT": MCT,
        # donnees pour les graphiques :
        "xs": xs, "A_x": A, "bw_x": bw,
    }


def affiche_resultats(res):
    """Affiche un tableau lisible des resultats hydrostatiques."""
    lignes = [
        ("Longueur L", res["L"], "m"),
        ("Largeur B", res["B"], "m"),
        ("Tirant d'eau T", res["T"], "m"),
        ("Creux D", res["D"], "m"),
        ("KG (centre de gravite)", res["KG"], "m"),
        ("-- Carene --", None, ""),
        ("Volume immerge", res["volume"], "m3"),
        ("Deplacement", res["deplacement"], "t"),
        ("Poids", res["poids"], "kN"),
        ("KB (centre de carene)", res["KB"], "m"),
        ("LCB (long.)", res["LCB"], "m"),
        ("-- Flottaison --", None, ""),
        ("Aire flottaison Aw", res["Aw"], "m2"),
        ("LCF (long.)", res["LCF"], "m"),
        ("Inertie transv. It", res["It"], "m4"),
        ("-- Stabilite initiale --", None, ""),
        ("BMt (rayon metac.)", res["BMt"], "m"),
        ("KMt (metacentre)", res["KMt"], "m"),
        ("GMt (haut. metac.)", res["GMt"], "m"),
        ("-- Coefficients --", None, ""),
        ("Cb (bloc)", res["Cb"], ""),
        ("Cm (maitre-couple)", res["Cm"], ""),
        ("Cp (prismatique)", res["Cp"], ""),
        ("Cw (flottaison)", res["Cw"], ""),
        ("-- Pratique --", None, ""),
        ("TPC", res["TPC"], "t/cm"),
        ("MCT 1cm", res["MCT"], "t.m/cm"),
    ]
    print("\n" + "=" * 48)
    print(" RESULTATS HYDROSTATIQUES (navire droit)")
    print("=" * 48)
    for nom, val, unite in lignes:
        if val is None:
            print(f"\n {nom}")
        else:
            print(f"   {nom:<26} {val:>12.4f} {unite}")
    print("=" * 48)
