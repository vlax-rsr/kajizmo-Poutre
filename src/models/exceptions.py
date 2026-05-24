""" Classe d'exception """

class BaelError(Exception):
    """Exception de base pour les erreurs du moteur BAEL."""
    pass

class SectionDepasseeError(BaelError):
    """Levée quand la section d'acier dépasse le maximum admissible (A_max)."""
    pass

class BetonInsuffisantError(BaelError):
    """Levée quand le pivot ou le moment dépasse les limites physiques (ex: mu > 0.5)."""
    pass