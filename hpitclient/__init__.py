from .plugin import Plugin
from .tutor import Tutor

class HpitClientSettings:
    instance = None
    HPIT_URL_ROOT = 'http://23.239.14.159:80'
    REQUESTS_LOG_LEVEL = 'debug'

    def __new__(cls):
        if cls.instance:
            raise Exception("Settings has already been created.")

    @classmethod
    def settings(cls):
        if not cls.instance:
            cls.instance = HpitClientSettings()

        return cls.instance

settings = HpitClientSettings.settings()

__all__ = [
    'Plugin',
    'Tutor',
    'settings'
]