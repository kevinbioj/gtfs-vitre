"""Girouettes : trip_headsign = nom du dernier arrêt desservi ; les stop_headsign de la source sont supprimés."""

import pandas as pd

from ..gtfs import Feed


def apply(feed: Feed):
    stop_times = feed["stop_times"]
    stop_times.drop(columns="stop_headsign", errors="ignore", inplace=True)
    last_stop_ids = (
        stop_times.assign(sequence=pd.to_numeric(stop_times["stop_sequence"]))
        .sort_values("sequence", kind="stable")
        .groupby("trip_id")["stop_id"]
        .last()
    )
    last_stop_names = last_stop_ids.map(feed["stops"].set_index("stop_id")["stop_name"])

    trips = feed["trips"]
    trips["trip_headsign"] = trips["trip_id"].map(last_stop_names).fillna("")
