VERSION = "1.1.0"

def parse_version(version_str):
    """Convertit une chaîne de version en tuple pour comparaison"""
    return tuple(map(int, version_str.split('.')))

def compare_versions(current, latest):
    """Compare deux versions et retourne True si une mise à jour est disponible"""
    current_parts = parse_version(current)
    latest_parts = parse_version(latest)
    return latest_parts > current_parts
