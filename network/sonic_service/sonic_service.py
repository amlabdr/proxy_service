from network.query.query import Query
class Sonic_service:
    def __init__(self, client):
        self.commandList = ['show runningconfiguration all | grep -A 11 -i metadata', 'show arp', 'show ip route', 'show acl table', 'show acl rule', 'show lldp table', 'show vlan config',
               'vtysh -c "show interface"', 'show ip bgp neighbors']
        self.headerList = ['metadata', 'arp', 'ipRoute', 'aclTable', 'aclRule', 'lldp', 'vlan', 'interface', 'bgp']

        # list of commands that will be run for each node on network
        self.command_dict = {
                'metadata': 'show runningconfiguration all | grep -A 11 -i metadata',
                'arp': 'show arp',
                'ipRoute': 'show ip route',
                'aclTable': 'show acl table',
                'aclRule': 'show acl rule',
                'lldp': 'show lldp table',
                'vlan': 'show vlan config',
                'interface': 'vtysh -c "show interface"',
                'bgp': 'show ip bgp neighbors'
        }
        self.client = client

    def collectData(self,device):
        #initialize device dict
        query_dictionary={}
        query_dictionary[device] = {}
        for key in self.command_dict:
            current_query = Query(device, self.command_dict[key], key)
            current_query.send_query(self.client)
            query_dictionary[current_query.device][current_query.template] = current_query
        return query_dictionary

        
    
    