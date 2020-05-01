
from huey import RedisHuey, crontab

from geoprocess.controllers import update_geoplots
from geoprocess.settings import REDIS_HOST

huey = RedisHuey('beatcovid.geoprocess', host=REDIS_HOST)

@huey.periodic_task(crontab(minute="*/5"))
def process_geos():
    update_geoplots()
