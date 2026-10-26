"""
navires.py
==========
Les jeux de parametres des navires etudies. Un seul code (carene.py,
hydrostatique.py, stabilite.py) sert a tous les navires : seul le jeu de
parametres change.

Chaque navire est un dictionnaire :
  nom                : texte affiche dans les resultats
  carene             : parametres passes a Carene (L, B, T, D, kp, kv), voir carene.py
  KG                 : hauteur du centre de gravite (m). Donnee de chargement,
                       pas de la coque.
  deplacement_publie : deplacement de reference (t) pour le calage, ou None si
                       le navire est fictif.

Regle : chaque chiffre porte un commentaire qui dit d'ou il vient, soit une
source (titre, date, lien), soit "HYPOTHESE" et la raison du choix.
"""

# --- Phase 1 : fregate fictive de taille moyenne ----------------------------
FREGATE_PHASE1 = {
    "nom": "Fregate phase 1 (L = 100 m)",
    "carene": {
        "L": 100.0,   # HYPOTHESE : fregate de taille moyenne (navire fictif)
        "B": 14.0,    # HYPOTHESE : idem
        "T": 4.5,     # HYPOTHESE : idem
        "D": 9.0,     # HYPOTHESE : idem
        "kp": 1.0,    # carene de Wigley
        "kv": 2.0,    # carene de Wigley
    },
    "KG": 5.4,                   # HYPOTHESE : ~0.6 x creux, valeur realiste pour une fregate
    "deplacement_publie": None,  # navire fictif : pas de valeur de reference
}

# --- Phase 2 : carene aux dimensions principales de la FDI (Kimon, F-601) ---
FREGATE_PHASE2_FDI = {
    "nom": "Fregate paramétrique (FDI) phase 2 (L = 122 m)",
    "carene": {
        "L": 122.0,   # Chiffre sourcé : (Naval Group, communique du 20/10/2025, "Length: 122 metres") # HYPOTHESE : longueur hors tout utilisée comme L .
        "B": 18.0,  # Naval Group, communique du 20/10/2025, "Width: 18 metres" (arrondi, largeur max et non a la flottaison)
        "T": 4.44,  # HYPOTHESE : deduit de Delta = 4500 t avec L = 122 m, B = 18 m et Cb = 0.45 (Cb typique de fregate, source : a completer)
        "D": 9.0,  # HYPOTHESE : environ 2 x T, meme regle que la phase 1 (creux non publie)
        "kp": 1.0,    # carene de Wigley
        "kv": 2.0808, # CALAGE : python calage.py fregate_phase2_fdi kv, Delta = 4500 t (ecart 0.000 %)
    },
    "KG": 5.4,                   # HYPOTHESE : ~0.6 x creux,meme regle que la phase 1 : 0.6 x D (KG non publie)
    "deplacement_publie": 4500.0,  # Naval Group, communique du 20/10/2025, "Displacement: 4,500 tonnes" ; etat de chargement non precise par les sources
  }

NAVIRES = {
    "fregate": FREGATE_PHASE1,
    "fregate_phase2_fdi": FREGATE_PHASE2_FDI,
}
