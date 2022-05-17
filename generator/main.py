import logging
import time
import redis
import sys
import os


from bootstrup import bootstrup
from job import run_job


LOG = None
DB = redis.Redis(host=os.environ['REDIS_HOST'], port=6379)


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
    while not bootstrup(db=DB, logger=logger):
        logger.warning('Failed to start worker. Retrying')
        time.sleep(1)
    try:
        run_job(db=DB, logger=logger)
    except Exception:
        logger.exception('Job failed with exception')
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
