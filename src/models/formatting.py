# src/models/formatting.py
import logging
from collections import Counter
from .constant import MU_LIM

logger = logging.getLogger(__name__)

# Largeur globale pour le centrage et le formatage des blocs textuels
LARGEUR_RACCORD = 75


def afficher_resume(poutre) -> list[str]:
    """Génère un résumé formaté des propriétés initiales sous forme de liste de lignes."""
    logger.info("Début de l'export de l'affichage du résumé.")
    txt_res = [
        "\n" + "=" * LARGEUR_RACCORD,
        f"{'PROPRIÉTÉS INITIALES DE LA POUTRE':^{LARGEUR_RACCORD}}",
        "=" * LARGEUR_RACCORD,
        "\nGÉOMÉTRIE",
        f"  Largeur (b)                                 : {poutre.b_cm:8.0f} cm",
        f"  Hauteur (h)                                 : {poutre.h_cm:8.0f} cm",
        f"  Portée (L)                                  : {poutre.l_m:8.2f} m",
        f"  Hauteur utile (d)                           : {poutre.d_m:8.2f} m",
        "\nMATÉRIAUX",
        f"  f_c28 (Béton)                               : {poutre.fc28_MPa:8.0f} MPa",
        f"  f_t28 (Béton)                               : {poutre.ft28_MPa:8.2f} MPa",
        f"  f_e   (Acier)                               : {poutre.fe_MPa:8.0f} MPa",
        f"  f_bu  (Calcul ELU)                          : {poutre.fbu_MPa:8.2f} MPa",
        f"  f_su  (Calcul ELU)                          : {poutre.fsu_MPa:8.0f} MPa",
        "\nSOLLICITATIONS",
        f"  Moment ultime (M_u)                         : {poutre.M_u_kNm:8.2f} kN·m",
        f"  Moment de service (M_ser)                   : {poutre.M_ser_kNm:8.2f} kN·m",
        f"  Effort tranchant ultime (V_u)               : {poutre.V_u_kN:8.2f} kN",
        "\nCONDITIONS AUX LIMITES (ELS)",
        f"  Classe de fissuration                       : {poutre.fis:>8}",
        f"  Type de barre                               : {poutre.type_barre:>8}",
        f"  σ_bc admissible                             : {poutre.sigma_bc_bar_MPa:8.0f} MPa",
        f"  σ_st admissible                             : {poutre.sigma_st_bar_MPa:8.0f} MPa",
        "\nSECTIONS REQUISES RÉGLEMENTAIRES",
        f"  Section minimale (A_min)                    : {poutre.A_min_cm2:8.2f} cm²",
        f"  Section maximale (A_max)                    : {poutre.A_max_cm2:8.2f} cm²",
    ]
    logger.info("Fin de l'export de l'affichage du résumé.")
    return txt_res


def afficher_result_long(poutre) -> list[str]:
    """Calcule et met en forme les résultats du ferraillage longitudinal."""
    logger.info("Début de l'export des résultats du ferraillage longitudinal.")
    res_long = poutre.calculer_ferraillage_longitudinal()
    res_elu = res_long["res_elu"]
    res_els = res_long["res_els"]

    txt_res = [
            "\n" + "=" * LARGEUR_RACCORD,
            f"{'FERRAILLAGE LONGITUDINAL - RÉSULTATS':^{LARGEUR_RACCORD}}",
            "=" * LARGEUR_RACCORD
    ]

    if res_elu.get("utilite"):
        if res_elu['config'] == "Simple":
            expl = "µ < µ_lim → Armatures tendus uniquement"
        else:
            expl = "µ ≥ µ_lim → Armatures comprimées nécessaires"

        txt_res.append("\nCALCULS À L'ELU")
        txt_res.append(f"  Moment réduit (μ)                           : {res_elu['mu']:7.3f}")
        txt_res.append(f"  Moment réduit limite (μ_lim)                : {MU_LIM:7.3f}")
        txt_res.append("\n")
        txt_res.append(f"  ► {expl}")

        if res_elu.get("alpha") is not None:
            txt_res.append(f"  Coefficient alpha (α)                       : {res_elu['alpha']:7.3f}")
            txt_res.append(f"  Bras de levier (z)                          : {res_elu['z']:7.3f} m")
        if res_elu.get("M_r") is not None:
            txt_res.append(f"  Moment résistant (M_r)                      : {res_elu['M_r']:7.3f} MN·m")
        if res_elu.get("sigma_sc") is not None:
            txt_res.append(f"  Contrainte acier comprimé (σ_sc)            : {res_elu['sigma_sc']:7.2f} MPa")
        
        txt_res.append(f"  Section théorique acier tendu (A_t)         : {res_elu['A_t']:7.2f} cm²")
    else: 
        txt_res.append("   ► Fissuration très préjudiciable, calcul à l'ELS uniquement.")
    
    if res_elu.get("A_c") is not None and res_elu["A_c"] > 0:
        txt_res.append(f"  Section théorique acier comp. (A_c)         : {res_elu['A_c']:7.2f} cm²")
    
    if res_els.get("utilite"):
        txt_res.append("\nCALCULS À L'ELS")
        txt_res.append(f"  Coefficient alpha (α_ser)                   : {res_els['alpha']:7.3f}")
        txt_res.append(f"  Position axe neutre (y_1)                   : {res_els['y1']:7.3f} m")
        txt_res.append(f"  Moment résistant béton (M_rsb)              : {res_els['M_rsb']:7.3f} MN·m")
        
        if res_els['config'] == "Simple":
            expl2 = "M_ser < M_rsb → Armatures tendus uniquement"
        else:
            expl2 = "M_ser ≥ M_rsb → Armatures comprimées nécessaires"
        
        txt_res.append("\n")
        txt_res.append(f"  ► {expl2}")
        
        txt_res.append(f"  Bras de levier de service (z_ser)           : {res_els['z']:7.3f} m")
        txt_res.append(f"  Section acier tendu requise (A_t)           : {res_els['A_t']:7.2f} cm²")
        if res_els.get("A_c") is not None and res_els["A_c"] > 0:
            txt_res.append(f"  Section acier comp. requise (A_c)           : {res_els['A_c']:7.2f} cm²")
    else:
        txt_res.append("\n")
        txt_res.append("  ► Fissuration peu préjudiciable, calcul à l'ELU uniquement.")

    txt_res.extend([
        "\nBILAN DES SECTIONS REQUISES",
        f"  Section théorique finale retenue            : {poutre.A_t_final_cm2:7.2f} cm²",
    ])
    
    if hasattr(poutre, 'A_c_final_cm2') and poutre.A_c_final_cm2 > 0:
        txt_res.append(f"  Section comprimée finale retenue            : {poutre.A_c_final_cm2:7.2f} cm²")
        
    txt_res.extend([
        f"  Condition de non-fragilité (A_min)          : {poutre.A_min_cm2:7.2f} cm²",
        f"  Section maximale autorisée (A_max)          : {poutre.A_max_cm2:7.2f} cm²",
    ])
    logger.info("Début de l'export des résultats du ferraillage longitudinal.")
    return txt_res


def afficher_result_cisaillement(poutre) -> list[str]:
    """Génère la note textuelle de vérification des contraintes de cisaillement."""
    logger.info("Début de l'export de la vérification des contraintes de cisaillement.")
    text_cisaillement = [
        "\n" + "=" * LARGEUR_RACCORD,
        f"{'VÉRIFICATION DE LA CONTRAINTE DE CISAILLEMENT':^{LARGEUR_RACCORD}}",
        "=" * LARGEUR_RACCORD
    ]

    verif_cis = poutre.verifier_cisaillement()

    text_cisaillement.extend([
        f"  Contrainte de cisaillement admissible (τ_lim) : {verif_cis['tau_lim_MPa']:.2f} MPa",
        f"  Contrainte de cisaillement calculée (τ_u)     : {verif_cis['tau_u_MPa']:.2f} MPa"
    ])

    est_valide = verif_cis['tau_u_MPa'] <= verif_cis['tau_lim_MPa']
    statut_cis = "OK (τ_u ≤ τ_lim)" if est_valide else "HORS LIMITES (τ_u > τ_lim)"

    text_cisaillement.append(
        f"  ► Vérification de la condition de cisaillement : {statut_cis}"
    )

    logger.info("Fin de l'export de la vérification des contraintes de cisaillement.")
    return text_cisaillement


def afficher_choix(poutre, compositions: list[tuple[int, int]]) -> list[str]:
    logger.info("Début de l'export de la structure d'aciers réels choisis par l'utilisateur.")
    """Met en forme la structure d'aciers réels choisis par l'utilisateur."""
    text_choix = [
        "\n" + "=" * LARGEUR_RACCORD,
        f"{"COMPOSITION DE L'ARMATURE RÉELLE SÉLECTIONNÉE":^{LARGEUR_RACCORD}}",
        "=" * LARGEUR_RACCORD
    ]

    list_intermediaire = []
    compositions_valides = []
    
    for nb, phi in compositions:
        if nb > 0 and phi > 0:
            list_intermediaire.append(f"{nb} HA{phi:.0f}")
            compositions_valides.append((nb, phi))

    if list_intermediaire:
        text_choix.append(f"  Combinaison d'aciers retenue                : {' + '.join(list_intermediaire)}")
        section_reelle = poutre.calculer_section_reelle(compositions_valides)
        text_choix.append(f"  Section totale réelle fournie (A_réel)      : {section_reelle} cm²")
        if section_reelle > poutre.A_t_final_cm2:
            text_choix.append("  ►  Vérification de la condition             : OK (A_reel > A_th)")
        else:
            text_choix.append("  ►  Vérification de la condition             : Non vérifié (A_reel < A_th)")
    else:
        text_choix.append("  [!] Aucun acier longitudinal sélectionné pour le moment.")
        
    logger.info("Fin de l'export de la structure d'aciers réels choisis par l'utilisateur.")
    return text_choix


def afficher_result_trans(poutre, phi_t: int, nb_brins: int) -> list[str]:
    """Calcule et met en forme les résultats réglementaires du ferraillage transversal."""
    logger.info("Début de l'export des résultats du ferraillage transversal.")
    text_trans = []
    
    if nb_brins <= 0 or phi_t <= 0:
        text_trans.append("\n[Erreur] Configuration transversale incomplète ou invalide.")
        return text_trans

    res_trans = poutre.calculer_ferraillage_transversale(nb_brin=nb_brins, phi_t=phi_t)
    section_at_fournie = poutre.calculer_section_reelle([(nb_brins, phi_t)])
    
    text_trans.extend([
        "\n" + "=" * LARGEUR_RACCORD,
        f"{'FERRAILLAGE TRANSVERSAL - RÉSULTATS':^{LARGEUR_RACCORD}}",
        "=" * LARGEUR_RACCORD,
        "\nCARACTÉRISTIQUES DU COURS DE CADRE",
        f"  Diamètre de l'armature choisi               : HA{res_trans.get('phi_t', phi_t):2.0f}",
        f"  Nombre de brins verticaux (n)               : {res_trans.get('nb_brin', nb_brins):5.0f} brins",
        f"  Section totale d'un cours (A_t)             : {section_at_fournie:7.2f} cm²",
        "\nESPACEMENTS RÉGLEMENTAIRES",
        f"  Espacement initial au nu (S_t0)             : {res_trans.get('st0', 0):7.2f} cm",
        f"  Espacement théorique requis (S_t)           : {res_trans.get('st', 0):7.2f} cm",
        f"  Espacement maximal BAEL (S_tmax)            : {res_trans.get('st_max', 0):7.2f} cm"
    ])

    logger.info("Fin de l'export des résultats du ferraillage transversal.")
    return text_trans


def afficher_repartition_arm_trans(poutre, nb_brin: int, phi_t: int) -> str:
    """Génère la suite de répartition simplifiée des espacements (Séquence de Caquot)."""
    logger.info("Début de l'export de la répartition simplifiée des espacements.")
    if not hasattr(poutre, 'disposition') or not poutre.disposition:
        return "Répartition des cadres : Aucune séquence générée"

    # 1. Compter les occurrences successives des espacements
    compte = Counter(poutre.disposition)

    # 2. Nettoyer les clés pour enlever les ".0" inutiles si ce sont des entiers
    mon_dict = {
        str(int(k) if isinstance(k, (int, float)) and k.is_integer() else k): v
        for k, v in compte.items()
    }

    # 3. Construire la suite de répartition graphique
    elements_repartition = [f"{value} x {key}" for key, value in mon_dict.items()]
    repartition_str = " \n      •  ".join(elements_repartition)

    texte_final = (
        f"\nRépartition des cadres :\n"
        f"      •  {repartition_str}\n"
    )
    logger.info("Fin de l'export de la répartition simplifiée des espacements.")
    return texte_final


def afficher_result_fleche(poutre) -> list[str]:
    """Génère la note textuelle de vérification des conditions de flèche forfaitaires."""
    logger.info("Début de l'export de la vérification des conditions de flèche forfaitaires.")
    text_fleche = [
        "=" * LARGEUR_RACCORD,
        f"{'VÉRIFICATION DE LA FLÈCHE':^{LARGEUR_RACCORD}}",
        "=" * LARGEUR_RACCORD
    ]

    res_fleche = poutre.verifier_fleche()
    
    text_fleche.extend([
        f"  Flèche maximale admissible (f_lim)          : {res_fleche['f_lim_cm']:.2f} cm",
        f"  Flèche maximale calculée (f)                : {res_fleche['f_cm']:.2f} cm",
    ])
    
    # Ajout d'une ligne d'état claire
    est_valide = res_fleche['f_cm'] <= res_fleche['f_lim_cm']
    statut_fleche = "OK (f ≤ f_lim)" if est_valide else "HORS LIMITES (f > f_lim)"
    text_fleche.append(f"  ► Vérification de la condition de flèche    : {statut_fleche}")
    
    text_fleche.append("=" * LARGEUR_RACCORD)

    logger.info("Fin de l'export de la vérification des conditions de flèche forfaitaires.")
    return text_fleche