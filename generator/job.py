import imp
import threading
import time

from random import random
from consts import REDIS_TTL


class JobException(Exception):
    pass


class Job(threading.Thread):
    def __init__(self, db, logger):
        super().__init__()
        self.db = db
        self.logger = logger
        self.__result = None
        self.last_key = None

    @property
    def result(self):
        return self.__result

    @staticmethod
    def mutate(values):
        return [max(v + (-1 if random() < 0.5 else 1), 0) for v in values]

    def get_first_missing_key(self):
        # note: this is a quick operation because all keys have short ttl
        actual_keys = [int(k) for k in self.db.keys()]
        self.logger.info(f'Actual keys: {sorted(actual_keys)}')
        if not actual_keys:
            raise JobException('There are no keys left. Generation aborted')

        min_key = min(actual_keys)
        current_time = int(time.time())
        if min_key > current_time:
            raise JobException(f'Incorrect data in db. Key: {min_key}, current time: {current_time}')

        expected_keys = range(min_key, current_time + 1)
        missing = set(expected_keys) - set(actual_keys)
        return min(missing) if missing else None

    def run(self):
        while True:
            missing = self.get_first_missing_key()
            self.logger.info(f'First missing key: {missing}')

            if missing:
                previous_value = self.db.get(str(missing - 1))
                self.logger.info(f'Previous value: {previous_value}')

                mutated_value = self.mutate(map(int, previous_value.decode().split(';')))
                self.logger.info(f'Mutated value: {mutated_value}')

                self.db.set(missing, ';'.join(map(str, mutated_value)).encode(), ex=REDIS_TTL, nx=True)
            else:
                # all keys are in db
                time.sleep(0.25)


def run_job(db, logger, wait=True):
    logger.info('Run job')
    job = Job(db, logger)
    job.start()
    if wait:
        job.join()
    logger.info('Finished job')
    return job.result
