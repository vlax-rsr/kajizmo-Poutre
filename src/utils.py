# src/utils.py

def safe_float(value, default: float = 0.0) -> float:
    """Convertit une valeur en float de façon robuste.
    
    Gère les None, les espaces inutiles, remplace les virgules par des points
    et renvoie une valeur par défaut en cas d'erreur de conversion.
    """
    if value is None:
        return default
        
    text = str(value).strip().replace(",", ".")
    if not text:
        return default
        
    try:
        return float(text)
    except ValueError:
        return default