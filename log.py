import logging
import os

from cfg import Config

cfg = Config()

log_dir = '/home/ubuntu/logs'

class Log(logging.Logger):
    def __init__(self):
        logging.Logger.__init__(self, 'analytics')
        self.setLevel(logging.DEBUG)

        sh = logging.StreamHandler()
        self.addHandler(sh)
        if cfg.env != 'development':
            log_file = os.path.join(log_dir, 'analyticsService.log')
            fh = logging.FileHandler(log_file)
            fh.setLevel(logging.INFO)
            self.addHandler(fh)
