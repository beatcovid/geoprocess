"""

encode business names to geolocation using Google Places API

"""
import logging
import os
import sys
import time
from datetime import timedelta

import pandas as pd
import requests
import requests_cache

from geoprocess.settings import GOOGLE_PLACES_API_KEY

from .settings import CACHE_PATH

logging.basicConfig(level=logging.INFO)


requests_cache.install_cache(CACHE_PATH, expire_after=timedelta(days=60))

BACKOFF_TIME = 30
QUERY_LIMIT = 0


def google_geocode(query, region=None, api_key=None, return_full_response=False):

    GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/geocode/json"

    query_params = {}

    query_components = {}

    url_params = {
        "key": GOOGLE_PLACES_API_KEY,
    }

    if region:
        query_params["region"] = region

    if "postal_code" in query:
        query_components["postal_code"] = query["postal_code"]

    if "country" in query:
        query_params["region"] = query["country"]
        query_components["country"] = query["country"]
        query.pop("country", None)

    url_params["components"] = "|".join(f"{k}:{v}" for k, v in query_components.items())

    results = requests.get(GOOGLE_PLACES_URL, params=url_params).json()

    logging.debug(results)

    if not "status" in results:
        raise Exception("Invalid response")

    if results["status"] == "REQUEST_DENIED":
        raise Exception("API Key or other request denied error")

    if results["status"] == "OVER_QUERY_LIMIT":
        logging.warn("Hit Query Limit! Backing off for a bit.")
        time.sleep(5)  # sleep for 30 minutes
        return google_geocode(query, region, api_key, return_full_response)

    if results["status"] == "ZERO_RESULTS":
        return None

    if not results["status"] == "OK":
        logging.error("Error results for %s", query)
        raise Exception("No results: {}".format(results["status"]))

    if len(results["results"]) == 0:
        logging.error("No results for %s", query)
        return None

    cand = results["results"][0]
    return cand


def lookup_placeid(place_id, api_key=None, retry=0):

    GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/details/json"

    url_params = {"key": GOOGLE_PLACES_API_KEY, "place_id": place_id}

    results = requests.get(GOOGLE_PLACES_URL, params=url_params).json()

    if not "status" in results:
        raise Exception("Invalid response")

    if results["status"] == "REQUEST_DENIED":
        raise Exception("API Key or other request denied error")

    if results["status"] == "OVER_QUERY_LIMIT":
        logging.warn("Hit Query Limit! Backing off for a bit.")
        time.sleep(5)  # sleep for 30 minutes
        lookup_placeid(place_id)

    if results["status"] == "ZERO_RESULTS":
        return None

    if not results["status"] == "OK":
        logging.error("Error results for %s", place_id)
        raise Exception("No results: {}".format(results["status"]))

    if not "result" in results:
        logging.error("No result for %s", place_id)
        raise Exception("No result: {}".format(place_id))

    return results["result"]


def find_placeid(input_file, address_column_name="userdetail_location"):
    if not os.path.isfile(input_file):
        raise Exception(f"Not a valid file {input_file}")

    data = pd.read_csv(input_file, encoding="utf8")

    if address_column_name not in data.columns:
        raise ValueError(f"Missing geo column {address_column_name} in input data")

    geos = data[address_column_name].tolist()

    results = []
    queries = 0

    for _, record in data.iterrows():
        geo = record[address_column_name]

        # @TODO need to parse the geojson

        logging.debug("Looking up place_id for location %s", geo)

        # Geocode the address with google
        try:
            geocode_result = google_geocode(geo)
            queries += 1
        except Exception as e:
            logging.exception(e)
            logging.error("No result for {}".format(geo))

        logging.info(geocode_result)
        results.append({**record, **geocode_result})

        if QUERY_LIMIT and QUERY_LIMIT > 0 and queries >= QUERY_LIMIT:
            logging.info("Hit query limit of {}".format(QUERY_LIMIT))
            break

        # Print status every 100 geos
        if len(results) % 10 == 0:
            logging.info("Completed {} of {} address".format(len(results), len(geos)))

    # All done
    logging.info(
        "Finished geocoding {} addresses using {} queries".format(len(results), queries)
    )

    return pd.DataFrame(results)


def place_autocomplete(query, region=None, api_key=None, return_full_response=False):

    GOOGLE_PLACES_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"

    query_params = {}

    query_components = {}

    url_params = {
        "key": GOOGLE_PLACES_API_KEY,
        "input": query,
    }

    if region:
        query_params["region"] = region

    if "postal_code" in query:
        query_components["postal_code"] = query["postal_code"]

    if "country" in query:
        query_params["region"] = query["country"]
        query_components["country"] = query["country"]
        query.pop("country", None)

    url_params["components"] = "|".join(f"{k}:{v}" for k, v in query_components.items())

    results = requests.get(GOOGLE_PLACES_URL, params=url_params).json()

    logging.debug(results)

    if not "status" in results:
        raise Exception("Invalid response")

    if results["status"] == "REQUEST_DENIED":
        raise Exception("API Key or other request denied error")

    if results["status"] == "OVER_QUERY_LIMIT":
        logging.warn("Hit Query Limit! Backing off for a bit.")
        time.sleep(5)  # sleep for 30 minutes
        return google_geocode(query, region, api_key, return_full_response)

    if results["status"] == "ZERO_RESULTS":
        return None

    if not results["status"] == "OK":
        logging.error("Error results for %s", query)
        raise Exception("No results: {}".format(results["status"]))

    if len(results["predictions"]) == 0:
        logging.error("No results for %s", query)
        return None

    cand = results["predictions"]
    return cand
