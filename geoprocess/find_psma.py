import logging
import os

import geopandas as gpd
from shapely.geometry import Point

from .settings import BASE_PATH

logger = logging.getLogger("geoprocess.find_psma")


def read_shape(shape_path):
    shape_path = os.path.join(BASE_PATH, shape_path)

    if not os.path.isfile(shape_path):
        logger.error("Could not find shape {}".format(shape_path))
        return None

    return gpd.read_file(shape_path)


LGA = [
    {
        "state": "NSW",
        "shape": read_shape("data/LGA2019/Standard/NSW_LGA_POLYGON_shp.shx"),
    },
    {
        "state": "QLD",
        "shape": read_shape("data/LGA2019/Standard/QLD_LGA_POLYGON_shp.shx"),
    },
    {
        "state": "VIC",
        "shape": read_shape("data/LGA2019/Standard/VIC_LGA_POLYGON_shp.shx"),
    },
    {"state": "NT", "shape": read_shape("data/LGA2019/Standard/NT_LGA_POLYGON_shp.shx"),},
    {
        "state": "TAS",
        "shape": read_shape("data/LGA2019/Standard/TAS_LGA_POLYGON_shp.shx"),
    },
    {"state": "SA", "shape": read_shape("data/LGA2019/Standard/SA_LGA_POLYGON_shp.shx"),},
    {"state": "WA", "shape": read_shape("data/LGA2019/Standard/WA_LGA_POLYGON_shp.shx"),},
]


SA3 = [
    {
        "state": "NSW",
        "shape": read_shape("data/2016ABS/Standard/NSW_SA3_2016_POLYGON_shp.shx"),
    },
    {
        "state": "QLD",
        "shape": read_shape("data/2016ABS/Standard/QLD_SA3_2016_POLYGON_shp.shx"),
    },
    {
        "state": "VIC",
        "shape": read_shape("data/2016ABS/Standard/VIC_SA3_2016_POLYGON_shp.shx"),
    },
    {
        "state": "NT",
        "shape": read_shape("data/2016ABS/Standard/NT_SA3_2016_POLYGON_shp.shx"),
    },
    {
        "state": "TAS",
        "shape": read_shape("data/2016ABS/Standard/TAS_SA3_2016_POLYGON_shp.shx"),
    },
    {
        "state": "SA",
        "shape": read_shape("data/2016ABS/Standard/SA_SA3_2016_POLYGON_shp.shx"),
    },
    {
        "state": "WA",
        "shape": read_shape("data/2016ABS/Standard/WA_SA3_2016_POLYGON_shp.shx"),
    },
]


def find_lga(lng, lat):
    p = Point(lat, lng)
    for state in LGA:
        for _, bound in state["shape"].iterrows():
            if p.within(bound.geometry):
                return bound["LGA_PID"]


def find_sa3(lng, lat):
    p = Point(lat, lng)
    for state in SA3:
        for _, bound in state["shape"].iterrows():
            if p.within(bound.geometry):
                return bound["SA3_16PPID"]
