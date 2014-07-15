class HpitClientSettings:
    instance = None
    HPIT_URL_ROOT = 'http://23.239.14.159:80'
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
