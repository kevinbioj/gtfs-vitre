"""Lignes : le route_short_name de la source, corrigé par config.ROUTE_SHORT_NAMES puis config.TECHNICAL_SHORT_NAME,
devient le route_id, puis config.ROUTE_PATTERNS et config.ROUTES sont appliqués. Un route_long_name identique au nom
court est vidé.

Les lignes de même route_short_name sont fusionnées en une seule (la première déclarée donne ses champs), ce qui résout
aussi les route_id en double de la source dès lors que leurs noms courts corrigés coïncident (3510 et 10 → 10). Un
route_id partagé par des noms courts différents reste ambigu : ses courses vont à la première ligne déclarée.
"""

import re

from .. import config
from ..gtfs import Feed, patch, warn


def apply(feed: Feed) -> Feed:
    routes = feed["routes"]
    unknown = sorted(set(config.ROUTE_SHORT_NAMES) - set(routes["route_short_name"]))
    if unknown:
        warn(f"Noms courts ignorés, route_short_name inconnus : {unknown}")
    source, long_names = routes["route_short_name"], routes["route_long_name"]
    promoted = (
        ~source.isin(config.ROUTE_SHORT_NAMES.keys())
        & source.str.fullmatch(config.TECHNICAL_SHORT_NAME)
        & long_names.str.fullmatch(r"\S+")
    )
    short_names = source.replace(config.ROUTE_SHORT_NAMES).mask(promoted, long_names)
    short_names = short_names.mask(short_names == "", routes["route_id"])
    print(f"Noms courts techniques remplacés par le nom long : {promoted.sum()}")

    new_ids = short_names.groupby(routes["route_id"]).unique()
    for route_id, ids in new_ids[new_ids.map(len) > 1].items():
        warn(f"route_id {route_id} ambigu, partagé par les lignes {list(ids)} : courses rattachées à {ids[0]}")
    trips = feed["trips"]
    trips["route_id"] = trips["route_id"].map(new_ids.str[0])

    routes = routes.assign(
        route_id=short_names, route_short_name=short_names, route_long_name=long_names.mask(long_names == short_names, "")
    )
    merged = routes["route_id"].duplicated()
    if merged.any():
        print(f"Lignes fusionnées : {sorted(set(routes.loc[merged, 'route_id']))}")
    feed["routes"] = routes = routes[~merged].reset_index(drop=True)

    unknown = sorted(set(config.ROUTES) - set(routes["route_id"]))
    if unknown:
        warn(f"Lignes ignorées, route_id inconnus : {unknown}")
    routes["route_sort_order"] = sort_orders(routes["route_id"])
    for pattern, fields in config.ROUTE_PATTERNS.items():
        matching = routes[routes["route_id"].str.fullmatch(pattern)]
        patch(routes, "route_id", {
            row["route_id"]: {column: value.format(**row) for column, value in fields.items()}
            for row in matching.to_dict("records")
        })
    patch(routes, "route_id", config.ROUTES)
    print(f"{len(routes)} lignes")
    return feed


def sort_orders(route_ids):
    """route_sort_order d'après config.ROUTE_ORDER."""
    last = len(config.ROUTE_ORDER)
    groups = {
        route_id: next((index for index, pattern in enumerate(config.ROUTE_ORDER) if re.fullmatch(pattern, route_id)), last)
        for route_id in route_ids
    }
    unordered = sorted(route_id for route_id, group in groups.items() if group == last)
    if unordered:
        warn(f"Lignes hors config.ROUTE_ORDER, placées à la fin : {unordered}")
    order = sorted(groups, key=lambda route_id: (groups[route_id], route_id))
    return route_ids.map({route_id: str(index) for index, route_id in enumerate(order)})
