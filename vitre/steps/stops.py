"""Arrêts : base commune aux graphicages assemblés par la source (lignes 1 à 4, A à D, interurbaines, spéciales,
scolaires), qui décrivent souvent un même point physique sous plusieurs stop_id.

1. Noms : communes harmonisées (config.STOP_COMMUNES) puis noms corrigés (config.STOP_NAMES).
2. Quais opposés (config.OPPOSITE_QUAYS) : les passages au quai source sont reportés sur le quai dédié pour chaque couple
   ligne-sens qui dessert ce dernier.
3. Fusion des doublons (config.STOP_MERGES) : les passages de l'arrêt fusionné sont reportés sur l'arrêt conservé.
4. Les arrêts sans passage sont supprimés.
5. Zones d'arrêt : les quais de même nom (sans commune, casse, accents ni numéro final) distants d'au plus
   config.STOP_AREA_DISTANCE sont regroupés sous une station ZA_<quai principal>, au nom du quai principal (celui de la
   première ligne dans config.ROUTE_ORDER) ; ils perdent leur numéro final (« CENTRE 2 » → « CENTRE »).

La correspondance entre arrêts de la source et du GTFS produit, nécessaire au temps réel qui cite les stop_id de la
source, est publiée comme pour le GTFS Astuce :
- merged_stops (stop_id, merged_into_stop_id) : arrêt fusionné → arrêt conservé ;
- split_stops (source_stop_id, route_id, route_direction, dest_stop_id) : pour chaque arrêt source d'un quai opposé et
  chaque couple ligne-sens qui le dessert, le quai desservi.
L'arrêt d'un stop_id de la source est donc split_stops pour sa ligne et son sens, sinon merged_stops, sinon lui-même.
"""

import re
import unicodedata

import numpy as np
import pandas as pd

from .. import config
from ..gtfs import Feed, warn

NUMBER_SUFFIX = r"\s+\d+$"


def commune_name(name):
    commune, separator, rest = name.partition(" - ")
    if separator and commune in config.STOP_COMMUNES:
        return f"{config.STOP_COMMUNES[commune]} - {rest}"
    return name


def place_key(name):
    """Lieu d'un nom d'arrêt, pour comparer les graphicages : sans commune (préfixe en capitales), casse, accents,
    ponctuation ni numéro final."""
    commune, separator, rest = name.partition(" - ")
    if separator and commune == commune.upper():
        name = rest
    name = unicodedata.normalize("NFD", re.sub(NUMBER_SUFFIX, "", name)).encode("ascii", "ignore").decode().upper()
    return re.sub(r"[^A-Z0-9]+", " ", name).strip()


def distances(stops):
    """Matrice des distances (m) entre arrêts."""
    lat, lon = (np.radians(stops[column].astype(float).to_numpy()) for column in ("stop_lat", "stop_lon"))
    a = np.sin((lat[:, None] - lat) / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat) * np.sin((lon[:, None] - lon) / 2) ** 2
    return 2 * 6371000 * np.arcsin(np.sqrt(a))


def checked(mapping, known, label):
    unknown = sorted(k for k, v in mapping.items() if k not in known or v not in known)
    if unknown:
        warn(f"{label} ignorés, stop_id inconnus : {unknown}")
    return {k: v for k, v in mapping.items() if k not in unknown}


def rename(feed: Feed):
    stops = feed["stops"]
    stops["stop_name"] = stops["stop_name"].str.strip().str.replace(r"\s+", " ", regex=True).map(commune_name)
    unknown = sorted(set(config.STOP_NAMES) - set(stops["stop_id"]))
    if unknown:
        warn(f"Noms d'arrêts ignorés, stop_id inconnus : {unknown}")
    renamed = stops["stop_id"].isin(config.STOP_NAMES.keys())
    stops.loc[renamed, "stop_name"] = stops.loc[renamed, "stop_id"].map(config.STOP_NAMES)
    print(f"Arrêts renommés d'après la config : {renamed.sum()}")


def reassign(feed: Feed, served_by):
    """Reporte les passages des quais source sur leur quai opposé ; renvoie {(source, route_id, direction_id): quai}."""
    opposites = checked(config.OPPOSITE_QUAYS, set(feed["stops"]["stop_id"]), "Quais opposés")
    served = set(served_by)
    targets = {
        (source, route_id, direction_id): dest
        for source, dest in opposites.items()
        for stop_id, route_id, direction_id in served
        if stop_id == dest and (source, route_id, direction_id) in served
    }
    unused = sorted(set(opposites) - {source for source, _, _ in targets})
    if unused:
        warn(f"Quais opposés sans passage à reporter : {unused}")

    dests = served_by.map(targets)
    moved = dests.notna()
    feed["stop_times"].loc[moved, "stop_id"] = dests[moved]
    print(f"Passages reportés sur le quai opposé : {moved.sum()} ({len(targets)} couples arrêt-ligne-sens)")
    return targets


def merge(feed: Feed):
    stops, stop_times = feed["stops"], feed["stop_times"]
    merges = checked(config.STOP_MERGES, set(stops["stop_id"]), "Fusions")
    chained = sorted(k for k, v in merges.items() if v in merges)
    if chained:
        warn(f"Fusions ignorées, arrêt conservé lui-même fusionné : {chained}")
    trips_of = stop_times.groupby("stop_id")["trip_id"].agg(set)
    shared = sorted(k for k, v in merges.items() if trips_of.get(k, set()) & trips_of.get(v, set()))
    if shared:
        warn(f"Fusions ignorées, arrêts desservis par une même course : {shared}")
    merges = {k: v for k, v in merges.items() if k not in chained and k not in shared}

    stop_times["stop_id"] = stop_times["stop_id"].replace(merges)
    print(f"Arrêts fusionnés : {len(merges)}")
    return merges


def areas(feed: Feed):
    """Regroupe les quais de même lieu en zones d'arrêt."""
    stops = feed["stops"].reset_index(drop=True)
    keys = stops["stop_name"].map(place_key)
    near = distances(stops) <= config.STOP_AREA_DISTANCE
    group = np.arange(len(stops))
    for _, rows in keys.groupby(keys).groups.items():
        rows = list(rows)
        # Composantes connexes des quais de même lieu proches les uns des autres
        for i in rows:
            for j in rows:
                if i < j and near[i, j] and group[i] != group[j]:
                    group[group == group[j]] = group[i]

    # Quai principal : celui de la première ligne dans l'ordre du réseau (lignes urbaines avant interurbaines, spéciales
    # puis scolaires), puis le plus desservi
    stop_times = feed["stop_times"]
    sort_orders = stop_times["trip_id"].map(feed["trips"].set_index("trip_id")["route_id"]).map(
        pd.to_numeric(feed["routes"].set_index("route_id")["route_sort_order"])
    )
    stops["sort_order"] = stops["stop_id"].map(sort_orders.groupby(stop_times["stop_id"]).min())
    stops["departures"] = -stops["stop_id"].map(stop_times["stop_id"].value_counts())
    stops["group"] = group
    grouped = stops[stops["group"].duplicated(keep=False)]
    parents = []
    for _, quays in grouped.groupby("group"):
        main = quays.sort_values(["sort_order", "departures", "stop_id"]).iloc[0]
        parent_id = f"ZA_{main['stop_id']}"
        parents.append({
            **dict.fromkeys(stops.columns, ""),
            "stop_id": parent_id,
            "stop_name": re.sub(NUMBER_SUFFIX, "", main["stop_name"]),
            "stop_lat": f"{quays['stop_lat'].astype(float).mean():.6f}",
            "stop_lon": f"{quays['stop_lon'].astype(float).mean():.6f}",
            "location_type": "1",
            "wheelchair_boarding": "0",
        })
        stops.loc[quays.index, "parent_station"] = parent_id
        stops.loc[quays.index, "stop_name"] = quays["stop_name"].str.replace(NUMBER_SUFFIX, "", regex=True)
    stops = stops.drop(columns=["sort_order", "departures", "group"])
    feed["stops"] = pd.concat([pd.DataFrame(parents, columns=stops.columns), stops], ignore_index=True)
    print(f"Zones d'arrêt : {len(parents)}, regroupant {len(grouped)} quais")


def audit(feed: Feed):
    """Signale les arrêts distincts très proches, hors d'une même zone d'arrêt : doublons probables."""
    stops = feed["stops"][feed["stops"]["location_type"] != "1"].reset_index(drop=True)
    trips_of = feed["stop_times"].groupby("stop_id")["trip_id"].agg(set)
    close = np.argwhere(np.triu(distances(stops) <= config.DUPLICATE_STOP_DISTANCE, k=1))
    for i, j in close:
        a, b = stops.iloc[i], stops.iloc[j]
        same_area = a["parent_station"] != "" and a["parent_station"] == b["parent_station"]
        if not same_area and not trips_of[a["stop_id"]] & trips_of[b["stop_id"]]:
            warn(f"Doublon probable : {a['stop_id']} ({a['stop_name']}) / {b['stop_id']} ({b['stop_name']})")


def apply(feed: Feed):
    rename(feed)

    # (stop_id, route_id, direction_id) de chaque passage, tel que la source le décrit
    trips = feed["trips"].set_index("trip_id")
    stop_times = feed["stop_times"]
    served_by = pd.Series(
        list(zip(stop_times["stop_id"], stop_times["trip_id"].map(trips["route_id"]), stop_times["trip_id"].map(trips["direction_id"]))),
        index=stop_times.index,
    )
    targets = reassign(feed, served_by)
    merges = merge(feed)

    stops = feed["stops"]
    used = stops["stop_id"].isin(set(feed["stop_times"]["stop_id"]))
    print(f"Arrêts supprimés (fusionnés ou sans passage) : {(~used).sum()}")
    feed["stops"] = stops[used]
    areas(feed)
    audit(feed)

    feed["merged_stops"] = pd.DataFrame(sorted(merges.items()), columns=["stop_id", "merged_into_stop_id"], dtype=str)
    sources = {source for source, _, _ in targets}
    feed["split_stops"] = pd.DataFrame(
        sorted(
            (stop_id, route_id, direction_id, merges.get(dest, dest))
            for stop_id, route_id, direction_id in set(served_by)
            if stop_id in sources
            for dest in [targets.get((stop_id, route_id, direction_id), stop_id)]
        ),
        columns=["source_stop_id", "route_id", "route_direction", "dest_stop_id"],
        dtype=str,
    )
    print(f"{(feed['stops']['location_type'] != '1').sum()} quais")
