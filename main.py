import argparse, logging, time
from threading import Thread
from config.config import Config
from controller.controller_service import Controller_service
from network.network import Network

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def run(emmulation_mode):
    cfg = Config()
    #logging.debug("username is {}".format(cfg.conf_file_contents['CONTROLLER_AUTH']['username']))
    logging.debug("url is {}".format(cfg.controller_url))
    Ctl_service = Controller_service(config = cfg)
    network = Network(emmulation_mode)
    network.get_topology(cfg)
    logging.info("config is {}".format(network.topology))
    #Now it's time to authenticate to the controller.
    authentication_period = int(cfg.conf_file_contents['CONTROLLER_AUTH']['authentification_period'])
    thread_authentification = Thread(target=Ctl_service.controllerAuthentication,args=(authentication_period,))
    thread_authentification.start()

    Thread_get_config = Thread(target=network.thread_collect_config, args=(cfg,Ctl_service))
    #Thread_get_config.start()



    Ctl_service.run_http_server(network = network,cfg=cfg)
    
    #test post file of requirements.txt
    #Ctl_service.post('requirements.txt')

    


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description= "proxy service to collect datad fro network and configuring the network",
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter )
    args_parser.add_argument("-e", "--emulation", action="store_true", help="Emulation mode")
    args = args_parser.parse_args()
    emmulation_mode = vars(args)['emulation']
    run(emmulation_mode)
    print("done")
    