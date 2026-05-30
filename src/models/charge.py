# src/models/charge.py
def get_efforts(G_kN_m, Q_kN_m):
    return [G_kN_m, Q_kN_m]

def moment_elu(G_kN_m, Q_kN_m, l_m):
    q = 1.35 * G_kN_m + 1.50 * Q_kN_m

    return q * l_m**2 / 8

def moment_ser(G_kN_m, Q_kN_m, l_m):
    q = G_kN_m + Q_kN_m

    return q * l_m**2 / 8

def effort_tranchant_elu(G_kN_m, Q_kN_m, l_m):
    q = 1.35 * G_kN_m + 1.50 * Q_kN_m

    return q * l_m / 2

def sollicitations(G_kN_m, Q_kN_m, l_m):
    M_u = moment_elu(G_kN_m, Q_kN_m, l_m)
    M_ser = moment_ser(G_kN_m, Q_kN_m, l_m)
    V_u = effort_tranchant_elu(G_kN_m, Q_kN_m, l_m)

    return {
        "M_u": M_u,
        "M_ser": M_ser,
        "V_u": V_u
    }