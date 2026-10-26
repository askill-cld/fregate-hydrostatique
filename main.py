"""
main.py
=======
Programme principal : il enchaine tout le projet.

  1. Definit la carene du navire choisi (parametres dans navires.py).
  2. Calcule l'hydrostatique du navire droit.
  3. Calcule la courbe de stabilite GZ(theta).
  4. Genere les graphiques (dossier figures/).
  5. Genere les fichiers CAO (dossier exports/).
  6. Enregistre tous les resultats chiffres dans resultats.json.

Lancer :
  python main.py        -> fregate de la phase 1 (figures/, exports/, resultats.json)
  python main.py fdi    -> carene FDI (figures/fdi/, exports/fdi/, resultats_fdi.json)
"""

import os
import sys
import json
import numpy as np

from carene import Carene
from navires import NAVIRES
from hydrostatique import calcul_hydrostatique, affiche_resultats, RHO_MER
from stabilite import courbe_gz, gz_murailles_droites
import graphiques
import exports


def main(nom="fregate"):
    if nom not in NAVIRES:
        print(f"Navire inconnu : '{nom}'. Choix possibles : {', '.join(NAVIRES)}")
        return None
    navire = NAVIRES[nom]
    if navire is None:
        print(f"Le jeu de parametres '{nom}' n'est pas encore ecrit (voir navires.py).")
        return None

    # La fregate de la phase 1 garde ses dossiers d'origine ; les autres
    # navires ont leurs propres sous-dossiers, pour ne rien ecraser.
    ici = os.path.dirname(os.path.abspath(__file__))
    if nom == "fregate":
        dossier_figures = os.path.join(ici, "figures")
        dossier_exports = os.path.join(ici, "exports")
        fichier_resultats = os.path.join(ici, "resultats.json")
    else:
        dossier_figures = os.path.join(ici, "figures", nom)
        dossier_exports = os.path.join(ici, "exports", nom)
        fichier_resultats = os.path.join(ici, f"resultats_{nom}.json")
    os.makedirs(dossier_figures, exist_ok=True)
    os.makedirs(dossier_exports, exist_ok=True)

    # 1) --- Definition du navire (parametres et sources dans navires.py) --
    carene = Carene(**navire["carene"])
    # KG : hauteur du centre de gravite. C'est une donnee de chargement (pas de
    # la coque), fournie avec le jeu de parametres.
    KG = navire["KG"]

    print(navire["nom"])
    print("Carene definie :",
          f"L={carene.L} m, B={carene.B} m, T={carene.T} m, D={carene.D} m, KG={KG} m")

    # 2) --- Hydrostatique du navire droit --------------------------------
    res = calcul_hydrostatique(carene, KG=KG, rho=RHO_MER)
    affiche_resultats(res)

    # Comparaison au deplacement publie (navires reels uniquement)
    if navire["deplacement_publie"] is not None:
        ecart = 100.0 * (res["deplacement"] - navire["deplacement_publie"]) / navire["deplacement_publie"]
        print(f"   Deplacement publie        = {navire['deplacement_publie']:.0f} t"
              f"  (ecart du calcul : {ecart:+.2f} %)")

    # 3) --- Courbe de stabilite GZ(theta) --------------------------------
    print("\nCalcul de la courbe de stabilite GZ (peut prendre quelques secondes)...")
    angles = np.arange(0, 91, 5)
    res_gz = courbe_gz(carene, KG=KG, volume_droit=res["volume"], angles_deg=angles)
    res_ws = gz_murailles_droites(angles, res["GMt"], res["BMt"])

    print(f"   GM (hydrostatique)        = {res['GMt']:.3f} m")
    print(f"   GM (pente de la courbe GZ) = {res_gz['gm_pente']:.3f} m  (doit coller a GM)")
    print(f"   GZ max                    = {res_gz['gz_max']:.3f} m a {res_gz['angle_gz_max']:.0f} deg")
    if res_gz["angle_annulation"]:
        print(f"   Limite de stabilite       = {res_gz['angle_annulation']:.1f} deg")
    print(f"   Aire sous GZ a 30 deg     = {res_gz['aire_30deg']:.4f} m.rad")
    print(f"   Aire sous GZ a 40 deg     = {res_gz['aire_40deg']:.4f} m.rad")

    # 4) --- Graphiques ---------------------------------------------------
    print("\nGeneration des graphiques...")
    graphiques.plan_des_formes(carene, os.path.join(dossier_figures, "1_plan_des_formes.png"))
    graphiques.courbe_aires(res, os.path.join(dossier_figures, "2_courbe_des_aires.png"))
    graphiques.vue_3d(carene, os.path.join(dossier_figures, "3_vue_3d.png"))
    graphiques.courbe_gz(res_gz, os.path.join(dossier_figures, "4_courbe_gz.png"), res_ws=res_ws)
    print(f"   -> {os.path.relpath(dossier_figures, ici)}/ : 4 images PNG")

    # 5) --- Exports CAO --------------------------------------------------
    print("\nGeneration des fichiers CAO...")
    nt = exports.export_stl(carene, os.path.join(dossier_exports, "carene.stl"))
    ns = exports.export_dxf_sections(carene, os.path.join(dossier_exports, "sections.dxf"))
    exports.export_table_cotes(carene, os.path.join(dossier_exports, "table_des_cotes.csv"))
    rel_exports = os.path.relpath(dossier_exports, ici)
    print(f"   -> {rel_exports}/carene.stl ({nt} triangles)")
    print(f"   -> {rel_exports}/sections.dxf ({ns} couples)")
    print(f"   -> {rel_exports}/table_des_cotes.csv")

    # 6) --- Sauvegarde des resultats chiffres ----------------------------
    a_sauver = {k: v for k, v in res.items()
                if not isinstance(v, np.ndarray)}
    a_sauver["stabilite"] = {
        "angles_deg": res_gz["angles_deg"].tolist(),
        "GZ": res_gz["GZ"].tolist(),
        "gz_max": res_gz["gz_max"],
        "angle_gz_max": float(res_gz["angle_gz_max"]),
        "angle_annulation": res_gz["angle_annulation"],
        "gm_pente": res_gz["gm_pente"],
        "aire_30deg": res_gz["aire_30deg"],
        "aire_40deg": res_gz["aire_40deg"],
    }
    if navire["deplacement_publie"] is not None:
        a_sauver["deplacement_publie"] = navire["deplacement_publie"]
        a_sauver["ecart_deplacement_pct"] = ecart
    with open(fichier_resultats, "w", encoding="utf-8") as f:
        json.dump(a_sauver, f, indent=2, ensure_ascii=False)
    print(f"\nResultats chiffres enregistres dans {os.path.basename(fichier_resultats)}")
    print("Termine.")

    return res, res_gz


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "fregate")
