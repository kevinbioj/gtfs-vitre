from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Réseau OpenStreetMap utilisé par pfaedle pour générer les tracés ; s'il est absent, le GTFS est produit sans tracés
OSM_PATH = ROOT / "mova.osm.pbf"

# Agence unique du réseau, à laquelle toutes les lignes sont rattachées
AGENCY = {
    "agency_id": "MOVA",
    "agency_name": "MOVA",
    "agency_url": "https://mova.bzh",
    "agency_timezone": "Europe/Paris",
    "agency_lang": "fr",
    "agency_phone": "+33222195070",
    "agency_fare_url": "https://www.mova.bzh/titres-et-tarifs/",
}

# Noms courts techniques de la source (3101, 3511…) : le route_long_name les remplace lorsqu'il est un code sans espace
# (AR01, 11…)
TECHNICAL_SHORT_NAME = r"\d{4}"

# Noms courts corrigés explicitement, par route_short_name de la source, prioritaires sur la règle ci-dessus. Les noms
# courts sont corrigés avant de devenir le route_id.
ROUTE_SHORT_NAMES = {
    "3510": "10",
    "3601": "SBC",
    "3603": "SMPV",
}

# Ordre des lignes (route_sort_order et tri de routes.txt) : chaque motif (expression régulière sur le route_id) forme un
# groupe, trié par route_id ; les lignes qui ne correspondent à aucun motif passent à la fin
ROUTE_ORDER = [
    "1", "2", "3", "4", "A", "B", "C", "D", "10", "11", "12", "14", "3314", "3315",
    r"S.*", r"18H.*", r"AR.*", r"CH.*", r"LG.*", r"VI.*",
]

# Lignes, par motif (expression régulière sur le route_id) : chaque entrée remplace les champs de routes.txt indiqués,
# les valeurs pouvant reprendre les champs de la ligne ({route_short_name}…). Appliqué avant ROUTES.
ROUTE_PATTERNS = {
    r"(18H|AR|CH|LG|VI).*": {"route_long_name": "Circuit scolaire {route_short_name}"},
}

# Lignes, par route_id (= route_short_name corrigé). Chaque entrée remplace les champs de routes.txt indiqués.
ROUTES = {
    "1": {"route_text_color": "FFFFFF", "route_long_name": "Rond-Point d'Erbrée <> Briqueterie"},
    "2": {"route_text_color": "FFFFFF", "route_long_name": "Haut Chalet <> Saint-Etienne"},
    "3": {"route_text_color": "FFFFFF", "route_long_name": "Massonnais <> René Dumont - Lactalis"},
    "4": {"route_text_color": "FFFFFF", "route_long_name": "Grand Fougeray <> Pont Billon"},
    "A": {"route_text_color": "FFFFFF", "route_long_name": "Marpiré <> Châteaubourg Gare Nord"},
    "B": {"route_text_color": "000000", "route_long_name": "Domagné <> Châteaubourg Gare Nord"},
    "C": {"route_text_color": "FFFFFF", "route_long_name": "Broons-sur-Vilaine <> Châteaubourg Gare Nord"},
    "D": {"route_text_color": "FFFFFF", "route_long_name": "ZA Gaultière - Galmandière <> Châteaubourg Gare Nord"},
    "10": {"route_long_name": "Rannée <> Vitré"},
    "11": {"route_long_name": "La Guerche-de-Bretagne <> Vitré"},
    "12": {"route_long_name": "Val d'Izé <> Vitré"},
    "14": {"route_long_name": "Le Pertre <> Vitré"},
    "SBC": {"route_long_name": "Spécial Broons-Châteaubourg"},
    "SCH": {"route_long_name": "Spécial La Clé des Champs <> Châteaubourg Collèges"},
    "SMPV": {"route_long_name": "Spécial Montreuil-sous-Pérouse <> Gare SNCF"},
    "SPLB": {"route_long_name": "Spécial Pocé-les-Bois <> Gare SNCF"},
}
