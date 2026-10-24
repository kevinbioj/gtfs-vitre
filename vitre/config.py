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
    "3314": "LG14",
    "3315": "LG15",
}

# Ordre des lignes (route_sort_order et tri de routes.txt) : chaque motif (expression régulière sur le route_id) forme un
# groupe, trié par route_id ; les lignes qui ne correspondent à aucun motif passent à la fin
ROUTE_ORDER = [
    "1", "2", "3", "4", "A", "B", "C", "D", "10", "11", "12", "14",
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
    "10": {"route_text_color": "FFFFFF", "route_long_name": "Rannée <> Vitré"},
    "11": {"route_text_color": "FFFFFF", "route_long_name": "La Guerche-de-Bretagne <> Vitré"},
    "12": {"route_long_name": "Val d'Izé <> Vitré"},
    "14": {"route_text_color": "FFFFFF", "route_long_name": "Le Pertre <> Vitré"},
    "LG14": {"route_color": "00FF40"},
    "LG15": {"route_color": "00FF40"},
    "SBC": {"route_long_name": "Spécial Broons-Châteaubourg"},
    "SCH": {"route_long_name": "Spécial La Clé des Champs <> Châteaubourg Collèges"},
    "SMPV": {"route_long_name": "Spécial Montreuil-sous-Pérouse <> Gare SNCF"},
    "SPLB": {"route_long_name": "Spécial Pocé-les-Bois <> Gare SNCF"},
}

# Communes des noms d'arrêts « COMMUNE - Nom », par graphie de la source → graphie retenue
STOP_COMMUNES = {
    "ARGENTRE": "ARGENTRE DU PLESSIS",
    "CHATILLON": "CHATILLON EN VENDELAIS",
    "DOMALIN": "DOMALAIN",
    "GENNES": "GENNES SUR SEICHE",
    "LA GUERCHE": "LA GUERCHE DE BRETAGNE",
    "LA GUERCHE BRETAGNE": "LA GUERCHE DE BRETAGNE",
    "LOUVIGNE": "LOUVIGNE DE BAIS",
    "MONTREUIL SS/PER.": "MONTREUIL SOUS PEROUSE",
    "POCE": "POCE LES BOIS",
    "SAINT GERMAIN": "SAINT GERMAIN DU PINEL",
    "ST DIDIER": "SAINT DIDIER",
    "ST GERMAIN": "SAINT GERMAIN DU PINEL",
    "ST GERMAIN DU PINEL": "SAINT GERMAIN DU PINEL",
    "ST JEAN": "SAINT JEAN SUR VILAINE",
    "ST M'HERVE": "SAINT M'HERVE",
    "VAL D' IZE": "VAL D'IZE",
}

# Noms d'arrêts corrigés, par stop_id (après correction des communes). Les variantes d'un même lieu reçoivent le même
# nom, ce qui les regroupe en une zone d'arrêt.
STOP_NAMES = {
    # Châteaubourg (lignes A à D) : casse, accents, soulignés
    "CHGBRET1": "La Bretonnière",
    "CHGBRET2": "La Bretonnière",
    "CHGBRU1": "Rue de la Brunelière (Accès Gare)",
    "CHGCHEN1": "Le Chenot",
    "CHGCIME1": "Cimetière",
    "CHGCIME2": "Cimetière",
    "CHGCOTA1": "Les Cottages",
    "CHGDRPA1": "Rue de Paris",
    "CHGDRPA2": "Rue de Paris",
    "CHGGALI1": "Galilée",
    "CHGGALM1": "La Galmandière",
    "CHGGAUL1": "Gaultière",
    "CHGLAND1": "La Lande",
    "CHGRDVI1": "Route de Vitré",
    "CHGRDVI2": "Route de Vitré",
    "CHGTREO1": "La Tréolière",
    "CHGTREO2": "La Tréolière",
    "CHGVERO1": "La Verronière",
    # Vitré (lignes 1 à 4)
    "VITMASS1": "Massonnais",
    "VITMASS2": "Massonnais",
    "VITRPER1": "Rond-Point d'Erbrée",
    # Commune sans séparateur, circuit dans le nom
    "BRIEL4": "BRIELLES - BELLE VUE",
    "CHATE5": "CHATEAUBOURG - JULES VERNE",
    "CHATE7": "CHATEAUBOURG - LA BOURLIERE",
    # Variantes d'un même lieu
    "CHAT21": "CHATEAUBOURG - PARC IFFELDORF",
    "LA_GU7": "LA GUERCHE DE BRETAGNE - CHAMP DE FOIRE",
    "LA_GUE": "LA GUERCHE DE BRETAGNE - ZA LA BOUGEOIRE",
    "LOUVI1": "LOUVIGNE DE BAIS - ZA LA CHARDRONNAIS",
    "POCE_5": "POCE LES BOIS - RUE DU PETIT MORIN",
    "VAL_42": "VAL D'IZE - ZA LE BOURGNEUF",
    "VITRE6": "VITRE - GARE",
}

# Quais opposés des lignes interurbaines : les courses de l'été (services 24 et 25) desservent le quai source dans les deux
# sens, celles du reste de l'année un quai dédié (souvent « … 2 ») dans l'un d'eux. Les passages au quai source sont
# reportés sur le quai dédié pour chaque couple ligne-sens qui dessert ce dernier.
OPPOSITE_QUAYS = {
    # Ligne 10
    "ARGEN1": "ARGE44",
    "ARGENT": "ARGE45",
    "DOMALA": "DOMA48",
    "ETREL2": "ETRE26",
    "LA_GU2": "LA_G15",
    "LA_GUE": "LA_G17",
    "MOUTIE": "MOUT11",
    "RANNEE": "RANN16",
    "VITRE1": "VITR22",
    # Lignes 10 et 11
    "LA_GU1": "LA_G16",
    # Ligne 11
    "BAIS_": "BAIS30",
    "DOMAL1": "DOMA50",
    "DOMAL2": "DOMA49",
    "LA_GU3": "LA_G18",
    "LOUVI1": "LOUV11",
    "LOUVIG": "LOUV12",
    "TORCE": "TORCE1",
    "VITRE2": "VITR23",
    # Ligne 12
    "MONTRE": "MONT19",
    "VAL_D1": "VAL_43",
    "VAL_D_": "VAL_42",
    "VITRE3": "VITR24",
    # Ligne 14
    "ERBREE": "ERBR16",
    "LE_PER": "LE_P26",
    "MONDEV": "MONDE8",
    "VITRE4": "VITR25",
}

# Arrêts en doublon d'un graphicage à l'autre (stop_id fusionné → stop_id conservé) : un même point physique, le quai
# urbain étant conservé de préférence
STOP_MERGES = {
    # Vitré : lignes 14, spéciales et scolaires sur les quais des lignes 1 à 4
    "VITR25": "VITBGAS1",
    "VITRE4": "VITBGAS2",
    "VITRE7": "VITFOIR2",
    "VITRE8": "VITCHAM1",
    "VITRE9": "VITTERT1",
    # Châteaubourg : spéciales et scolaires sur les quais des lignes A à D
    "CHAT19": "CHGCOPE1",
    "CHAT20": "CHGGALI1",
    "CHATE2": "CHGPPRI2",
    "CHATE6": "CHGTREO2",
    "CHATE9": "CHGCHEN1",
    "CHATEA": "CHGSTME1",
    # Saint-Jean-sur-Vilaine : la ligne A sur l'arrêt des scolaires, « Centre » ne disant pas la commune
    "SJVCENT1": "ST_JE3",
    # Scolaires et spéciales entre eux (mêmes coordonnées à quelques mètres près, noms parfois différents)
    "BRIEL5": "ARGEN7",
    "BROON1": "BROONS",
    "CHAT33": "CHATE3",
    "DOMA31": "DOMA13",
    "GENN15": "GENNE2",
    "TORC13": "TORCE8",
}

# Distance maximale (m) entre les quais de même nom regroupés en une zone d'arrêt
STOP_AREA_DISTANCE = 100

# Distance (m) en deçà de laquelle deux arrêts distincts, hors d'une même zone d'arrêt, sont signalés comme doublons
# probables
DUPLICATE_STOP_DISTANCE = 10
