import json, os, logging, time, traceback
from paramiko import SSHClient, AutoAddPolicy
from network.sonic_service.sonic_service import Sonic_service
from network.parser.parser import Parser

class Network:
    def __init__(self, simulation_mode = False):
        self.topology = {}
        self.client = SSHClient()
        self.loadSSH()
        self.simulation_mode = simulation_mode
        self.soic_service = Sonic_service(self.client)
        self.sonic_data = {}
        self.ocnos_data = {}
        self.parser = Parser()
        if self.simulation_mode:
            self.vm = SSHClient()
    
    def get_topology(self,config):
        #get type of devices
        self.topology={device : 'sonic' for device in json.loads(config.conf_file_contents['TARGETS']['devices'])}

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
        if self.simulation_mode:
            # if we will work with the simulated network
            self.vm.set_missing_host_key_policy(AutoAddPolicy())
            try:
                self.vm.connect(hostname = config.conf_file_contents['SIMULATION']['hostname'],
                    port = int(config.conf_file_contents['SIMULATION']['port']),
                    username = config.conf_file_contents['SIMULATION']['username'],
                    password=config.conf_file_contents['SIMULATION']['password'],
                    key_filename=config.conf_file_contents['SIMULATION']['key_filename'])
            except:
                logging.error("Connection Error to simulator")
                return 0
        
        # read config file and foreach host create connection
        for device in self.topology:
            if self.simulation_mode:
                vmtransport = self.vm.get_transport()
                dest_addr = (device, 22) #edited#
                local_addr = ('localhost', 22) #edited#
                vmchannel = vmtransport.open_channel("direct-tcpip", dest_addr, local_addr)
            else:
                vmchannel = None
            try:
                self.client.connect(
                    device,
                    username = config.conf_file_contents['AUTH']['username'],
                    password = config.conf_file_contents['AUTH']['password'],
                    allow_agent = False,
                    banner_timeout = 10,
                    sock=vmchannel)
                logging.debug("++++connected to device {} successful".format(device))
            except:
                logging.error("Error in connection to device {}".format(device))
                traceback.print_exc()
                continue
            if self.topology[device] == 'sonic':
                self.sonic_data.update(self.soic_service.collectData(device = device))
            elif self.topology[device] == 'ocnos':
                pass
            else:
                pass
        self.jsonParser()
        self.client.close()