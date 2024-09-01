__all__ = ['Config']
import sys
import logging.config
import tomllib
import atexit
from .std import *

class Config():
    initlog_status = False

    def __new__(cls, *args, **kwargs):
        if not hasattr(Config, 'instance'):
            Config.instance = super().__new__(cls, *args, **kwargs)
        return Config.instance

    def __init__(self):
        if not hasattr(self, 'config'):
            self.config = {}

    def load(self, config_path: str):
        with open(config_path, "rb") as file:
            self.config = tomllib.load(file)

    def initlog(self, name: str = 'NOTSET', attach: object = None):
        if Config.initlog_status:
            logger = logging.getLogger(name)
            logger.warning('Skip initializing logging because logging has already been initialized.')
        else:
            if self['logging']:
                logging.config.dictConfig(self['logging'])
            else:
                logging.basicConfig()
            queue_handler = logging.getHandlerByName("QueueHandler")
            if queue_handler is not None:
                queue_handler.listener.start()
                atexit.register(queue_handler.listener.stop)
            logger = logging.getLogger(name)
            def log_exception(exc_type, exc_value, exc_traceback):
                if issubclass(exc_type, KeyboardInterrupt):
                    logger.warning("KeyboardInterrupt")
                    #sys.__excepthook__(exc_type, exc_value, exc_traceback)
                    sys.exit(1)
                logger.critical('Uncaught exception:', exc_info=(exc_type, exc_value, exc_traceback))
            sys.excepthook = log_exception
            Config.initlog_status = True
        self.attachlog(name, attach)
        return logger

    def attachlog(self, name: str = 'NOTSET', attach: object = None):
        logger = logging.getLogger(name)
        if attach:
            log_attr = ['debug','info','warning','error','critical','exception']
            for attr in log_attr:
                setattr(attach, attr, getattr(logger, attr))

    def __getitem__(self, key):
        return self.config.get(key, {})

    def __str__(self):
        return logdict(self.config, indent = 1)