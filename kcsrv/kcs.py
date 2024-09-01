__all__ = ['KCS']
from .utils.config import Config

class KCS():
    def __init__(self, config_path: str = 'config.toml'):
        self.config = Config()
        self.config.load(config_path)
        self.logger = self.config.initlog('kcs', self)
        self.debug(f'Config loaded\n{self.config}')
        self.server = None
        self.info('KC.Server initialization completed')
    def start(self):
        self.info(f'KC.Server starts on')

    def stop(self):
        self.info(f'KC.Server stopped')