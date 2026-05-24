import math

GAMMA_B = 1.5
GAMMA_S = 1.15
COEF_EQUIVALENCE = 15
MU_LIM = 0.372
ALPHA_LIM = 0.612

COEF_FISSURATION = {
    "rond lisse": 1.0,
    "HA": 1.6,
    "HA inf. 6mm": 1.3,
}

DIAMETRES = [6, 8, 10, 12, 14, 16, 20, 25, 32]
SECTIONS_HA = {d: round((math.pi * d**2 / 4), 2) for d in DIAMETRES}
SUITE_CAQUOT = [7, 8, 9, 10, 11, 13, 16, 20, 25, 30, 35, 40]

# Conversions
KN_TO_MN = 1e-3
KN_TO_N = 1e3
M2_TO_CM2 = 1e4
M_TO_CM = 100
M_TO_MM = 1e3
CM2_TO_MM2 = 1e2
CM_TO_MM = 10