def bool_to_01(v):
    # accepte bool Excel, VRAI/FAUX, TRUE/FALSE, 1/0
    if isinstance(v, bool):
        return 1 if v else 0
    s = normalize_lower(v)
    if s in ("vrai", "true", "1", "yes"):
        return 1
    if s in ("faux", "false", "0", "no", ""):
        return 0
    # si valeur inattendue, on peut mettre 1 (conservateur) ou 0 ; ici 1
    return 1


# BI: 0 si BH est FAUX, 1 si VRAI
setv(ws_dest, "BI", r, bool_to_01(getv(ws_dest, "BH", r)))

# BO: 0 si BN est FAUX, 1 si VRAI
setv(ws_dest, "BO", r, bool_to_01(getv(ws_dest, "BN", r)))