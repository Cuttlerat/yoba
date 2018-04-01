import glob

import yaml
from sqlalchemy import create_engine


class Config:
    def __init__(self):
        for filename in glob.glob('./config/config.y*ml'):
            with open(filename, 'r') as ymlfile:
                cfg = yaml.load(ymlfile)

        self.__tg_token = cfg['tokens']['tg_token']
        self.__weather_token = cfg['tokens']['weather_token'] if 'weather_token' in cfg['tokens'] else None

        self.__db_host = cfg['database']['host']

        self.__tg_mode = cfg['telegram']['mode']
        self.__tg_webhook_port = cfg['telegram']['webhook_port']
        self.__tg_webhook_url = cfg['telegram']['webhook_url'].format(self.__tg_token)
        self.__tg_listen_ip = cfg['telegram']['listen_ip']

        self.__tg_admins = cfg['admins']

        self.__database = 'sqlite:///{}'.format(self.__db_host)
        self.__engine = create_engine(self.__database)

    def telegram_token(self):
        return self.__tg_token

    def weather_token(self):
        if self.__weather_token is None:
            raise NotImplementedError("Weather token in config-file is not declared")
        return self.__weather_token

    def telegram_mode(self):
        return self.__tg_mode

    def webhook_port(self):
        return self.__tg_webhook_port

    def webhook_url(self):
        return self.__tg_webhook_url

    def listen_ip(self):
        return self.__tg_listen_ip

    def database_host(self):
        return self.__db_host

    def admins(self):
        return self.__tg_admins

    def databse(self):
        return self.__database

    def engine(self):
        return self.__engine
