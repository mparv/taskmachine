import configparser
import datetime
import hashlib


class ConfigUtils(object):
    def __init__(self, filename, logger):
        config = configparser.ConfigParser()
        self.logger = logger
        config.read(filename)

        self.config_dict = dict(config['settings'])
        self.logger.info("Config loaded: {}".format(self.config_dict))
    
    def get_hosturi(self):
        return self.config_dict.get('host_uri', 'http://127.0.0.1:5000')

    def get_scrape_urls(self):
        return self.config_dict.get("scrape_urls", "")

    def get_db_models(self):
        return self.config_dict.get("db_models", "")

    def get_cert_location(self):
        return self.config_dict.get("cert_location", "")

    def get_key_location(self):
        return self.config_dict.get("key_location", "")

class Utils(object):
    @staticmethod
    def cmp_dates(d1, d2):
        date1 = datetime.datetime.strptime(d1, '%Y-%m-%d').date()
        date2 = datetime.datetime.strptime(d2, '%Y-%m-%d').date()

        if d1 >= d2:
            return True

        return False

    @staticmethod
    def get_md5sum(data):
        md5sum = hashlib.md5(data.encode()).hexdigest()
        return md5sum
