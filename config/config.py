import os, logging
import configparser

class Config:
    def __init__(self):
        self.repeat_timer = os.environ.get('REPEAT_TIMER','10')
        self.controller_url = os.environ.get('CONTROLLER_URL','http://127.0.0.1:8787')
        self.conf_file_path = os.environ.get('CONF_FILE',"config/config.ini")
        self.conf_file_contents = self.read_config()
    def read_config(self):
        # open config file
        try:
            config = configparser.ConfigParser()
            config.read(self.conf_file_path)
            config.sections()
            return config
        except IOError:
            logging.error("*********** ERROR reading config file **********")
            exit(1)
