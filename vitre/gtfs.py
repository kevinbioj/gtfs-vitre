"""GTFS en mémoire : une DataFrame par table (nom sans .txt), toutes les valeurs en texte brut.

Toutes les tables de la source sont conservées et les valeurs sont réécrites à l'identique.
"""

import sys
import zipfile
from pathlib import Path

import pandas as pd

Feed = dict[str, pd.DataFrame]

SORT_COLUMNS = {
    "routes": ["route_sort_order", "route_id"],
    "trips": ["route_id", "direction_id", "service_id", "trip_headsign"],
    "stop_times": ["trip_id", "stop_sequence"],
}
INTEGER_COLUMNS = {"route_sort_order", "direction_id", "stop_sequence"}


def warn(message):
    print(message, file=sys.stderr)


def text(value):
    return "" if value is None else str(value)


def read_table(file) -> pd.DataFrame:
    return pd.read_csv(file, dtype=str, keep_default_na=False, encoding="utf-8-sig")


def read(path) -> Feed:
    """Lit un GTFS zippé ou un répertoire GTFS."""
    path = Path(path)
    if path.is_dir():
        return {file.stem: read_table(file) for file in sorted(path.glob("*.txt"))}
    with zipfile.ZipFile(path) as archive:
        return {Path(name).stem: read_table(archive.open(name)) for name in archive.namelist() if name.endswith(".txt")}


def tables(feed: Feed):
    """(nom de fichier, contenu CSV) des tables non vides."""
    for name, table in feed.items():
        if not table.empty:
            yield f"{name}.txt", sort(name, table).to_csv(index=False, lineterminator="\n")


def write(feed: Feed, path):
    path = Path(path)
    temp_path = path.with_suffix(".tmp")
    with zipfile.ZipFile(temp_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, content in tables(feed):
            archive.writestr(name, content)
    temp_path.replace(path)


def write_dir(feed: Feed, directory):
    for name, content in tables(feed):
        (Path(directory) / name).write_text(content, encoding="utf-8")


def sort(name, table):
    columns = [column for column in SORT_COLUMNS.get(name, []) if column in table.columns]
    if not columns:
        return table
    return table.sort_values(
        columns,
        key=lambda values: pd.to_numeric(values, errors="coerce") if values.name in INTEGER_COLUMNS else values,
        na_position="last",
        kind="stable",
    )


def patch(table, key, patches):
    """Applique {identifiant: {colonne: valeur}} aux lignes de la table, en ajoutant les colonnes manquantes."""
    index = pd.Index(table[key])
    for row_id, fields in patches.items():
        rows = index.get_indexer_for([row_id])
        rows = rows[rows >= 0]
        for column, value in fields.items():
            if column not in table.columns:
                table[column] = ""
            table.iloc[rows, table.columns.get_loc(column)] = text(value)


def restrict_to_trips(feed: Feed, trip_ids) -> Feed:
    """Nouveau feed limité aux courses données et à ce qu'elles utilisent (même logique que gtfs_kit)."""
    feed = dict(feed)
    trips = feed["trips"] = feed["trips"][feed["trips"]["trip_id"].isin(trip_ids)]
    trip_ids = set(trips["trip_id"])
    routes = feed["routes"] = feed["routes"][feed["routes"]["route_id"].isin(trips["route_id"])]
    stop_times = feed["stop_times"] = feed["stop_times"][feed["stop_times"]["trip_id"].isin(trip_ids)]

    stops = feed["stops"]
    stop_ids = set(stop_times["stop_id"])
    if "parent_station" in stops.columns:
        stop_ids |= set(stops.loc[stops["stop_id"].isin(stop_ids), "parent_station"]) - {""}
    feed["stops"] = stops[stops["stop_id"].isin(stop_ids)]

    for name in ("calendar", "calendar_dates"):
        if name in feed:
            feed[name] = feed[name][feed[name]["service_id"].isin(trips["service_id"])]
    if "agency_id" in routes.columns:
        feed["agency"] = feed["agency"][feed["agency"]["agency_id"].isin(routes["agency_id"])]
    if "frequencies" in feed:
        feed["frequencies"] = feed["frequencies"][feed["frequencies"]["trip_id"].isin(trip_ids)]
    if "shapes" in feed and "shape_id" in trips.columns:
        feed["shapes"] = feed["shapes"][feed["shapes"]["shape_id"].isin(trips["shape_id"])]
    if "transfers" in feed:
        transfers = feed["transfers"]
        feed["transfers"] = transfers[transfers["from_stop_id"].isin(stop_ids) & transfers["to_stop_id"].isin(stop_ids)]
    return feed


def restrict_to_routes(feed: Feed, route_ids) -> Feed:
    trip_ids = feed["trips"].loc[feed["trips"]["route_id"].isin(route_ids), "trip_id"]
    return restrict_to_trips(feed, trip_ids)
