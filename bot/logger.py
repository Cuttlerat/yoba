from datetime import datetime
from dateutil.tz import tzlocal
import json


class Watchman(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Watchman, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Log(metaclass=Watchman):

    levels ={"DEBUG": 0,
             "INFO": 1,
             "WARN": 2,
             "ERROR": 3,
             "CRITICAL": 4}

    def __init__(self):
        from config import Config
        from odr.container import register
        config = Config()
        register(config)
        self.level = config.log_level

    def print(self, level="DEBUG", message={}):
        if level not in self.levels:
            level="ERROR"
            message={"error": "Log level is incorrect",
                     "failed_message": {"log_level": level, **message}}

        if self.levels[level] >= self.levels[self.level]:
            message.update({"timestamp": self.get_timestamp(),
                            "log_level": level})
            print(json.dumps(message))

    def get_timestamp(self):
        return datetime.now(tzlocal()).strftime("%Y-%m-%dT%H:%M:%SZ")


def log_print(message, level="DEBUG", **kwargs):
    log_message = {"message": message, **kwargs}
    log = Log()
    log.print(level, log_message)
