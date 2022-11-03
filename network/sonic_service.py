from paramiko import SSHClient, AutoAddPolicy
import os, json
from ..utils.query.query import Query
from ..utils.parser.parser import Parser
class Sonic_service:
    def __init__(self, client, config):
        self.commandList = ['show runningconfiguration all | grep -A 11 -i metadata', 'show arp', 'show ip route', 'show acl table', 'show acl rule', 'show lldp table', 'show vlan config',
               'vtysh -c "show interface"', 'show ip bgp neighbors']
        self.headerList = ['metadata', 'arp', 'ipRoute', 'aclTable', 'aclRule', 'lldp', 'vlan', 'interface', 'bgp']
        self.query_dictionary = {}
        self.client = client
        self.cfg = config
        self.parser = Parser()
    
    def loadSSH(self):
        # load host ssh keys
        self.client.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        # known_hosts policy
        self.client.set_missing_host_key_policy(AutoAddPolicy())

    def collectData(self):
        # read config file and foreach host create connection
        for device in json.loads(self.cfg.conf_file_contents['TARGETS']['devices']):
            self.client.connect(
                device,
                username=self.cfg.conf_file_contents['AUTH']['username'],
                password=self.cfg.conf_file_contents['AUTH']['password'])
            self.deviceList.append(device)
            for i in self.commandList:
                current_query = Query(device, i)
                current_query.send_query(self.client)
                self.query_dictionary[current_query.device + '.' + current_query.cmd] = current_query
        self.client.close()

    def jsonParse(self):
        outputDict = {}
        n = 0
        # parsing data into JSON
        for i in self.query_dictionary:
            result = self.parser.parse_query_result(self.query_dictionary[i])
            outputDict[self.headerList[n % len(self.headerList)]] = result
            if ((n+1) % len(self.headerList)) == 0:
                self.jsonDict[self.deviceList[int(n / len(self.headerList))]] = outputDict
                outputDict = {}
            n += 1
        json_network = json.dumps(self.jsonDict)

        # saving JSON output to a JSON file
        jsonFile = open("data.json", "w+")
        jsonFile.write(json_network)
        jsonFile.close()

    