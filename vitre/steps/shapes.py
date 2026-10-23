"""Tracés : ceux de la source sont supprimés, puis générés par pfaedle d'après config.OSM_PATH.

pfaedle travaille sur un répertoire GTFS : le feed y est écrit puis relu une fois les tracés générés.
"""

import shutil
import subprocess
import tempfile

from .. import config, gtfs
from ..gtfs import Feed, warn


def drop(feed: Feed):
    """Supprime shapes.txt et ses références (trips.shape_id, stop_times.shape_dist_traveled)."""
    feed.pop("shapes", None)
    feed["trips"].drop(columns="shape_id", errors="ignore", inplace=True)
    feed["stop_times"].drop(columns="shape_dist_traveled", errors="ignore", inplace=True)


def generate(feed: Feed) -> Feed:
    if not config.OSM_PATH.exists():
        warn(f"{config.OSM_PATH} absent : aucun tracé")
        return feed
    if shutil.which("pfaedle") is None:
        warn("pfaedle absent du PATH : aucun tracé")
        return feed

    with tempfile.TemporaryDirectory() as directory:
        gtfs.write_dir(feed, directory)
        subprocess.run(["pfaedle", "--inplace", "-x", str(config.OSM_PATH), directory], check=True)
        feed = gtfs.read(directory)
    print(f"{feed['shapes']['shape_id'].nunique()} tracés")
    return feed
