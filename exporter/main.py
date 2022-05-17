import logging
import redis
import sys
import os

from exporter import run_exporter
from influxdb_client import InfluxDBClient

LOG = None
REDIS_DB = redis.Redis(host=os.environ['REDIS_HOST'], port=6379)
INFLUX_DB = InfluxDBClient.from_env_properties()


def getLogger():
    global LOG
    if LOG is None:
        LOG = logging.getLogger(__name__)
        LOG.setLevel(logging.INFO)
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt="%Y-%m-%dT%H:%M:%S%z")
        handler.setFormatter(formatter)
        LOG.addHandler(handler)
    return LOG


def main():
    logger = getLogger()
    try:
        run_exporter(redis_db=REDIS_DB, influx_db=INFLUX_DB, logger=logger)
    except Exception:
        logger.exception('Exporter failed with exception')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
