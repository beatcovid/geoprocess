from geoprocess.controllers import update_geoplots

if __name__ == "__main__":
    try:
        update_geoplots()
    except KeyboardInterrupt as e:
        logger.error("User interrupted")
    except Exception as e:
        logger.exception(e)
