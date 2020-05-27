import csv
import email.utils
import json
import logging
import os
import sys
from datetime import datetime
from pprint import pprint

from dotenv import load_dotenv
from pymongo import MongoClient

from geoprocess.find_psma import find_lga, find_sa3
from geoprocess.google_geo import google_geocode, lookup_placeid, place_autocomplete
from geoprocess.settings import MONGO_CONNECT_URL

load_dotenv()

logger = logging.getLogger("geoprocess")
logging.basicConfig(level=logging.INFO)
logger.setLevel(logging.INFO)

mongo_connection = MongoClient(MONGO_CONNECT_URL)


def flatten_google_place(place, prefix):
    ac = place["address_components"]

    flattened = {}

    for component in ac:
        for ctype in component["types"]:
            if not ctype == "political":
                flattened[prefix + "_" + ctype] = component["short_name"]

    return flattened


def get_granuality(flat_geo, prefix):
    FIELDS = [
        f"{prefix}_postal_code",
        f"{prefix}_locality",
        f"{prefix}_administrative_area_level_2",
        f"{prefix}_administrative_area_level_1",
        f"{prefix}_country",
    ]

    for field in FIELDS:
        if field in flat_geo:
            return field[len(prefix) + 1 :]

    return "country"


def update_geoplots():
    """
        just a simple q
    """

    db = mongo_connection.prod_covid19_api_docdb.instances
    query = {"_geo_processed": {"$ne": True}}

    processed = 0
    updated = 0
    place_fields = ["userdetail_city", "travel_country"]

    for a in db.find(query).sort("_submission_time", -1):
        for place_field in place_fields:
            if place_field in a:

                if not type(a[place_field]) is str:
                    continue

                if " " in a[place_field]:
                    continue

                try:
                    p = lookup_placeid(a[place_field])
                except Exception as e:
                    logger.error("Could not find place id for: {}".format(a[place_field]))
                    logger.error(e)
                    continue

                p_flat = flatten_google_place(p, place_field)

                if (
                    place_field + "_country" in p_flat
                    and p_flat[place_field + "_country"] == "AU"
                    and (
                        place_field + "_locality" in p_flat
                        or place_field + "_postal_code" in p_flat
                    )
                ):
                    if not place_field + "_lga_id" in a:
                        lgs = find_lga(
                            p["geometry"]["location"]["lat"],
                            p["geometry"]["location"]["lng"],
                        )

                        if lgs:
                            p_flat[place_field + "_lga_id"] = lgs

                    if not place_field + "_sa3_id" in a:
                        sa3 = find_sa3(
                            p["geometry"]["location"]["lat"],
                            p["geometry"]["location"]["lng"],
                        )

                        if sa3:
                            p_flat[place_field + "_sa3_id"] = sa3

                p_flat[place_field + "_granuality"] = get_granuality(p_flat, place_field)

                if (
                    place_field + "_country" in p_flat
                    and p_flat[place_field + "_country"] == "AU"
                    and (
                        place_field + "_administrative_area_level_1" in p_flat
                        or "userdetail_city_postal_code" in p_flat
                    )
                ):
                    p_flat[place_field + "_state"] = p_flat[
                        place_field + "_administrative_area_level_1"
                    ]

                p_flat["_geo_processed"] = True

                pprint(p_flat)

                try:
                    db.update_one(
                        {"_id": a["_id"]}, {"$set": p_flat},
                    )
                except Exception as e:
                    logger.error(
                        "Db error on updating place_id: {} {}".format(
                            a["_id"], place_field
                        )
                    )
                    logger.error(e)
                    continue

                logger.info(
                    "Updated {} {} -> {}".format(place_field, a["_id"], a[place_field])
                )
                updated += 1

        processed += 1

    print("Processed {} and updated {}".format(processed, updated))
