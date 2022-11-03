import argparse, logging
from paramiko import SSHClient, AutoAddPolicy
from config.config import Config

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)




deviceList = []
query_dictionary = {}
jsonDict = {}

def run(args):
    cfg = Config()
    logging.debug("username is {}".format(cfg.conf_file_contents['AUTH']['username']))
    logging.debug("url is {}".format(cfg.controller_url))


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description= "proxy service to collect datad fro network and configuring the network",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter )
    args_parser.add_argument("-s", "--simulation", action="store_true", help="Simulation mode")
    args = args_parser.parse_args()
    run(args)
    print("done")
    