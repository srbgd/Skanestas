import time


class Exporter:
    def __init__(self, redis_db, influx_db, logger):
        self.redis_db = redis_db
        self.influx_db = influx_db
        self.logger = logger
        self.max_key = 0

    def export(self, keys):
        self.logger.info(f'Exporting keys: {keys}')
        for key in keys:
            self.max_key = max(self.max_key, key)
            value = self.redis_db.get(str(key))
            #self.influx_db

    @property
    def keys(self):
        self.logger.info('Get all keys')
        keys = [int(k) for k in self.redis_db.keys()]
        self.logger.info(f'Found keys: {keys}')
        return keys

    def run(self):
        if self.max_key is None:
            self.export(self.keys)

        while True:
            self.logger.info('Find new keys')
            new_keys = [k for k in self.keys if k > self.max_key]
            self.logger.info(f'New keys: {new_keys}')

            self.export(new_keys)

            self.max_key = max(new_keys + [self.max_key])

            time.sleep(0.25) 


def run_exporter(redis_db, influx_db, logger):
    logger.info('Start exporter')
    exporter = Exporter(redis_db=redis_db, influx_db=influx_db, logger=logger)
    exporter.run()
    logger.info('Finish exporter')