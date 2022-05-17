import time

from consts import REDIS_TTL


class Bootstrup:

    PING_TIMEOUT = 60

    def __init__(self, db, logger):
        self.db = db
        self.logger = logger
        self.bootstrup_order = [
            self.wait_ping,
            self.init_keys,
        ]

    def start(self):
        for f in self.bootstrup_order:
            try:
                result = f()
            except Exception:
                self.logger.exception()
                result = False
            if not result:
                return False
        return True

    def wait_ping(self):
        start_time = time.time()
        while time.time() - start_time < self.PING_TIMEOUT:
            self.logger.info('PING')
            if self.db.ping():
                return True
            time.sleep(1)
        return False
    
    def init_keys(self):
        dbsize = self.db.dbsize()
        self.logger.info(f'DBSIZE: {dbsize}')
        if dbsize == 0:
            value = ';'.join(['0']*10)
            current_time = int(time.time())
            result = self.db.set(current_time, value, ex=REDIS_TTL, nx=True)
            self.logger.info(f'Set result: {result}')
            if result not in ['OK', None, b'OK']:
                return False
        return True


def bootstrup(db, logger):
    logger.info('Bootstrup started')
    bootstraper = Bootstrup(db, logger)
    result = bootstraper.start()
    logger.info('Bootstrup finished')
    return result