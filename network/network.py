import json, os, logging, time, traceback
from paramiko import SSHClient, AutoAddPolicy
from network.sonic_service.sonic_service import Sonic_service
from network.ocnos_service.ocnos_service import OcnosService
from network.parser.parser import Parser

class Network:
    def __init__(self, emulation_mode = False):
        self.topology = {}
        self.client = SSHClient()
        self.loadSSH()
        self.emulation_mode = emulation_mode
        self.soic_service = Sonic_service(self.client)
        self.ocnos_service = OcnosService(self.client)
        self.sonic_data = {}
        self.ocnos_data = {}
        self.parser = Parser()
        if self.emulation_mode:
            self.vm = SSHClient()
    
    def get_topology(self,config):
        #get type of devices
        for node in config.network_targets.get_nodes():
            self.topology[node.get_name().replace('"','')] = node.obj_dict["attributes"]

    def loadSSH(self):
    # load host ssh keys
        self.client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        # known_hosts policy
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def jsonOcnosParser(self):
        return {}

    def jsonSonicParse(self):
        outputDict = {}
        jsonDict = {}
        # parsing data into JSON
        for i in self.sonic_data:
            for j in self.sonic_data[i]:
                result = self.parser.parse_query_result(self.sonic_data[i][j])
                outputDict[j] = result
            jsonDict[i] = outputDict
            outputDict = {}
        return jsonDict

    def jsonParser(self):
        dict = {}
        dict.update(self.jsonSonicParse())
        dict.update(self.jsonOcnosParser())
        
        json_network = json.dumps(dict)
        # saving JSON output to a JSON file
        jsonFile = open("network_state.json", "w+")
        jsonFile.write(json_network)
        jsonFile.close()

    def thread_collect_config(self, config, ctl_service):
        periode = int(config.repeat_timer)
        while True:
            #collect the network configuration every periiode
            self.collect_config(config = config)
            ctl_service.post('network_state.json')

            time.sleep(periode)

    def collect_config(self, config):
        if self.emulation_mode:
            # if we will work with the emulated network
            self.vm.set_missing_host_key_policy(AutoAddPolicy())
            try:
                self.vm.connect(hostname = config.conf_file_contents['EMULATION']['hostname'],
                    port = int(config.conf_file_contents['EMULATION']['port']),
                    username = config.conf_file_contents['EMULATION']['username'],
                    password=config.conf_file_contents['EMULATION']['password'],
                    key_filename=config.conf_file_contents['EMULATION']['key_filename'])
            except:
                logging.error("Connection Error to emulator")
                return 0
        
        # read config file and foreach host create connection
        for device in self.topology:
            if self.emulation_mode:
                vmtransport = self.vm.get_transport()
                dest_addr = (self.topology[device]['mgmt_ip'].replace('"',''), 22)
                local_addr = ('localhost', 22) 
                vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
            else:
                vmchannel = None
            try:
                self.client.connect(
                    self.topology[device]['mgmt_ip'].replace('"',''),
                    username = self.topology[device]['username'].replace('"',''),
                    password = self.topology[device]['password'].replace('"',''),
                    allow_agent = False,
                    banner_timeout = 10,
                    sock=vmchannel)
                logging.debug("++++connected to device {} successful".format(device))
            except:
                logging.error("Error in connection to device {}".format(device))
                traceback.print_exc()
                continue
            if self.topology[device]['os'].replace('"','') == 'sonic':
                self.sonic_data.update(self.soic_service.collectData(device = device))
            elif self.topology[device]['os'].replace('"','') == 'ocnos':
                self.ocnos_data.update(self.ocnos_service.collectData(device = device))

            else:
                pass
        self.jsonParser()
        self.client.close()
    
    def config_network(self, network_config, cfg, backup = False):
        if self.emulation_mode:
            # if we will work with the emulated network
            self.vm.set_missing_host_key_policy(AutoAddPolicy())
            try:
                self.vm.connect(hostname = cfg.conf_file_contents['EMULATION']['hostname'],
                    port = int(cfg.conf_file_contents['EMULATION']['port']),
                    username = cfg.conf_file_contents['EMULATION']['username'],
                    password=cfg.conf_file_contents['EMULATION']['password'],
                    key_filename=cfg.conf_file_contents['EMULATION']['key_filename'])
            except:
                logging.error("Connection Error to emulator")
                traceback.print_exc()
                return 0

        for device in self.topology:
            if (device in network_config):
                # bind the vmchannel with each device to connect to the emulator if we are in the emulation mode otherwise NONE
                if self.emulation_mode:
                    vmtransport = self.vm.get_transport()
                    dest_addr = (self.topology[device]['mgmt_ip'].replace('"',''), 22) #edited#
                    local_addr = ('localhost', 22) #edited#
                    vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
                else:
                    vmchannel = None
                #connect to the device
                try:
                    self.client.connect(
                        self.topology[device]['mgmt_ip'].replace('"',''),
                        username = self.topology[device]['username'].replace('"',''),
                        password = self.topology[device]['password'].replace('"',''),
                        allow_agent = False,
                        banner_timeout = 10,
                        sock=vmchannel)
                    logging.debug("++++connected to device {} successful".format(device))
                except:
                    logging.error("Error in connection to device {}".format(device))
                    traceback.print_exc()
                    self.client.close()
                    if not backup:
                        self.config_network(network_config,cfg,backup=True)
                    break;

                if backup: # backup mode
                    if self.topology[device] == 'sonic':
                        Sonic_service.backup_device()
                    elif self.topology[device] == 'ocnos':
                        pass
                    else:
                        pass

                else: # regular configuration mode
                    if self.topology[device] == 'sonic':
                        
                        if(self.soic_service.config_device(device = device, config = network_config[device]) != 0):
                            logging.warning("Configuring device {} Failed, starting backup mode for all devices...")
                            self.client.close()
                            self.config_network(network_config,cfg,backup=True)
                            break;
                    elif self.topology[device] == 'ocnos':
                        self.ocnos_service.config_device(device=device, config= network_config[device])
                    else:
                        pass
                
