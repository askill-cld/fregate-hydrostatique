"""
calage.py
=========
Calage de la forme de la carene sur un deplacement publie.

Les dimensions principales (L, B, T) sont fixees par les sources et les
hypotheses. Le deplacement publie impose alors le coefficient de bloc. On regle
UN des deux exposants de forme (kp ou kv, voir carene.py) pour que le
deplacement calcule soit egal au deplacement publie.

Lancer :
  python calage.py fregate_phase2_fdi kv
  python calage.py fregate_phase2_fdi kp

Le script affiche la valeur calee et ses consequences (coefficients, KB, BM,
GM). On recopie ensuite la valeur retenue dans navires.py, avec un commentaire
"CALAGE".
"""

import sys
from carene import Carene
from hydrostatique import calcul_hydrostatique, RHO_MER
from navires import NAVIRES


# Intervalle de recherche de chaque bouton de forme
BORNES = {"kp": (0.5, 2.0), "kv": (1.0, 5.0)}


def hydrostatique_pour(navire, bouton, valeur):
    """Hydrostatique de la carene du navire quand le bouton (kp ou kv) vaut valeur."""
    parametres = dict(navire["carene"])   # copie : on ne modifie pas navires.py
    parametres[bouton] = valeur
    return calcul_hydrostatique(Carene(**parametres), KG=navire["KG"], rho=RHO_MER)


def deplacement_pour(navire, bouton, valeur):
    """Deplacement (t) de la carene quand le bouton vaut valeur."""
    return hydrostatique_pour(navire, bouton, valeur)["deplacement"]


def cale_forme(navire, bouton, v_min, v_max, n_iter=50):
    """
    Cherche par dichotomie, entre v_min et v_max, la valeur du bouton (kp ou kv)
    qui donne un deplacement egal a navire["deplacement_publie"].
    Retourne la valeur trouvee.
    """
    cible = navire["deplacement_publie"]
    deplacement_min = deplacement_pour(navire, bouton, v_min) 
    deplacement_max = deplacement_pour(navire, bouton, v_max)
    dep_min = deplacement_min - cible
    dep_max = deplacement_max - cible
    if dep_min * dep_max > 0:
        print(f"Erreur : le deplacement publie {cible:.0f} t n’est pas compris entre"
              f" {deplacement_min:.0f} t (pour {bouton}={v_min}) et"
              f" {deplacement_max:.0f} t (pour {bouton}={v_max}).")
        return None
    # On cherche la valeur du bouton qui donne un deplacement egal a cible. 
    for _ in range(n_iter):
        v = 0.5 * (v_min + v_max)
        dep = deplacement_pour(navire, bouton, v)
        if abs(dep - cible) < 1e-3:
            return v  
        if dep_min * (dep - cible) > 0:
                v_min = v
        else: 
                v_max = v 
    return 0.5 * (v_min + v_max)


def main(nom, bouton):
    if nom not in NAVIRES or bouton not in BORNES:
        print(f"Usage : python calage.py <{'|'.join(NAVIRES)}> <kp|kv>")
        return None
    navire = NAVIRES[nom]
    cible = navire["deplacement_publie"]
    if cible is None:
        print(f"'{nom}' n'a pas de deplacement publie : rien a caler.")
        return None

    depart = navire["carene"][bouton]
    print(f"{navire['nom']} : calage de {bouton} sur {cible:.0f} t")
    print(f"   Avant : {bouton} = {depart:.4f} -> deplacement = {deplacement_pour(navire, bouton, depart):.1f} t")

    valeur = cale_forme(navire, bouton, *BORNES[bouton])
    if valeur is None:
        print("   cale_forme() ne renvoie rien pour l'instant (voir le TODO dans calage.py).")
        return None

    res = hydrostatique_pour(navire, bouton, valeur)
    ecart = 100.0 * (res["deplacement"] - cible) / cible
    print(f"   Apres : {bouton} = {valeur:.4f} -> deplacement = {res['deplacement']:.1f} t"
          f"  (ecart {ecart:+.3f} %)")
    print(f"   Cb = {res['Cb']:.4f}  Cp = {res['Cp']:.4f}  Cm = {res['Cm']:.4f}  Cw = {res['Cw']:.4f}")
    print(f"   KB = {res['KB']:.3f} m  BMt = {res['BMt']:.3f} m  KMt = {res['KMt']:.3f} m"
          f"  GMt = {res['GMt']:.3f} m (KG = {navire['KG']} m)")
    return valeur


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage : python calage.py <{'|'.join(NAVIRES)}> <kp|kv>")
    else:
        main(sys.argv[1], sys.argv[2])
