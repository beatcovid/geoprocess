import logging

from geoprocess.controllers import update_geoplots

logger = logging.getLogger("beatcovid.geoprocess")
logger.setLevel(logging.DEBUG)

if __name__ == "__main__":
    try:
        update_geoplots()
    except KeyboardInterrupt as e:
        logger.error("User interrupted")
    except Exception as e:
        logger.exception(e)
