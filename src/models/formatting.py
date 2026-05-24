from collections import Counter

def afficher_resume(poutre) -> str:
    """Genere un resume formate des proprietes de la poutre."""
    texte = (
        "\n" + "=" * 70 + "\n"
        f"{'PROPRIETES DE LA POUTRE':^70}" + "\n" + "=" * 70 + "\n"
        f"Geometrie\n"
        f"  Largeur                   : {poutre.b_cm:8.0f} cm\n"
        f"  Hauteur                   : {poutre.h_cm:8.0f} cm\n"
        f"  Portee                    : {poutre.l_m:8.2f} m\n"
        f"  Hauteur utile (d)         : {poutre.d_m:8.2f} m\n"
        f"\nMateriaux\n"
        f"  fc28 (beton)              : {poutre.fc28_MPa:8.0f} MPa\n"
        f"  ft28 (beton)              : {poutre.ft28_MPa:8.2f} MPa\n"
        f"  fe (acier)                : {poutre.fe_MPa:8.0f} MPa\n"
        f"  fbu (calcul ELU)          : {poutre.fbu_MPa:8.2f} MPa\n"
        f"  fsu (calcul ELU)          : {poutre.fsu_MPa:8.0f} MPa\n"
        f"\nSollicitations\n"
        f"  Moment ELU                : {poutre.M_u_kNm:8.0f} kN.m\n"
        f"  Moment ELS                : {poutre.M_ser_kNm:8.0f} kN.m\n"
        f"  Effort tranchant          : {poutre.V_u_kN:8.0f} kN\n"
        f"\nConditions ELS\n"
        f"  Classe fissuration        : {poutre.fis:>8}\n"
        f"  Type barre                : {poutre.type_barre:>8}\n"
        f"  sigma_bc limite           : {poutre.sigma_bc_bar_MPa:8.2f} MPa\n"
        f"  sigma_st limite           : {poutre.sigma_st_bar_MPa:8.2f} MPa\n"
        f"\nLimites d'armatures\n"
        f"  Section minimale          : {poutre.A_min_cm2:8.2f} cm2\n"
        f"  Section maximale          : {poutre.A_max_cm2:8.2f} cm2\n"
        + "=" * 70
        + "\n"
    )
    return texte

def afficher_repartition_arm_trans(poutre, nb_brin: int, phi_t: int) -> str:
    # 1. Compter les occurrences des espacements
    compte = Counter(poutre.disposition)

    # 2. Nettoyer les clés pour enlever les ".0" inutiles si ce sont des entiers
    mon_dict = {
        str(int(k) if isinstance(k, (int, float)) and k.is_integer() else k): v
        for k, v in compte.items()
    }

    # 3. Construire la suite de répartition
    elements_repartition = []
    for key, value in mon_dict.items():
        elements_repartition.append(f"{value}x{key}")

    repartition_str = "\n       •  ".join(elements_repartition)

    # 4. Mettre en forme le texte final
    texte_final = f"Répartition des cadres :\n       •  {repartition_str}"

    return texte_final

def afficher_result_long(poutre) -> list[str]:
    """Calcule et met en forme les résultats du ferraillage longitudinal sous forme de lignes de texte."""
    res_long = poutre.calculer_ferraillage_longitudinal()
    res_elu = res_long["res_elu"]
    res_els = res_long["res_els"]

    txt_res = []
    txt_res.append("\n" + "=" * 70)
    # Correction de l'écriture des chaînes imbriquées (f-string imbriquée avec des guillemets simples)
    txt_res.append(f"{'FERRAILLAGE LONGITUDINAL - RESULTATS':^70}")
    txt_res.append("=" * 70)

    txt_res.append("\nCALCULS A L'ELU")
    txt_res.append(f"  Configuration             : {res_elu['config']}")
    txt_res.append(f"  Moment reduit (mu)        : {res_elu['mu']:7.3f}")
    if res_elu.get("alpha") is not None:
        txt_res.append(f"  Coefficient alpha         : {res_elu['alpha']:7.3f}")
        txt_res.append(f"  Bras de levier (z)        : {res_elu['z']:7.3f} m")
    if res_elu.get("M_r") is not None:
        txt_res.append(f"  Moment resistant (M_r)    : {res_elu['M_r']:7.3f} MN.m")
    if res_elu.get("sigma_sc") is not None:
        txt_res.append(f"  Contrainte acier comp.    : {res_elu['sigma_sc']:7.2f} MPa")
    txt_res.append(f"  Acier tendu               : {res_elu['A_t']:7.2f} cm2")
    if res_elu.get("A_c") is not None and res_elu["A_c"] > 0:
        txt_res.append(f"  Acier comprime            : {res_elu['A_c']:7.2f} cm2")
    
    if res_els.get("utilite"):
        txt_res.append("\nCALCULS A L'ELS")
        txt_res.append(f"  Configuration             : {res_els['config']}")
        txt_res.append(f"  Coefficient alpha         : {res_els['alpha']:7.3f}")
        txt_res.append(f"  Position axe neutre (y1)  : {res_els['y1']:7.3f} m")
        txt_res.append(f"  Moment resistant beton    : {res_els['M_rsb']:7.3f} MN.m")
        txt_res.append(f"  Bras de levier (z)        : {res_els['z']:7.3f} m")
        txt_res.append(f"  Acier tendu               : {res_els['A_t']:7.2f} cm2")
        if res_els.get("A_c") is not None and res_els["A_c"] > 0:
            txt_res.append(f"  Acier comprime            : {res_els['A_c']:7.2f} cm2")

    txt_res.append("\nRESULTAT FINAL")
    txt_res.append(f"  Acier tendu retenu        : {poutre.A_t_final_cm2:7.2f} cm2")
    if hasattr(poutre, 'A_c_final_cm2') and poutre.A_c_final_cm2 > 0:
        txt_res.append(f"  Acier comprime retenu     : {poutre.A_c_final_cm2:7.2f} cm2")
    txt_res.append(f"  Acier minimal             : {poutre.A_min_cm2:7.2f} cm2")
    txt_res.append(f"  Acier maximal             : {poutre.A_max_cm2:7.2f} cm2")

    txt_res.append("\n" + "=" * 70)

    return txt_res

def afficher_choix(poutre, compositions: list[tuple[int, int]]):
    text_choix = []
    text_choix.append("\nChoix d'armature longitudinale saisi :")

    # Formatage propre de la composition longitudinale
    list_intermediaire = []
    compositions_valides = []
    
    for nb, phi in compositions:
        if nb > 0 and phi > 0:
            list_intermediaire.append(f"{nb} HA{phi}")
            compositions_valides.append((nb, phi))

    if list_intermediaire:
        text_choix.append(" + ".join(list_intermediaire))
        text_choix.append(f" - Section longitudinale fournie = {poutre.calculer_section_reelle(compositions_valides):.2f} cm2")
    else:
        text_choix.append("Aucun acier longitudinal sélectionné")
        
    return text_choix

def afficher_result_trans(poutre, phi_t: int, nb_brins: int) -> list[str]:
    """
    Calcule et met en forme les résultats transversaux à partir de données brutes.
    Aucune dépendance avec l'interface graphique (Vue).
    """
    text_trans = []
    
    # Sécurité : On vérifie les entrées fondamentales
    if nb_brins <= 0 or phi_t <= 0:
        text_trans.append("\n[Erreur] Configuration transversale incomplète ou invalide.")
        return text_trans

    # Calcul moteur
    res_trans = poutre.calculer_ferraillage_transversale(nb_brin=nb_brins, phi_t=phi_t)
    
    text_trans.append("\n" + "=" * 70)
    text_trans.append(f"{'RESULTATS ARMATURES TRANSVERSALES':^70}")
    text_trans.append("=" * 70)

    # Traitement des aciers transversaux
    text_trans.append("\nArmature transversale calculée :")
    text_trans.append(f" - Diametre de cadre choisi = HA{res_trans.get('phi_t', phi_t)}")
    text_trans.append(f" - Nombre de brins = {res_trans.get('nb_brin', nb_brins)}")
    
    section_at_fournie = poutre.calculer_section_reelle([(nb_brins, phi_t)])
    text_trans.append(f" - At = {section_at_fournie:.2f} cm2")
    
    text_trans.append(f" - St0 (Espacement initial) = {res_trans.get('st0', 0):.2f} cm")
    text_trans.append(f" - St (Espacement calculé)  = {res_trans.get('st', 0):.2f} cm")
    text_trans.append(f" - St max (Espacement max)  = {res_trans.get('st_max', 0):.2f} cm")
    
    if "disposition" in res_trans:
        
        text_trans.append(f"\nSéquence de répartition : {res_trans['disposition']}")
    else:
        text_trans.append('pas de répartition')
        
    text_trans.append("\n" + "=" * 70)
    
    return text_trans

def afficher_result_fleche(poutre):
    res_fleche = poutre.verifier_fleche()
    texte = [
        "<b>Vérification de la flèche :</b>",
        f"Flèche maximale admissible flim : {res_fleche['f_lim_cm']:.2f}",
        f"Flèche calculée f : {res_fleche['f_cm']:.2f}"
    ]
    return texte