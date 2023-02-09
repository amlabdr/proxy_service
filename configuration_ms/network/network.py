import json, os, logging, traceback, re, sys
from paramiko import SSHClient, AutoAddPolicy
from network.sonic_service.sonic_service import Sonic_service
from network.ocnos_service.ocnos_service import OcnosService
from network.parser.parser import Parser
from ncclient import manager
from ncclient.operations import RPCError




class Network:
    def __init__(self, emulation_mode = False):
        self.topology = {}
        self.sshClient = SSHClient()
        self.loadSSH()
        self.emulation_mode = emulation_mode
        self.soic_service = Sonic_service(self.sshClient)
        self.ocnos_service = OcnosService(self.sshClient)
        self.sonic_data = {}
        self.ocnos_data = {}
        self.parser = Parser()
        if self.emulation_mode:
            self.vm = SSHClient()
    
    def fill_xml_template(self,template_file, configuration):
        # Read the XML template from the file
        with open(template_file, "r") as f:
            xml_template = f.read()
        xml_template = re.sub("{operation}", configuration["operation"], xml_template)
        for param, value in configuration["content"].items():
            xml_template = re.sub(f"{{{param}}}", str(value), xml_template)
        return xml_template

    def fill_xml_config(self,config):
        # Read the XML template from the file
        with open("configuration_ms/network/ocnos_service/xml_templates/config.xml", "r") as f:
            xml_template = f.read()
        xml_template = re.sub("{configuration}", config, xml_template)
        return xml_template

    def get_topology(self,config):
        #get type of devices
        for node in config.network_targets.get_nodes():
            self.topology[node.get_name().replace('"','')] = node.obj_dict["attributes"]

    def loadSSH(self):
    # load host ssh keys
        self.sshClient.load_host_keys(os.path.expanduser('~/.ssh/known_hosts'))
        # known_hosts policy
        self.sshClient.set_missing_host_key_policy(AutoAddPolicy())

    def config_network(self, network_config, cfg, backup = False):
        logging.info("will conf network")
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
                if self.topology[device]['os'].replace('"','') == 'sonic':
                    try:
                        self.sshClient.connect(
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
                        self.sshClient.close()
                        if not backup:
                            self.config_network(network_config,cfg,backup=True)
                        break;
                    if backup: # backup mode
                        Sonic_service.backup_device()
                    else:#regular mode
                        logging.info("will enter regular mode {}".format(self.topology[device]))
                        if(self.soic_service.config_device(device = device, config = network_config[device]) != 0):
                            logging.warning("Configuring device {} Failed, starting backup mode for all devices...")
                            self.sshClient.close()
                            self.config_network(network_config,cfg,backup=True)
                            break;

                elif self.topology[device]['os'].replace('"','') == 'ocnos':
                    try:
                        # Connect to the netconf server
                        netconfClient = manager.connect(
                            host=self.topology[device]['mgmt_ip'].replace('"',''),
                            port=830,
                            username=self.topology[device]['username'].replace('"',''),
                            password=self.topology[device]['password'].replace('"',''),
                            hostkey_verify=False,)
                        configuration_list=network_config[device]
                        xml_obj = ""
                        for configuration in configuration_list:
                            template_file = "configuration_ms/network/ocnos_service/xml_templates/"+configuration["resource"]+"/"+configuration["resource"]+".xml"
                            xml_obj += self.fill_xml_template(template_file, configuration)
                        xml_configuration=self.fill_xml_config(xml_obj)
                        try:
                            reply = netconfClient.edit_config(target="candidate", config=xml_configuration)
                            print(reply)
                        except Exception as e:
                            print(traceback.format_exc())
                            print(e)
                            logging.error(f"Error editing configuration: {e}")

                        # Commit the changes and save them to the running configuration
                        try:
                            #m.discard_changes()
                            netconfClient.commit()
                            
                        except RPCError as e:
                            logging.error(f"Error committing and saving changes: {e}")
                            netconfClient.discard_changes()
                            sys.exit(1)
                    except Exception as e:
                        logging.error(f"Error connecting to device: {e}")
                        sys.exit(1)
                        
                else:
                    pass