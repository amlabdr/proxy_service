from network.query.query import Query
import logging, json
class OcnosService:
    def __init__(self, client):
        # dictionary of commands that will be run for each node on network
        self.command_dict = {
                #'metadata': 'show runningconfiguration all | grep -A 11 -i metadata', # no equivalent
                'arp': 'show arp',
                'ipRoute': 'show ip route',
                #'aclTable': 'show acl table',
                #'aclRule': 'show acl rule',
                'lldp': 'show lldp neighbors breif',
                'vlan': 'show vlan brief',
                'interface': 'show interface',
                'bgp': 'show ip bgp neighbors'
        }
        self.client = client
    
    def exe_cmd(self,cmd):
        stdin, stdout, stderr = self.client.exec_command(cmd)
        output = ''
        status = 0
        for line in stdout.readlines():
            output += line
        for line in stderr.readlines():
            status=1
            output += line
        return status

    def collectData(self,device):
        #initialize device dict
        query_dictionary={}
        query_dictionary[device] = {}
        for key in self.command_dict:
            current_query = Query(device, self.command_dict[key], key)
            current_query.send_query(self.client)
            query_dictionary[current_query.device][current_query.template] = current_query
        logging.debug("data collected from {} is : {} ".format(device,query_dictionary))
        return query_dictionary
    
    def ctl2sonic_parse(self, config):
        return config

    def backup_device(self):
        cmd = "copy running-config file:/running-config-bkp"
        self.exe_cmd(cmd)
        cmd = "sudo config reload -y"
        self.exe_cmd(cmd)


    def config_device(self, device, config):
        config = self.ctl2sonic_parse(config)
        #open sftp session to get and put files from and to the remote device
        ftp_client=self.client.open_sftp()
        with open('config.json', 'w') as outfile:
            json.dump(config, outfile,indent=4)
        outfile.close()
        ftp_client.put('config.json','config.json')
        #create back-up config
        cmd = "sudo cp /etc/sonic/config_db.json /etc/sonic/config_db.json.bk"
        self.exe_cmd(cmd)
        status = 0
        cmd = "sonic-cfggen -j config.json"
        if self.exe_cmd(cmd)!=0:
            status =1
            logging.error("Error in json format ")
        cmd = "sudo config load config.json -y"
        if self.exe_cmd(cmd)!=0:
            status = 1
            logging.error("Error in loading config from file")
        cmd = "sudo config save -y"
        if self.exe_cmd(cmd)!=0:
            status = 1
            logging.error("Error in saving config")
        if status == 0:
            logging.info("{} Configured successfully".format(device))
            self.client.close()
            return 0
        else:
            logging.warning("{} Configuration not successful ... backup of the old configuration".format(device))
            self.backup_device()
            self.client.close()
            return -1
        
    
    
