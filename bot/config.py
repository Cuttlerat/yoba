import glob

import yaml
from sqlalchemy import create_engine


class Config:
    def __init__(self, file_path="./config/config.y*ml"):
        cfg = None
        for filename in glob.glob(file_path):
            with open(filename, 'r') as ymlfile:
                cfg = yaml.load(ymlfile)
        if cfg is None:
            raise FileNotFoundError("There is no config file")

        self.__tg_token = cfg['tokens']['tg_token'] if 'tg_token' in cfg['tokens'] else None
        self.__weather_token = cfg['tokens']['weather_token'] if 'weather_token' in cfg['tokens'] else None

        self.__db_host = cfg['database']['host'] if 'host' in cfg['database'] else None

        self.__tg_mode = cfg['telegram']['mode'] if 'mode' in cfg['telegram'] else None
        self.__tg_webhook_port = cfg['telegram']['webhook_port'] if 'webhook_port' in cfg['telegram'] else None
        self.__tg_webhook_url = cfg['telegram']['webhook_url'].format(self.__tg_token) if 'webhook_url' in cfg[
            'telegram'] else None
        self.__tg_listen_ip = cfg['telegram']['listen_ip'] if 'listen_ip' in cfg['telegram'] else None

        self.__tg_admins = cfg['admins'] if 'admins' in cfg else []

        self.__database = 'sqlite:///{}'.format(self.__db_host) if self.__db_host is not None else None
        self.__engine = create_engine(self.__database) if self.__database is not None else None

    def telegram_token(self):
        if self.__tg_token is None:
            raise NotImplementedError("Telegram token in config-file is not declared")
        return self.__tg_token

    def weather_token(self):
        if self.__weather_token is None:
            raise NotImplementedError("Weather token in config-file is not declared")
        return self.__weather_token

    def telegram_mode(self):
        if self.__tg_mode is None:
            raise NotImplementedError("TG mode in config-file is not declared")
        return self.__tg_mode

    def webhook_port(self):
        if self.__tg_webhook_port is None:
            raise NotImplementedError("Webhook port in config-file is not declared")
        return self.__tg_webhook_port

    def webhook_url(self):
        if self.__tg_webhook_url is None:
            raise NotImplementedError("Webhook url in config-file is not declared")
        return self.__tg_webhook_url

    def listen_ip(self):
        if self.__tg_listen_ip is None:
            raise NotImplementedError("Listen IP in config-file is not declared")
        return self.__tg_listen_ip

    def database_host(self):
        if self.__db_host is None:
            raise NotImplementedError("Path to database in config-file is not declared")
        return self.__db_host

    def admins(self):
        return self.__tg_admins

    def database(self):
        if self.__database is None:
            raise NotImplementedError("Path to database in config-file is not declared")
        return self.__database

    def engine(self):
        if self.__engine is None:
            raise NotImplementedError("Path to database in config-file is not declared")
        return self.__engine
