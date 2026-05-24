def verifier_cisaillement(poutre) -> dict:
    """Verifie la contrainte de cisaillement par rapport a la limite admissible."""
    return {
        "tau_u_MPa": round(poutre.tau_u_MPa, 3),
        "tau_lim_MPa": poutre.tau_lim_MPa,
        "condition": poutre.tau_u_MPa <= poutre.tau_lim_MPa,
    }