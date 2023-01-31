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
        logging.info("output of {} : {}".format(cmd,output))
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
    
    def ctl2ocnos_parse(self, config):
        for interface_ip in config['INTERFACE']:
            interface = interface_ip.split('|')[0]
            ip = interface_ip.split('|')[1] 
        commands = ['enable', 'configure terminal', 'interface '+interface, 'ip address '+ip, 'exit', 'commit', 'end', 'disable']

        return commands

    def backup_device(self):
        cmd = "copy running-config file:/running-config-bkp"
        self.exe_cmd(cmd)
        cmd = "sudo config reload -y"
        self.exe_cmd(cmd)


    def config_device(self, device, config):
        commands = self.ctl2ocnos_parse(config)
        #open sftp session to get and put files from and to the remote device
        ftp_client=self.client.open_sftp()
        
        #execute configuration commands
        for cmd in commands:
            self.exe_cmd(cmd)
    
    
