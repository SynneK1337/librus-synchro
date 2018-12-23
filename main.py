from librus import LibrusSession
from configparser import ConfigParser

class Cfg(ConfigParser):
    parser = ConfigParser()
    def __init__(self):
        self.parser.read("config.cfg")
        self.librus = self.parser["librus_credentials"]
        self.librus.login = self.librus["login"]
        self.librus.password = self.librus["password"]
