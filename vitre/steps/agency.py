"""Agence : remplacée par config.AGENCY, à laquelle toutes les lignes sont rattachées."""

import pandas as pd

from .. import config
from ..gtfs import Feed


def apply(feed: Feed):
    feed["agency"] = pd.DataFrame([config.AGENCY], dtype=str)
    feed["routes"]["agency_id"] = config.AGENCY["agency_id"]
