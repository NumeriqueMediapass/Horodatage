"""
Module de gestion des versions de l'application.

Ce module fournit :
- La version actuelle de l'application
- Une fonction de comparaison des versions
- Des utilitaires pour la gestion sémantique des versions
"""

VERSION = "1.1.0"


def compare_versions(current: str, latest: str) -> bool:
    """Compare deux versions et détermine si une mise à jour est nécessaire.
    
    Utilise la comparaison sémantique des versions (MAJOR.MINOR.PATCH).
    Une version plus récente est disponible si latest > current.
    
    Args:
        current (str): Version actuelle de l'application (ex: "1.0.0")
        latest (str): Dernière version disponible (ex: "1.1.0")
        
    Returns:
        bool: True si une mise à jour est disponible, False sinon
        
    Examples:
        >>> compare_versions("1.0.0", "1.1.0")
        True
        >>> compare_versions("1.1.0", "1.1.0")
        False
        >>> compare_versions("1.2.0", "1.1.0")
        False
    """
    def version_tuple(v):
        """Convertit une chaîne de version en tuple d'entiers."""
        return tuple(map(int, v.split('.')))
    
    return version_tuple(latest) > version_tuple(current)
