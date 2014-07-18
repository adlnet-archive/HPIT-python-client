class HpitClientSettings:
    instance = None
    HPIT_URL_ROOT = 'https://www.hpit-project.org'
    REQUESTS_LOG_LEVEL = 'debug'

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            raise Exception("Settings has already been created.")

        cls.instance = object.__new__(cls)
        cls.instance.__init__(*args, **kwargs)
        return cls.instance

    @classmethod
    def settings(cls):
        if not cls.instance:
            cls.instance = HpitClientSettings()

        return cls.instance
