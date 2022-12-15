import os, logging
import configparser
import pydot

class Config:
    def __init__(self):
        self.repeat_timer = os.environ.get('REPEAT_TIMER','10')
        self.controller_url = os.environ.get('CONTROLLER_URL','http://10.11.200.125:8787')
        self.conf_file_path = os.environ.get('CONF_FILE', "config/config.ini")
        self.network_targets_file_path = os.environ.get('NET_TARGETS', 'config/network_targets.dot')
        self.conf_file_contents = self.read_config()
        self.network_targets = self.read_network_targets()
    
    def read_config(self):
        '''opens and loads initial config file to memory'''
        try:
            config = configparser.ConfigParser()
            config.read(self.conf_file_path)
            config.sections()
            return config
        except IOError:
            logging.error("*********** ERROR reading config file **********")
            exit(1)

    def read_network_targets(self):
        '''reads the network topology file and loads it to memory as a dictionary using pydot'''
        try:
            print(self.network_targets_file_path)
            graph = pydot.graph_from_dot_file(self.network_targets_file_path)
            return graph[0]
        except IOError:
            logging.error("*********** ERROR reading network targets file **********")
            exit(1)
