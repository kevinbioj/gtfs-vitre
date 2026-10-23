"""Pipeline GTFS MOVA (Vitré Communauté) : python -m vitre <gtfs-source.zip> <gtfs-sortie.zip>"""

import argparse
import time
from contextlib import contextmanager
from pathlib import Path

from . import gtfs
from .steps import agency, headsigns, routes, shapes


@contextmanager
def step(label):
    print(f"== {label}")
    start = time.perf_counter()
    yield
    print(f"   ({time.perf_counter() - start:.1f} s)")


def main():
    parser = argparse.ArgumentParser(description="Construit le GTFS MOVA retraité.")
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    with step("Lecture"):
        feed = gtfs.read(args.source)
    with step("Agence"):
        agency.apply(feed)
    with step("Lignes"):
        feed = routes.apply(feed)
    with step("Girouettes"):
        headsigns.apply(feed)
    with step("Suppression des tracés"):
        shapes.drop(feed)
    with step("Tracés"):
        feed = shapes.generate(feed)
    with step(f"Écriture de {args.output}"):
        gtfs.write(feed, args.output)


if __name__ == "__main__":
    main()
